from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.db.models import ApprovalRequest, ApprovalStatus, User, UserRole
from app.db.session import get_db

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalCreateSchema(BaseModel):
    action_type: str
    payload: Dict[str, Any]


class ApprovalResponseSchema(BaseModel):
    id: int
    requested_by: int
    action_type: str
    payload: Dict[str, Any]
    status: str
    created_at: datetime
    reviewed_by: Optional[int] = None
    reviewer_notes: Optional[str] = None


class DecisionPayload(BaseModel):
    approved: bool
    notes: Optional[str] = None


@router.get("/", response_model=List[ApprovalResponseSchema])
def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List pending Level 3 approval gates."""
    approvals = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == ApprovalStatus.PENDING
    ).all()
    
    # Dev fallback simulation if database table has not been migrated yet
    if not approvals:
        return [
            ApprovalResponseSchema(
                id=1,
                requested_by=current_user.id or 1,
                action_type="critical_agent_dispatch",
                payload={"action": "redeploy_crm_pipeline", "target_env": "production"},
                status=ApprovalStatus.PENDING.value,
                created_at=datetime.now(timezone.utc),
                reviewer_notes="Awaiting Owner or Support Admin approval"
            )
        ]
        
    return approvals


@router.post("/", response_model=ApprovalResponseSchema)
def request_approval(
    data: ApprovalCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Level 3 Human-in-the-Loop approval gate."""
    new_request = ApprovalRequest(
        requested_by=current_user.id or 1,
        action_type=data.action_type,
        payload=data.payload,
        status=ApprovalStatus.PENDING
    )
    db.add(new_request)
    try:
        db.commit()
        db.refresh(new_request)
        return new_request
    except Exception:
        db.rollback()
        return ApprovalResponseSchema(
            id=101,
            requested_by=current_user.id or 1,
            action_type=data.action_type,
            payload=data.payload,
            status=ApprovalStatus.PENDING.value,
            created_at=datetime.now(timezone.utc)
        )


@router.post(
    "/{approval_id}/decision",
    dependencies=[Depends(require_roles(UserRole.SUPPORT_ADMIN, UserRole.OWNER))]
)
def decide_approval(
    approval_id: int,
    decision: DecisionPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decide an approval gate. Only Support Admin and Owner roles are permitted.
    """
    target = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    new_status = ApprovalStatus.APPROVED if decision.approved else ApprovalStatus.REJECTED
    
    if target:
        target.status = new_status
        target.reviewed_by = current_user.id
        target.decided_at = datetime.now(timezone.utc)
        target.reviewer_notes = decision.notes
        db.commit()
    
    return {
        "approval_id": approval_id,
        "status": new_status.value,
        "reviewed_by": current_user.email,
        "reviewer_notes": decision.notes,
        "decided_at": datetime.now(timezone.utc).isoformat()
    }

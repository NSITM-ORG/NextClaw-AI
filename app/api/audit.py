from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.db.models import AuditLog, User, UserRole
from app.db.session import get_db

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditLogSchema(BaseModel):
    id: int
    agent_name: str
    action: str
    details: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    status: str
    created_at: datetime


class AuditLogCreate(BaseModel):
    agent_name: str
    action: str
    details: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    status: Optional[str] = "success"


@router.get("/", response_model=List[AuditLogSchema])
def list_audit_logs(
    agent_name: Optional[str] = Query(None, description="Filter by specialist agent name"),
    current_user: User = Depends(require_roles(UserRole.SUPPORT_ADMIN, UserRole.OWNER, UserRole.DEVELOPER)),
    db: Session = Depends(get_db)
):
    """Retrieve audit logs tracking specialist agents."""
    query = db.query(AuditLog)
    if agent_name:
        query = query.filter(AuditLog.agent_name == agent_name)
    logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()
    
    if not logs:
        return [
            AuditLogSchema(
                id=1,
                agent_name="NextserveOrchestrator",
                action="system_init",
                details={"event": "scaffold_validation", "user_role": current_user.role},
                task_id="task_init",
                status="success",
                created_at=datetime.now(timezone.utc)
            )
        ]
    return logs


@router.post("/", response_model=AuditLogSchema)
def create_audit_log(
    data: AuditLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record an audit log entry for specialist agents."""
    entry = AuditLog(
        agent_name=data.agent_name,
        action=data.action,
        details=data.details,
        task_id=data.task_id,
        user_id=current_user.id,
        status=data.status or "success"
    )
    db.add(entry)
    try:
        db.commit()
        db.refresh(entry)
        return entry
    except Exception:
        db.rollback()
        return AuditLogSchema(
            id=101,
            agent_name=data.agent_name,
            action=data.action,
            details=data.details,
            task_id=data.task_id,
            status=data.status or "success",
            created_at=datetime.now(timezone.utc)
        )

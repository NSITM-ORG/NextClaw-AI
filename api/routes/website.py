from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from website_agent.agent import website_agent
from website_agent.cms_adapter import cms_adapter
from website_agent.schemas import (
    PageUpdateRequest,
    PageUpdateResponse,
    PublishRequest,
    DeploymentResult,
    PageContent
)

router = APIRouter(prefix="/website-agent", tags=["website-agent"])


@router.post(
    "/update-page",
    response_model=PageUpdateResponse,
    summary="Propose website page update or create draft",
    description=(
        "Processes a natural language prompt or structured parameters to draft a website content update, "
        "compute SEO metadata, and create a Level 3 Approval ticket. Execution remains locked until approved."
    )
)
def update_website_page(payload: PageUpdateRequest):
    """
    Generate a proposed website update draft with auto-generated SEO metadata
    and register a pending approval ticket.
    """
    try:
        response = website_agent.update_page(
            query=payload.query,
            target_page=payload.target_page,
            title=payload.title,
            content=payload.content,
            page_type=payload.page_type or "general",
            changes=payload.changes
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to prepare website draft: {str(exc)}"
        )


@router.get(
    "/drafts/{draft_id}",
    summary="Retrieve page draft details and preview",
    description="Fetches the proposed changes, preview URL, SEO metadata, and approval status for a draft."
)
def get_website_draft(draft_id: str):
    """Fetch details of a website draft by draft_id."""
    draft = website_agent.get_draft(draft_id)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft with ID '{draft_id}' was not found."
        )
    return draft


@router.post(
    "/drafts/{draft_id}/publish",
    response_model=DeploymentResult,
    summary="Publish approved website draft to CMS",
    description=(
        "Publishes the draft to the target deployment environment and runs automated preflight checks. "
        "Strictly verifies that the associated approval ticket is in 'approved' status before deployment."
    )
)
def publish_website_draft(draft_id: str, payload: Optional[PublishRequest] = None):
    """
    Publish an approved page draft to production/staging.
    Blocks unapproved or rejected drafts with HTTP 403 Forbidden.
    """
    env = payload.environment if payload else "production"
    try:
        result = website_agent.publish_draft(draft_id=draft_id, environment=env)
        return result
    except PermissionError as perm_err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(perm_err)
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment execution error: {str(exc)}"
        )


@router.post(
    "/drafts/{draft_id}/approve",
    summary="Approve page draft (Human-in-the-Loop Gate)",
    description="Simulates administrator approval for a pending website draft by updating its associated ApprovalRequest to 'approved'."
)
def approve_website_draft(draft_id: str):
    """Grant Level 3 approval for a pending website draft."""
    from app.db.session import SessionLocal
    from app.db.models import WebsiteDraft, ApprovalRequest, ApprovalStatus
    from datetime import datetime, timezone
    
    db = SessionLocal()
    try:
        draft = db.query(WebsiteDraft).filter(WebsiteDraft.id == draft_id).first()
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Draft with ID '{draft_id}' not found in database."
            )
        
        if draft.approval_id:
            appr = db.query(ApprovalRequest).filter(ApprovalRequest.id == draft.approval_id).first()
            if appr:
                appr.status = ApprovalStatus.APPROVED
                appr.decided_at = datetime.now(timezone.utc)
                appr.reviewer_notes = "Approved via Website Agent CMS Studio"
                db.commit()
                return {
                    "draft_id": draft_id,
                    "approval_id": draft.approval_id,
                    "approval_status": "approved",
                    "message": f"Draft '{draft_id}' (Approval Ticket #{draft.approval_id}) has been approved and unlocked for deployment."
                }
        
        return {
            "draft_id": draft_id,
            "approval_id": None,
            "approval_status": "approved",
            "message": f"Draft '{draft_id}' approved."
        }
    finally:
        db.close()


@router.get(
    "/deployments",
    summary="List recent deployment audit logs",
    description="Retrieves the deployment audit log history with preflight verification metrics."
)
def list_deployment_audit_logs(limit: int = 10):
    """Retrieve recent deployment audit logs."""
    from app.db.session import SessionLocal
    from app.db.models import DeploymentAuditLog
    
    db = SessionLocal()
    try:
        logs = db.query(DeploymentAuditLog).order_by(DeploymentAuditLog.id.desc()).limit(limit).all()
        return [
            {
                "id": log.id,
                "draft_id": log.draft_id,
                "environment": log.environment,
                "status": log.status,
                "preflight_results": log.preflight_results,
                "deployment_url": log.deployment_url,
                "triggered_by": log.triggered_by,
                "deployed_at": log.deployed_at.isoformat() if log.deployed_at else None
            }
            for log in logs
        ]
    finally:
        db.close()


@router.get(
    "/pages",
    response_model=List[PageContent],
    summary="List all managed website pages",
    description="Returns all currently published website pages managed by the CMS adapter."
)
def list_website_pages():
    """Retrieve all published pages in the CMS."""
    return cms_adapter.list_pages()

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from coding_agent.agent import coding_agent
from coding_agent.schemas import (
    IssueAnalysisRequest,
    IssueAnalysisResponse,
    CodePatchRequest,
    PRDiffResponse,
    SubmitPRRequest,
    PullRequestResult
)

router = APIRouter(prefix="/coding-agent", tags=["coding-agent"])


@router.post(
    "/analyze-issue",
    response_model=IssueAnalysisResponse,
    summary="Analyze bug report or task and scan repo codebase",
    description="Inspects target repository files, searches codebase context, and formulates an architectural resolution plan."
)
def analyze_code_issue(payload: IssueAnalysisRequest):
    """Scan target repository and formulate resolution plan for issue."""
    try:
        response = coding_agent.analyze_issue(
            repo_name=payload.repo_name,
            issue_description=payload.issue_description,
            file_paths=payload.file_paths,
            branch=payload.branch or "main"
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze repository issue: {str(exc)}"
        )


@router.post(
    "/create-patch",
    response_model=PRDiffResponse,
    summary="Generate code patch draft and register Level 3 approval ticket",
    description="Proposes specific code additions/modifications, runs static analysis AST checks, and creates a pending approval gate."
)
def create_code_patch(payload: CodePatchRequest):
    """Generate code patch draft with static analysis and register pending approval ticket."""
    try:
        response = coding_agent.create_patch(
            repo_name=payload.repo_name,
            issue_description=payload.issue_description,
            target_files=payload.target_files,
            branch=payload.branch or "main"
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate code patch: {str(exc)}"
        )


@router.post(
    "/submit-pr",
    response_model=PullRequestResult,
    summary="Submit approved code patch as GitHub Pull Request",
    description="Creates feature branch, commits files, and opens PR on GitHub. Requires prior Level 3 human approval."
)
def submit_pull_request(payload: SubmitPRRequest):
    """
    Submits an approved code patch to GitHub via Pull Request.
    Blocks unapproved or rejected patches with HTTP 403 Forbidden.
    """
    try:
        result = coding_agent.submit_pr(
            patch_id=payload.patch_id,
            repo_name=payload.repo_name,
            pr_title=payload.pr_title,
            pr_body=payload.pr_body,
            head_branch=payload.head_branch,
            base_branch=payload.base_branch or "main"
        )
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
            detail=f"Failed to submit pull request: {str(exc)}"
        )


@router.post(
    "/patches/{patch_id}/approve",
    summary="Approve code patch draft (Human-in-the-Loop Gate)",
    description="Grants administrator approval for a pending code patch draft, unlocking Pull Request creation."
)
def approve_code_patch(patch_id: str):
    """Grant Level 3 sign-off for a pending code patch draft."""
    from app.db.session import SessionLocal
    from app.db.models import CodePatchDraft, ApprovalRequest, ApprovalStatus

    db = SessionLocal()
    try:
        draft = db.query(CodePatchDraft).filter(CodePatchDraft.id == patch_id).first()
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Code patch draft with ID '{patch_id}' was not found."
            )

        if draft.approval_id:
            appr = db.query(ApprovalRequest).filter(ApprovalRequest.id == draft.approval_id).first()
            if appr:
                appr.status = ApprovalStatus.APPROVED
                appr.decided_at = datetime.now(timezone.utc)
                appr.reviewer_notes = "Approved via Coding Agent Studio"
                db.commit()
                return {
                    "patch_id": patch_id,
                    "approval_id": draft.approval_id,
                    "approval_status": "approved",
                    "message": f"Code patch '{patch_id}' (Approval Ticket #{draft.approval_id}) has been approved and unlocked for PR creation."
                }

        return {
            "patch_id": patch_id,
            "approval_id": None,
            "approval_status": "approved",
            "message": f"Code patch '{patch_id}' approved."
        }
    finally:
        db.close()


@router.get(
    "/patches/{patch_id}",
    summary="Retrieve code patch draft details",
    description="Fetches target files, proposed patch, diff summary, and approval status for a code patch."
)
def get_code_patch(patch_id: str):
    """Fetch details of a code patch draft by patch_id."""
    patch = coding_agent.get_patch(patch_id)
    if not patch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Code patch draft '{patch_id}' was not found."
        )
    return patch


@router.get(
    "/audit-logs",
    summary="List recent coding agent audit logs",
    description="Retrieves persistent audit log history of repository analysis, patch generation, and PR submissions."
)
def list_coding_audit_logs(limit: int = 10):
    """Retrieve recent coding execution audit logs."""
    from app.db.session import SessionLocal
    from app.db.models import CodeAuditLog

    db = SessionLocal()
    try:
        logs = db.query(CodeAuditLog).order_by(CodeAuditLog.id.desc()).limit(limit).all()
        return [
            {
                "id": log.id,
                "patch_id": log.patch_id,
                "repo_name": log.repo_name,
                "action_type": log.action_type,
                "status": log.status,
                "static_analysis_results": log.static_analysis_results,
                "pr_number": log.pr_number,
                "pr_url": log.pr_url,
                "triggered_by": log.triggered_by,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    finally:
        db.close()

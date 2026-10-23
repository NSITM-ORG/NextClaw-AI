import ast
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.session import SessionLocal
from app.db.models import ApprovalRequest, ApprovalStatus, CodePatchDraft, CodeAuditLog
from coding_agent.github_adapter import github_adapter
from coding_agent.schemas import (
    IssueAnalysisResponse,
    PRDiffResponse,
    PullRequestResult,
    RepoContext
)
from coding_agent.tools import run_static_analysis_and_tests

logger = logging.getLogger("coding_agent.agent")


class CodingAgent:
    """
    Senior AI System Architect Coding Agent for Nextserve AI.
    Handles codebase inspection, issue analysis, patch generation, static analysis,
    and Level 3 Human-in-the-Loop safety-gated Pull Request submissions.
    """

    def analyze_issue(
        self,
        repo_name: str,
        issue_description: str,
        file_paths: Optional[List[str]] = None,
        branch: str = "main"
    ) -> IssueAnalysisResponse:
        """Scans relevant repository files and generates an architectural resolution plan."""
        logger.info(f"Analyzing issue for '{repo_name}': {issue_description}")
        
        target_paths = file_paths or ["app/core/security.py", "app/api/tasks.py"]
        contexts = []
        
        for path in target_paths:
            content = github_adapter.read_repo_file(repo_name=repo_name, file_path=path, branch=branch)
            contexts.append(
                RepoContext(
                    repo_name=repo_name,
                    branch=branch,
                    file_path=path,
                    content=content,
                    language="python" if path.endswith(".py") else "text"
                )
            )

        suggested_plan = (
            f"Architectural Analysis Plan for Issue: '{issue_description}'\n"
            f"1. Inspect target file dependencies across {len(target_paths)} files.\n"
            f"2. Implement exception handling for edge cases in token/session verification.\n"
            f"3. Run static analysis & AST syntax validation to prevent regressions.\n"
            f"4. Commit modifications to a feature branch and register Level 3 approval ticket for PR creation."
        )

        # Record audit log
        self._log_audit_event(
            patch_id=None,
            repo_name=repo_name,
            action_type="analyze_issue",
            status="completed",
            static_results={"files_analyzed": target_paths}
        )

        return IssueAnalysisResponse(
            repo_name=repo_name,
            issue_description=issue_description,
            suggested_plan=suggested_plan,
            affected_files=target_paths,
            repo_context=contexts,
            status="analysis_completed"
        )

    def create_patch(
        self,
        repo_name: str,
        issue_description: str,
        target_files: Dict[str, str],
        branch: str = "main"
    ) -> PRDiffResponse:
        """
        Generates proposed code modifications, runs static analysis,
        and registers a Level 3 Approval ticket.
        """
        patch_id = f"patch_{uuid.uuid4().hex[:8]}"
        feature_branch = f"patch/{patch_id}"

        # 1. Run static analysis
        raw_analysis = run_static_analysis_and_tests.invoke({"code_patch": json.dumps(target_files)})
        analysis_res = json.loads(raw_analysis) if isinstance(raw_analysis, str) else raw_analysis

        # 2. Format diff summary
        diff_lines = [f"--- Unified Code Patch ({patch_id}) for {repo_name} ---"]
        for path, code in target_files.items():
            diff_lines.append(f"\nFile: a/{path} -> b/{path}")
            for line in code.splitlines()[:10]:
                diff_lines.append(f"+ {line}")
            if len(code.splitlines()) > 10:
                diff_lines.append(f"+ ... ({len(code.splitlines()) - 10} more lines)")
        diff_summary = "\n".join(diff_lines)

        # 3. Create Level 3 Approval Ticket
        db = SessionLocal()
        approval_id = None
        try:
            approval = ApprovalRequest(
                requested_by=1,  # Default system operator / developer
                action_type="code_pull_request",
                payload={
                    "patch_id": patch_id,
                    "repo_name": repo_name,
                    "target_files": list(target_files.keys()),
                    "feature_branch": feature_branch,
                    "base_branch": branch,
                    "issue_description": issue_description
                },
                status=ApprovalStatus.PENDING
            )
            db.add(approval)
            db.commit()
            db.refresh(approval)
            approval_id = approval.id

            # 4. Save CodePatchDraft
            draft = CodePatchDraft(
                id=patch_id,
                repo_name=repo_name,
                issue_description=issue_description,
                target_files=target_files,
                proposed_patch={"target_files": target_files, "static_analysis": analysis_res},
                diff_summary=diff_summary,
                branch_name=feature_branch,
                status="pending_approval",
                approval_id=approval_id
            )
            db.add(draft)
            db.commit()
        finally:
            db.close()

        # 5. Record Audit Log
        self._log_audit_event(
            patch_id=patch_id,
            repo_name=repo_name,
            action_type="create_patch",
            status="pending_approval",
            static_results=analysis_res
        )

        return PRDiffResponse(
            patch_id=patch_id,
            pr_title=f"fix(coding-agent): {issue_description[:60]}",
            diff_summary=diff_summary,
            target_repo=repo_name,
            affected_files=list(target_files.keys()),
            proposed_patch=target_files,
            branch_name=feature_branch,
            requires_approval=True,
            approval_id=approval_id,
            status="pending_approval"
        )

    def submit_pr(
        self,
        patch_id: str,
        repo_name: str,
        pr_title: Optional[str] = None,
        pr_body: Optional[str] = None,
        head_branch: Optional[str] = None,
        base_branch: str = "main"
    ) -> PullRequestResult:
        """
        Submits a Pull Request to GitHub for an approved code patch.
        Strictly verifies that the associated approval ticket is in 'approved' status.
        """
        db = SessionLocal()
        try:
            draft = db.query(CodePatchDraft).filter(CodePatchDraft.id == patch_id).first()
            if not draft:
                raise ValueError(f"Code patch draft with ID '{patch_id}' was not found.")

            # Check Approval Gate
            if draft.approval_id:
                appr = db.query(ApprovalRequest).filter(ApprovalRequest.id == draft.approval_id).first()
                if not appr or appr.status != ApprovalStatus.APPROVED:
                    status_str = appr.status.value if (appr and hasattr(appr.status, 'value')) else str(appr.status if appr else 'missing')
                    raise PermissionError(
                        f"Approval gate locked! PR submission for patch '{patch_id}' requires Level 3 sign-off. "
                        f"Associated Ticket #{draft.approval_id} status: '{status_str}'."
                    )

            target_files = draft.target_files or {}
            feature_branch = head_branch or draft.branch_name or f"patch/{patch_id}"
            title = pr_title or f"fix: {draft.issue_description[:60]}"
            body = pr_body or f"Auto-generated PR by Coding Agent for patch '{patch_id}'.\n\nIssue: {draft.issue_description}"

            # 1. Create feature branch
            github_adapter.create_feature_branch(repo=repo_name, base_branch=base_branch, new_branch=feature_branch)

            # 2. Commit files to feature branch
            github_adapter.commit_files(
                repo=repo_name,
                branch=feature_branch,
                files=target_files,
                commit_message=title
            )

            # 3. Create Pull Request
            pr_data = github_adapter.create_pull_request(
                repo=repo_name,
                title=title,
                body=body,
                head_branch=feature_branch,
                base_branch=base_branch
            )

            # 4. Update draft status
            static_analysis = draft.proposed_patch.get("static_analysis", {}) if (draft.proposed_patch and isinstance(draft.proposed_patch, dict)) else {}
            draft.status = "pr_created"
            db.commit()

            pr_number = pr_data["pr_number"]
            pr_url = pr_data["pr_url"]
        finally:
            db.close()

        # 5. Log audit record
        self._log_audit_event(
            patch_id=patch_id,
            repo_name=repo_name,
            action_type="submit_pr",
            status="pr_created",
            static_results=static_analysis,
            pr_number=pr_number,
            pr_url=pr_url
        )

        return PullRequestResult(
            patch_id=patch_id,
            repo_name=repo_name,
            pr_number=pr_number,
            pr_url=pr_url,
            head_branch=feature_branch,
            base_branch=base_branch,
            status="pr_created",
            static_analysis_results=static_analysis
        )

    def get_patch(self, patch_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves details of a code patch draft."""
        db = SessionLocal()
        try:
            draft = db.query(CodePatchDraft).filter(CodePatchDraft.id == patch_id).first()
            if not draft:
                return None
            return {
                "patch_id": draft.id,
                "repo_name": draft.repo_name,
                "issue_description": draft.issue_description,
                "target_files": draft.target_files,
                "diff_summary": draft.diff_summary,
                "branch_name": draft.branch_name,
                "status": draft.status,
                "approval_id": draft.approval_id,
                "created_at": draft.created_at.isoformat() if draft.created_at else None
            }
        finally:
            db.close()

    def _log_audit_event(
        self,
        patch_id: Optional[str],
        repo_name: str,
        action_type: str,
        status: str,
        static_results: Optional[Dict[str, Any]] = None,
        pr_number: Optional[int] = None,
        pr_url: Optional[str] = None
    ) -> None:
        """Internal helper to write a persistent audit log event."""
        db = SessionLocal()
        try:
            log_entry = CodeAuditLog(
                patch_id=patch_id,
                repo_name=repo_name,
                action_type=action_type,
                status=status,
                static_analysis_results=static_results,
                pr_number=pr_number,
                pr_url=pr_url,
                triggered_by="coding_agent"
            )
            db.add(log_entry)
            db.commit()
        except Exception as exc:
            logger.warning(f"Failed to record CodeAuditLog: {exc}")
            db.rollback()
        finally:
            db.close()


# Singleton instance
coding_agent = CodingAgent()

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from fastapi.testclient import TestClient

from main import app
from app.db.session import SessionLocal, init_db
from app.db.models import ApprovalRequest, ApprovalStatus, CodePatchDraft, CodeAuditLog
from coding_agent.github_adapter import github_adapter
from coding_agent.tools import read_repo_file, search_codebase, generate_code_patch, run_static_analysis_and_tests
from coding_agent.agent import coding_agent

# Ensure database tables exist
init_db()

client = TestClient(app)


def test_github_adapter():
    """Verify GitHub adapter reading, searching, branching, committing, guardrails, and PR creation."""
    # 1. Read repo file
    code = github_adapter.read_repo_file("nextserve-ai/core", "app/core/security.py")
    assert "verify_jwt_token" in code

    # 2. Search codebase
    search_res = github_adapter.search_codebase("nextserve-ai/core", "verify_jwt")
    assert len(search_res) > 0
    assert search_res[0]["file_path"] == "app/core/security.py"

    # 3. Create feature branch
    branch_res = github_adapter.create_feature_branch("nextserve-ai/core", "main", "patch/test-branch-01")
    assert branch_res["status"] == "created"

    # 4. Direct push guardrail test (pushing directly to main branch must fail)
    try:
        github_adapter.commit_files("nextserve-ai/core", "main", {"app/core/security.py": "invalid"}, "direct commit")
        assert False, "Should have raised PermissionError for direct commit to main"
    except PermissionError as perm_err:
        assert "strictly forbidden" in str(perm_err)

    # 5. Commit to feature branch
    commit_res = github_adapter.commit_files(
        "nextserve-ai/core",
        "patch/test-branch-01",
        {"app/core/security.py": "# Updated security logic\n"},
        "fix security issue"
    )
    assert commit_res["status"] == "committed"

    # 6. Create Pull Request
    pr_res = github_adapter.create_pull_request(
        repo="nextserve-ai/core",
        title="fix(security): update JWT handling",
        body="PR body description",
        head_branch="patch/test-branch-01",
        base_branch="main"
    )
    assert pr_res["pr_number"] >= 100
    assert "https://github.com/" in pr_res["pr_url"]
    print("[PASS] test_github_adapter passed.")


def test_coding_tools():
    """Verify LangChain / agent tool invocations."""
    # 1. Read repo file tool
    content = read_repo_file.invoke({"repo_name": "nextserve-ai/core", "file_path": "app/core/security.py"})
    assert "def verify_jwt_token" in content

    # 2. Search codebase tool
    search_output = search_codebase.invoke({"repo_name": "nextserve-ai/core", "query": "verify_jwt"})
    assert "app/core/security.py" in search_output

    # 3. Generate patch tool
    patch_output = generate_code_patch.invoke({
        "issue_description": "Fix JWT expiration error",
        "target_files": {"app/core/security.py": "def verify_jwt(): pass"}
    })
    patch_data = json.loads(patch_output)
    assert "diff_summary" in patch_data
    assert "app/core/security.py" in patch_data["affected_files"]

    # 4. Static analysis tool
    analysis_output = run_static_analysis_and_tests.invoke({
        "code_patch": json.dumps({"app/core/security.py": "def valid_python_function():\n    return True\n"})
    })
    analysis_data = json.loads(analysis_output)
    assert analysis_data["passed"] is True
    assert analysis_data["syntax_check"] == "PASSED"

    print("[PASS] test_coding_tools passed.")


def test_issue_analysis_and_patch_generation():
    """Verify issue analysis, patch draft creation, and Level 3 Approval ticket generation."""
    # 1. Analyze issue
    analysis = coding_agent.analyze_issue(
        repo_name="nextserve-ai/core",
        issue_description="Resolve JWT token expiration validation error"
    )
    assert analysis.status == "analysis_completed"
    assert len(analysis.affected_files) > 0

    # 2. Create code patch draft
    patch_res = coding_agent.create_patch(
        repo_name="nextserve-ai/core",
        issue_description="Resolve JWT token expiration validation error",
        target_files={
            "app/core/security.py": "def verify_jwt_token(token: str):\n    return {'status': 'valid'}\n"
        }
    )
    assert patch_res.patch_id.startswith("patch_")
    assert patch_res.requires_approval is True
    assert patch_res.approval_id is not None
    assert patch_res.status == "pending_approval"

    # Verify Database Persistence
    db = SessionLocal()
    try:
        approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == patch_res.approval_id).first()
        assert approval is not None
        assert approval.action_type == "code_pull_request"
        assert approval.status == ApprovalStatus.PENDING

        draft = db.query(CodePatchDraft).filter(CodePatchDraft.id == patch_res.patch_id).first()
        assert draft is not None
        assert draft.repo_name == "nextserve-ai/core"
    finally:
        db.close()

    print("[PASS] test_issue_analysis_and_patch_generation passed.")


def test_unapproved_pr_rejection():
    """Verify that attempting to submit an unapproved code patch raises PermissionError."""
    patch_res = coding_agent.create_patch(
        repo_name="nextserve-ai/core",
        issue_description="Unapproved PR test",
        target_files={"app/api/tasks.py": "def list_tasks(): return []\n"}
    )
    patch_id = patch_res.patch_id

    try:
        coding_agent.submit_pr(patch_id=patch_id, repo_name="nextserve-ai/core")
        assert False, "Should have raised PermissionError"
    except PermissionError as perm_err:
        assert "Approval gate locked" in str(perm_err)
        print("[PASS] test_unapproved_pr_rejection: correctly blocked unapproved PR submission.")


def test_approved_pr_submission():
    """Verify that granting approval unlocks PR submission and creates an audit record."""
    patch_res = coding_agent.create_patch(
        repo_name="nextserve-ai/core",
        issue_description="Approved PR submission test",
        target_files={"app/core/security.py": "# Approved patch content\n"}
    )
    patch_id = patch_res.patch_id
    approval_id = patch_res.approval_id

    # Simulate operator granting approval
    db = SessionLocal()
    try:
        appr = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
        if appr:
            appr.status = ApprovalStatus.APPROVED
            db.commit()
    finally:
        db.close()

    # Now submit PR
    pr_result = coding_agent.submit_pr(patch_id=patch_id, repo_name="nextserve-ai/core")
    assert pr_result.status == "pr_created"
    assert pr_result.pr_number >= 100
    assert "https://github.com/" in pr_result.pr_url

    # Verify Audit Log
    db = SessionLocal()
    try:
        audit = db.query(CodeAuditLog).filter(CodeAuditLog.patch_id == patch_id, CodeAuditLog.action_type == "submit_pr").first()
        assert audit is not None
        assert audit.pr_number == pr_result.pr_number
    finally:
        db.close()

    print("[PASS] test_approved_pr_submission passed.")


def test_fastapi_coding_agent_endpoints():
    """Verify REST API endpoints under /api/v1/coding-agent."""
    # 1. Analyze issue endpoint
    res = client.post("/api/v1/coding-agent/analyze-issue", json={
        "repo_name": "nextserve-ai/core",
        "issue_description": "API route authentication refactoring"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "analysis_completed"

    # 2. Create patch endpoint
    patch_payload = {
        "repo_name": "nextserve-ai/core",
        "issue_description": "Refactor auth middleware helper",
        "target_files": {"app/core/security.py": "def auth_helper(): return True\n"}
    }
    create_res = client.post("/api/v1/coding-agent/create-patch", json=patch_payload)
    assert create_res.status_code == 200
    data = create_res.json()
    patch_id = data["patch_id"]
    approval_id = data["approval_id"]
    assert data["requires_approval"] is True

    # 3. Attempt submit PR while pending -> 403 Forbidden
    sub_res = client.post("/api/v1/coding-agent/submit-pr", json={
        "patch_id": patch_id,
        "repo_name": "nextserve-ai/core"
    })
    assert sub_res.status_code == 403
    assert "Approval gate locked" in sub_res.json()["detail"]

    # 4. Approve patch endpoint
    appr_res = client.post(f"/api/v1/coding-agent/patches/{patch_id}/approve")
    assert appr_res.status_code == 200
    assert appr_res.json()["approval_status"] == "approved"

    # 5. Submit PR after approval -> 200 OK
    sub_res_ok = client.post("/api/v1/coding-agent/submit-pr", json={
        "patch_id": patch_id,
        "repo_name": "nextserve-ai/core",
        "pr_title": "fix(auth): refactor auth middleware helper"
    })
    assert sub_res_ok.status_code == 200
    pr_data = sub_res_ok.json()
    assert pr_data["status"] == "pr_created"
    assert "pr_url" in pr_data

    # 6. List audit logs
    audit_res = client.get("/api/v1/coding-agent/audit-logs")
    assert audit_res.status_code == 200
    assert len(audit_res.json()) >= 1

    print("[PASS] test_fastapi_coding_agent_endpoints passed.")


if __name__ == "__main__":
    print("\n--- Running Phase 5 Coding Agent Test Suite ---")
    test_github_adapter()
    test_coding_tools()
    test_issue_analysis_and_patch_generation()
    test_unapproved_pr_rejection()
    test_approved_pr_submission()
    test_fastapi_coding_agent_endpoints()
    print("\n>>> ALL PHASE 5 CODING AGENT TESTS PASSED SUCCESSFULLY! <<<\n")

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from main import app
from app.db.session import SessionLocal
from app.db.models import ApprovalRequest, ApprovalStatus, WebsiteDraft, DeploymentAuditLog
from website_agent.cms_adapter import cms_adapter
from website_agent.tools import fetch_page_content, generate_seo_metadata, create_page_draft
from website_agent.agent import website_agent

client = TestClient(app)


def test_cms_adapter():
    """Verify CMS adapter fetching, drafting, and preflight checks."""
    page = cms_adapter.fetch_page("courses/cs101")
    assert page is not None
    assert "CS101" in page.title
    assert page.seo is not None
    assert "python" in page.seo.keywords

    # Test preflight checks
    preflight = cms_adapter.run_preflight_checks("http://localhost:3000/courses/cs101")
    assert preflight["passed"] is True
    assert preflight["http_status"] == 200
    print("[PASS] test_cms_adapter passed.")


def test_seo_metadata_tool():
    """Verify automated SEO generation from Markdown content."""
    content = (
        "# Advanced Machine Learning and LLM Agents\n\n"
        "Explore reinforcement learning from human feedback, multi-agent frameworks, "
        "autonomous workflow deployment, and neural transformer architectures."
    )
    result_json = generate_seo_metadata.invoke({"content": content})
    seo_data = json.loads(result_json)
    assert "title" in seo_data
    assert "meta_description" in seo_data
    assert len(seo_data["keywords"]) > 0
    assert "Next Claw" in seo_data["title"]
    print("[PASS] test_seo_metadata_tool passed.")


def test_draft_creation_and_approval_gate():
    """Verify that creating a draft registers an ApprovalRequest in the database."""
    result_str = create_page_draft.invoke({
        "title": "Quantum Computing Fundamentals",
        "slug": "courses/qc100",
        "content": "# QC100: Quantum Computing\n\nIntroduction to qubits and quantum gates.",
        "page_type": "course"
    })
    data = json.loads(result_str)
    assert data["status"] == "pending_approval"
    assert data["requires_approval"] is True
    assert data["approval_id"] is not None
    assert "draft_id" in data

    # Verify database persistence
    db = SessionLocal()
    try:
        approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == data["approval_id"]).first()
        assert approval is not None
        assert approval.status == ApprovalStatus.PENDING
        assert approval.action_type == "website_content_update"

        draft = db.query(WebsiteDraft).filter(WebsiteDraft.id == data["draft_id"]).first()
        assert draft is not None
        assert draft.slug == "courses/qc100"
    finally:
        db.close()

    print("[PASS] test_draft_creation_and_approval_gate passed.")


def test_unapproved_publish_rejection():
    """Verify that publishing an unapproved draft raises a PermissionError / 403."""
    update_res = website_agent.update_page(
        query="Update tuition policies with new 2027 deadlines",
        target_page="tuition-and-fees"
    )
    draft_id = update_res.draft_id

    # Verify attempt to publish immediately without approval fails
    try:
        website_agent.publish_draft(draft_id)
        assert False, "Should have raised PermissionError"
    except PermissionError as exc:
        assert "Approval gate" in str(exc)
        print("[PASS] test_unapproved_publish_rejection: correctly blocked unapproved publish.")


def test_approved_publish_and_preflight():
    """Verify that approving a draft enables CMS publishing and records audit log."""
    update_res = website_agent.update_page(
        query="Update CS201 Data Structures schedule to Monday/Wednesday",
        target_page="courses/cs201"
    )
    draft_id = update_res.draft_id
    approval_id = update_res.approval_id

    # Simulate administrator granting approval
    db = SessionLocal()
    try:
        approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
        if approval:
            approval.status = ApprovalStatus.APPROVED
            db.commit()
    finally:
        db.close()

    # Now publishing should succeed
    deploy_result = website_agent.publish_draft(draft_id, environment="production")
    assert deploy_result.status in ["success", "degraded"]
    assert deploy_result.preflight_checks["passed"] is True
    assert "http://localhost:3000" in deploy_result.live_url

    # Verify deployment audit record
    db = SessionLocal()
    try:
        deploy_log = db.query(DeploymentAuditLog).filter(DeploymentAuditLog.draft_id == draft_id).first()
        assert deploy_log is not None
        assert deploy_log.status == deploy_result.status
    finally:
        db.close()

    print("[PASS] test_approved_publish_and_preflight passed.")


def test_fastapi_endpoints():
    """Verify the /api/v1/website-agent endpoints via TestClient."""
    # 1. Propose page update
    req_body = {
        "query": "Add new bioengineering syllabus details to bio101",
        "target_page": "courses/bio101",
        "title": "BIO101: General Biology & Biotechnology",
        "page_type": "course"
    }
    res = client.post("/api/v1/website-agent/update-page", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert "draft_id" in data
    assert data["requires_approval"] is True
    assert data["status"] == "pending_approval"
    draft_id = data["draft_id"]
    approval_id = data["approval_id"]

    # 2. Retrieve draft
    get_res = client.get(f"/api/v1/website-agent/drafts/{draft_id}")
    assert get_res.status_code == 200
    assert get_res.json()["draft_id"] == draft_id

    # 3. Attempt publish while pending -> 403 Forbidden
    pub_res = client.post(f"/api/v1/website-agent/drafts/{draft_id}/publish", json={"environment": "production"})
    assert pub_res.status_code == 403
    assert "Approval gate" in pub_res.json()["detail"]

    # 4. Approve ticket directly in DB
    db = SessionLocal()
    try:
        appr = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
        if appr:
            appr.status = ApprovalStatus.APPROVED
            db.commit()
    finally:
        db.close()

    # 5. Publish approved draft -> 200 OK
    pub_res_ok = client.post(f"/api/v1/website-agent/drafts/{draft_id}/publish", json={"environment": "production"})
    assert pub_res_ok.status_code == 200
    deploy_data = pub_res_ok.json()
    assert deploy_data["status"] in ["success", "degraded"]
    assert "live_url" in deploy_data

    # 6. List pages
    pages_res = client.get("/api/v1/website-agent/pages")
    assert pages_res.status_code == 200
    assert len(pages_res.json()) >= 4

    print("[PASS] test_fastapi_endpoints passed.")


if __name__ == "__main__":
    print("\n--- Running Website Agent Test Suite ---")
    test_cms_adapter()
    test_seo_metadata_tool()
    test_draft_creation_and_approval_gate()
    test_unapproved_publish_rejection()
    test_approved_publish_and_preflight()
    test_fastapi_endpoints()
    print("\n>>> ALL PHASE 4 WEBSITE AGENT TESTS PASSED SUCCESSFULLY! <<<\n")

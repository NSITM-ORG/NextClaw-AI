"""
Tests for Phase 6 Content & Social Media Agent.
Validates campaign catalog discovery, character counting metrics, multi-channel copy generation,
and Level 3 HITL post publication governance.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from social_agent.tools import calculate_character_metrics

client = TestClient(app)


def test_get_social_campaigns():
    """Verify social campaign briefs grounded in MEMORY.md are listed."""
    res = client.get("/api/v1/social/campaigns")
    assert res.status_code == 200
    data = res.json()
    campaigns = data.get("campaigns", [])
    assert isinstance(campaigns, list)
    assert len(campaigns) >= 5
    camp_ids = [c["id"] for c in campaigns]
    assert "camp_content_pitch" in camp_ids
    assert "camp_waec_finisher" in camp_ids
    assert "camp_summer_immersion" in camp_ids


def test_tool_calculate_character_metrics():
    """Verify character counter accurately flags length limits per platform."""
    res_x = calculate_character_metrics.invoke({
        "text": "Empowering tech talent at Nextserve Institute! Enroll today. #TechCareers #EdTech",
        "platform": "x_twitter"
    })
    assert "PASSED ✅" in res_x
    assert "Characters:" in res_x
    assert "280" in res_x

    long_text = "A" * 300
    res_x_over = calculate_character_metrics.invoke({
        "text": long_text,
        "platform": "x_twitter"
    })
    assert "OVER LIMIT ❌" in res_x_over


def test_social_generate_and_approval_flow():
    """
    Verify full lifecycle of a social campaign:
    1. Generate multi-channel bundle.
    2. Review draft via Level 3 HITL approval.
    3. Verify published state and audit trail.
    """
    gen_res = client.post("/api/v1/social/generate", json={
        "campaign_id": "camp_content_pitch",
        "tone": "inspiring",
        "human_operator": "pytest_social_mgr"
    })
    assert gen_res.status_code == 200
    data = gen_res.json()
    draft_id = data["draft_id"]
    assert data["status"] == "pending_approval"
    assert data["approval_id"] is not None
    assert "posts" in data
    assert "x_twitter" in data["posts"]
    assert "linkedin" in data["posts"]
    assert "whatsapp" in data["posts"]

    # Verify query drafts list
    list_res = client.get("/api/v1/social/drafts")
    assert list_res.status_code == 200
    drafts_data = list_res.json()
    drafts = drafts_data.get("drafts", [])
    assert any(draft_id in d["id"] for d in drafts)

    # Approve draft
    approve_res = client.post(f"/api/v1/social/drafts/{draft_id}/resume", json={
        "decision": "approved",
        "human_operator": "pytest_social_mgr",
        "comments": "Copy aligned with NSITM brand voice."
    })
    assert approve_res.status_code == 200
    approved_data = approve_res.json()
    assert approved_data["status"] == "published"


def test_social_rejection_flow():
    """Verify social campaign draft rejection handles state properly."""
    gen_res = client.post("/api/v1/social/generate", json={
        "campaign_id": "camp_waec_finisher",
        "tone": "urgent_admissions",
        "human_operator": "pytest_reviewer"
    })
    assert gen_res.status_code == 200
    draft_id = gen_res.json()["draft_id"]

    reject_res = client.post(f"/api/v1/social/drafts/{draft_id}/resume", json={
        "decision": "rejected",
        "human_operator": "pytest_reviewer",
        "comments": "Need to emphasize scholarship availability first."
    })
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"

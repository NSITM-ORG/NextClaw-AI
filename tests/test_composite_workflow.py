"""
Tests for Multi-Agent Composite Orchestrator Pipeline (Section 1 Demo).
Validates end-to-end multi-agent coordination between Academic Advising,
Autonomous Coding, Website CMS, and Level 3 HITL Governance.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from app.services.composite_workflow import CompositeWorkflowOrchestrator

client = TestClient(app)


def test_get_composite_presets():
    """Verify composite preset blueprints are exposed via REST API."""
    res = client.get("/api/v1/composite/presets")
    assert res.status_code == 200
    data = res.json()
    presets = data.get("presets", {})
    assert isinstance(presets, dict)
    assert len(presets) >= 3
    assert "course_launch" in presets
    assert "curriculum_patch" in presets
    assert "tuition_policy_update" in presets


def test_composite_pipeline_approval_flow():
    """
    Verify end-to-end composite pipeline execution:
    1. Start workflow with a preset.
    2. Stages 1-3 complete (School Agent specs, Coding PR diff, CMS page draft).
    3. Stage 4 pauses for Level 3 HITL approval.
    4. Resume with 'approved' decision merges patch and dispatches production updates.
    """
    start_res = client.post("/api/v1/composite/start", json={
        "preset_key": "curriculum_patch",
        "human_operator": "pytest_admin"
    })
    assert start_res.status_code == 200
    data = start_res.json()
    pipeline_id = data["pipeline_id"]
    assert data["status"] == "awaiting_approval"
    assert data["approval_id"] is not None
    assert data["coding_output"] is not None
    assert data["website_output"] is not None
    assert data["school_output"] is not None
    assert len(data["timeline"]) >= 3

    # Verify pipeline state query
    get_res = client.get(f"/api/v1/composite/{pipeline_id}")
    assert get_res.status_code == 200
    pipe_data = get_res.json()
    assert pipe_data["status"] == "awaiting_approval"
    assert len(pipe_data["timeline"]) >= 3

    # Resume with approval
    resume_res = client.post(f"/api/v1/composite/{pipeline_id}/resume", json={
        "decision": "approved",
        "human_operator": "pytest_admin",
        "comments": "Approved via automated test suite."
    })
    assert resume_res.status_code == 200
    resumed_data = resume_res.json()
    assert resumed_data["status"] == "completed"
    assert resumed_data["audit_log_id"] is not None
    assert resumed_data["production_deployed"] is True


def test_composite_pipeline_rejection_flow():
    """Verify composite pipeline properly handles human rejection."""
    start_res = client.post("/api/v1/composite/start", json={
        "preset_key": "tuition_policy_update",
        "human_operator": "pytest_auditor"
    })
    assert start_res.status_code == 200
    pipeline_id = start_res.json()["pipeline_id"]

    # Reject the change
    resume_res = client.post(f"/api/v1/composite/{pipeline_id}/resume", json={
        "decision": "rejected",
        "human_operator": "pytest_auditor",
        "comments": "Tuition formula requires Senate council sign-off."
    })
    assert resume_res.status_code == 200
    resumed_data = resume_res.json()
    assert resumed_data["status"] == "rejected"
    assert resumed_data["production_deployed"] is False

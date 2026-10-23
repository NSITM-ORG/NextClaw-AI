"""API Routes for Multi-Agent Composite Orchestrator Pipeline (api/routes/composite.py).

Implements Section 1 & Section 2 composite pipeline endpoints coordinating:
- School Advising Agent
- Autonomous Coding Agent
- Website & Content Management Agent
- Level 3 Human-in-the-Loop Governance Gate
- Multi-Channel Dispatch (Telegram + SMTP Email + Audit Log)
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.composite_workflow import composite_orchestrator, COMPOSITE_PRESETS

router = APIRouter(prefix="/composite", tags=["multi-agent-composite-pipeline"])


class CompositePipelineStartRequest(BaseModel):
    title: Optional[str] = Field(None, description="Workflow title or summary")
    prompt: Optional[str] = Field(None, description="Action prompt or specification")
    category: Optional[str] = Field("custom", description="Category: course_launch, tuition_policy_update, curriculum_patch, custom")
    preset_key: Optional[str] = Field(None, description="Preset key from COMPOSITE_PRESETS if using blueprint")
    preset_id: Optional[str] = Field(None, description="Alias for preset_key")
    human_operator: Optional[str] = Field(None, description="Operator name or identifier")
    require_approval: Optional[bool] = Field(True, description="Enforce Level 3 Human-in-the-Loop gate before live deploy")


class CompositePipelineResumeRequest(BaseModel):
    approved: Optional[bool] = Field(None, description="True to approve and deploy; False to reject")
    decision: Optional[str] = Field(None, description="'approved' or 'rejected'")
    reviewer_notes: Optional[str] = Field(None, description="Reviewer feedback or authorization remarks")
    comments: Optional[str] = Field(None, description="Alias for reviewer_notes")
    human_operator: Optional[str] = Field(None, description="Approver identifier")


@router.get("/presets", summary="List available composite workflow blueprints")
def list_presets():
    """Returns preset composite workflow templates demonstrated in Section 1."""
    return {"presets": COMPOSITE_PRESETS}


@router.post("/start", summary="Start end-to-end multi-agent composite pipeline")
def start_composite_pipeline(payload: CompositePipelineStartRequest):
    """
    Initiates the multi-agent pipeline across Academic, Coding, and Website agents,
    pausing before live execution at the Level 3 Human-in-the-Loop gate.
    """
    key = payload.preset_key or payload.preset_id
    title = payload.title
    prompt = payload.prompt
    category = payload.category or "custom"

    # Use preset if specified
    if key and key in COMPOSITE_PRESETS:
        preset = COMPOSITE_PRESETS[key]
        title = title or preset["title"]
        prompt = prompt or preset["prompt"]
        category = preset.get("category", category)

    if not title:
        title = "Composite Workflow Run"
    if not prompt:
        prompt = "Execute standard composite catalog update"

    try:
        result = composite_orchestrator.start_pipeline(
            title=title,
            prompt=prompt,
            category=category,
            require_approval=payload.require_approval if payload.require_approval is not None else True
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start composite pipeline: {str(exc)}"
        )


@router.post("/{pipeline_id}/resume", summary="Authorize or reject Level 3 composite gate")
def resume_composite_pipeline(pipeline_id: str, payload: CompositePipelineResumeRequest):
    """
    Processes human authorization decision. If approved, merges code patch,
    publishes website CMS live, writes audit logs, and dispatches Telegram/Email.
    """
    is_approved = payload.approved
    if is_approved is None and payload.decision:
        is_approved = payload.decision.lower() in ["approved", "approve", "yes", "true"]
    if is_approved is None:
        is_approved = False
    notes = payload.reviewer_notes or payload.comments or ""

    result = composite_orchestrator.resume_pipeline(
        pipeline_id=pipeline_id,
        approved=is_approved,
        reviewer_notes=notes
    )
    if result.get("status") == "failed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Failed to resume pipeline")
        )
    return result


@router.get("/{pipeline_id}", summary="Get pipeline run details and timeline")
def get_composite_pipeline(pipeline_id: str):
    """Fetches real-time status, agent outputs, and execution timeline for a pipeline."""
    data = composite_orchestrator.get_pipeline(pipeline_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline with ID '{pipeline_id}' not found."
        )
    return data


@router.get("/", summary="List recent composite pipeline runs")
def list_composite_pipelines(limit: int = 15):
    """Returns recent multi-agent composite pipeline runs."""
    return {"pipelines": composite_orchestrator.list_pipelines(limit=limit)}

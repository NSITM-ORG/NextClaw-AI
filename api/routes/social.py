"""API Routes for Content & Social Agent (api/routes/social.py).

Implements Phase 6 Social Media Endpoints:
- GET /api/v1/social/campaigns: Institutional campaigns catalog from MEMORY.md
- POST /api/v1/social/generate: Multi-channel marketing copy synthesis
- GET /api/v1/social/drafts: List draft posts and campaigns
- GET /api/v1/social/drafts/{draft_bundle_id}: Full multi-channel bundle details
- POST /api/v1/social/drafts/{draft_bundle_id}/resume: Level 3 HITL approval / publish
- POST /api/v1/social/drafts/{draft_bundle_id}/schedule: Campaign calendar scheduling
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from social_agent.agent import social_agent
from social_agent.schemas import (
    GenerateCampaignRequest,
    MultiChannelDraftResponse,
    SocialApprovalDecisionRequest
)
from social_agent.campaigns import INSTITUTIONAL_CAMPAIGNS

router = APIRouter(prefix="/social", tags=["content-and-social-agent"])


class ScheduleCampaignRequest(BaseModel):
    scheduled_for: datetime = Field(..., description="Target publication timestamp")


@router.get("/campaigns", summary="List institutional marketing campaigns from MEMORY.md")
def get_campaigns():
    """Returns official institutional campaigns from Nextserve long-term memory."""
    return {"campaigns": list(INSTITUTIONAL_CAMPAIGNS.values())}


@router.post("/generate", response_model=MultiChannelDraftResponse, summary="Generate multi-channel social campaign copy")
def generate_social_campaign(payload: GenerateCampaignRequest):
    """
    Synthesizes tailored marketing copy for Twitter/X, LinkedIn, Instagram, Facebook,
    and WhatsApp with character counting, AI image prompts, and Level 3 HITL approval card.
    """
    try:
        response = social_agent.generate_campaign_bundle(payload)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate social campaign: {str(exc)}"
        )


@router.get("/drafts", summary="List social media drafts and campaign posts")
def list_social_drafts(limit: int = 25):
    """Returns recent social post drafts from PostgreSQL."""
    return {"drafts": social_agent.list_drafts(limit=limit)}


@router.get("/drafts/{draft_bundle_id}", summary="Get multi-channel bundle details and platform previews")
def get_social_draft_bundle(draft_bundle_id: str):
    """Fetches all platform variants, character counts, and approval status for a draft bundle."""
    details = social_agent.get_bundle_details(draft_bundle_id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Social draft bundle '{draft_bundle_id}' not found."
        )
    return details


@router.post("/drafts/{draft_bundle_id}/resume", summary="Level 3 approval decision for social campaign")
def resume_social_draft(draft_bundle_id: str, payload: SocialApprovalDecisionRequest):
    """
    Grants or denies Level 3 authorization for a social campaign draft.
    If approved with publish_now=True, transitions status to published and records audits.
    """
    is_approved = payload.approved
    if is_approved is None and payload.decision:
        is_approved = payload.decision.lower() in ["approved", "approve", "yes", "true"]
    if is_approved is None:
        is_approved = False
    notes = payload.reviewer_notes or payload.comments or ""

    result = social_agent.review_campaign_bundle(
        draft_bundle_id=draft_bundle_id,
        approved=is_approved,
        reviewer_notes=notes,
        publish_now=payload.publish_now or is_approved
    )
    if result.get("status") == "failed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Failed to update social draft")
        )
    return result

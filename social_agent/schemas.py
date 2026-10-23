"""Pydantic schemas and models for Phase 6 Content & Social Agent (social_agent/schemas.py)."""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SocialPlatform(str, Enum):
    X_TWITTER = "x_twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    WHATSAPP = "whatsapp"


class PostTone(str, Enum):
    INSPIRING = "inspiring"
    EDUCATIONAL = "educational"
    URGENT_ADMISSIONS = "urgent_admissions"
    PROFESSIONAL = "professional"


class CampaignInfo(BaseModel):
    id: str
    name: str
    target_audience: str
    key_objective: str
    dates: str
    default_hashtags: List[str]


class SinglePostContent(BaseModel):
    platform: SocialPlatform
    title: str
    content: str
    hashtags: List[str]
    character_count: int
    char_limit: int
    cta_link: str
    media_prompt: Optional[str] = None
    status: str = "pending_approval"


class GenerateCampaignRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Core subject or announcement topic")
    campaign_id: Optional[str] = Field(None, description="Campaign identifier from institutional memory")
    tone: Optional[Any] = Field("inspiring", description="Voice style for marketing copy")
    platforms: Optional[List[SocialPlatform]] = Field(
        default=[SocialPlatform.X_TWITTER, SocialPlatform.LINKEDIN, SocialPlatform.INSTAGRAM, SocialPlatform.WHATSAPP],
        description="Target social media channels"
    )
    course_name: Optional[str] = Field(None, description="Optional associated course")
    scheduled_for: Optional[datetime] = Field(None, description="Optional target publication time")
    human_operator: Optional[str] = Field(None, description="Operator initiating generation")


class MultiChannelDraftResponse(BaseModel):
    draft_id: str
    campaign_id: Optional[str] = None
    campaign_name: Optional[str] = None
    topic: str
    tone: Any
    posts: Dict[str, SinglePostContent]
    approval_id: Optional[int] = None
    requires_approval: bool = True
    status: str = "pending_approval"
    created_at: str


class SocialApprovalDecisionRequest(BaseModel):
    approved: Optional[bool] = None
    decision: Optional[str] = None
    reviewer_notes: Optional[str] = None
    comments: Optional[str] = None
    human_operator: Optional[str] = None
    publish_now: bool = False

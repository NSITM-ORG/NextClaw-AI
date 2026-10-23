"""Content & Social Media Agent Package (Phase 6)."""

from social_agent.agent import social_agent, SocialAgent
from social_agent.schemas import (
    SocialPlatform,
    PostTone,
    GenerateCampaignRequest,
    MultiChannelDraftResponse,
    SinglePostContent
)
from social_agent.campaigns import INSTITUTIONAL_CAMPAIGNS

__all__ = [
    "social_agent",
    "SocialAgent",
    "SocialPlatform",
    "PostTone",
    "GenerateCampaignRequest",
    "MultiChannelDraftResponse",
    "SinglePostContent",
    "INSTITUTIONAL_CAMPAIGNS"
]

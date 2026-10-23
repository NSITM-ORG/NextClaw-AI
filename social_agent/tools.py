"""LangChain tools for Content & Social Agent (social_agent/tools.py)."""

from typing import Dict, Any, List
from langchain_core.tools import tool

from social_agent.campaigns import INSTITUTIONAL_CAMPAIGNS
from social_agent.schemas import PostTone


@tool
def get_campaign_brief(campaign_id: str) -> str:
    """Retrieves target audience, budget, dates, and objectives for an institutional campaign.

    Args:
        campaign_id: Campaign key (e.g. 'camp_content_pitch', 'camp_waec_finisher', 'camp_cohort_flagship')
    """
    camp = INSTITUTIONAL_CAMPAIGNS.get(campaign_id.strip().lower())
    if not camp:
        return f"Campaign '{campaign_id}' not found. Available campaigns: {', '.join(INSTITUTIONAL_CAMPAIGNS.keys())}"
    
    return (
        f"Campaign: {camp['name']}\n"
        f"Objective: {camp['key_objective']}\n"
        f"Target Audience: {camp['target_audience']}\n"
        f"Dates: {camp['dates']}\n"
        f"Hashtags: {', '.join(camp['default_hashtags'])}\n"
        f"CTA: {camp['cta_url']}"
    )


@tool
def calculate_character_metrics(text: str, platform: str) -> str:
    """Calculates character count, word count, and validates length against platform constraints.

    Args:
        text: The draft post copy.
        platform: 'x_twitter', 'linkedin', 'instagram', 'facebook', or 'whatsapp'.
    """
    length = len(text)
    words = len(text.split())
    limits = {
        "x_twitter": 280,
        "linkedin": 3000,
        "instagram": 2200,
        "facebook": 63206,
        "whatsapp": 4096
    }
    limit = limits.get(platform.lower(), 280)
    fits = length <= limit

    return (
        f"Platform: {platform} | Characters: {length}/{limit} ({'PASSED ✅' if fits else 'OVER LIMIT ❌'}) | "
        f"Words: {words}"
    )

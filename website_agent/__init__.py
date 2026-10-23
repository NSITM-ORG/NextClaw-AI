"""
Nextserve AI Assistant - Website Agent Module.
Handles automated website CMS operations, page draft generation, SEO metadata,
preflight verification, and Level 3 Human-in-the-Loop publishing workflows.
"""

from website_agent.schemas import (
    SEOData,
    PageContent,
    PageUpdateRequest,
    PageUpdateResponse,
    PublishRequest,
    DeploymentResult
)
from website_agent.cms_adapter import CMSAdapter, LocalNextjsCMSAdapter
from website_agent.agent import WebsiteAgent, website_agent

__all__ = [
    "SEOData",
    "PageContent",
    "PageUpdateRequest",
    "PageUpdateResponse",
    "PublishRequest",
    "DeploymentResult",
    "CMSAdapter",
    "LocalNextjsCMSAdapter",
    "WebsiteAgent",
    "website_agent"
]

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SEOData(BaseModel):
    """Structured SEO metadata for search engine optimization and social previews."""
    title: str = Field(..., description="Target page title tag (50-60 characters)")
    meta_description: str = Field(..., description="Compelling meta description (150-160 characters)")
    keywords: List[str] = Field(default_factory=list, description="Target search keywords and phrases")
    og_title: Optional[str] = Field(None, description="OpenGraph social card title")
    og_description: Optional[str] = Field(None, description="OpenGraph social card description")
    og_image: Optional[str] = Field(None, description="OpenGraph banner asset URL")


class PageContent(BaseModel):
    """Website page state representation."""
    slug: str = Field(..., description="URL path identifier (e.g., 'courses/cs101' or 'admissions')")
    title: str = Field(..., description="Main page headline")
    content: str = Field(..., description="Markdown or HTML content body")
    page_type: str = Field("general", description="Page category: 'course', 'policy', 'landing', 'general'")
    seo: Optional[SEOData] = None
    updated_at: Optional[datetime] = None


class PageUpdateRequest(BaseModel):
    """
    Input schema for website modifications.
    Accepts natural language instructions (e.g. 'Update CS101 schedule and tuition')
    or structured page edits.
    """
    query: Optional[str] = Field(None, description="Natural language update directive")
    target_page: Optional[str] = Field(None, description="Target page slug (e.g., 'courses/cs101')")
    title: Optional[str] = Field(None, description="Explicit new title")
    content: Optional[str] = Field(None, description="Explicit new content (markdown or json)")
    page_type: Optional[str] = Field("general", description="Page type")
    changes: Optional[Dict[str, Any]] = Field(None, description="Structured dictionary of changes")
    auto_generate_seo: bool = Field(True, description="Automatically calculate optimized SEO metadata")


class PageUpdateResponse(BaseModel):
    """
    Response returned by the Website Agent when proposing changes.
    Enforces the Zero-Unapproved-Writes principle by locking execution
    behind an ApprovalRequest ticket.
    """
    draft_id: str = Field(..., description="Unique draft identifier")
    slug: str = Field(..., description="Target page URL slug")
    title: str = Field(..., description="Proposed page title")
    content_preview: str = Field(..., description="Truncated preview or summary of proposed content")
    proposed_changes: Dict[str, Any] = Field(default_factory=dict, description="Detailed diff / field changes")
    seo: Optional[SEOData] = Field(None, description="Auto-generated SEO metadata")
    preview_url: str = Field(..., description="Live staging preview link")
    approval_id: Optional[int] = Field(None, description="ID of the generated Level 3 ApprovalRequest")
    requires_approval: bool = Field(True, description="Enforces Human-in-the-Loop review")
    status: str = Field("pending_approval", description="Current draft status")
    message: str = Field(..., description="Human-readable summary of the agent action")


class PublishRequest(BaseModel):
    """Payload to trigger CMS deployment of an approved draft."""
    notes: Optional[str] = Field(None, description="Deployment changelog notes")
    environment: str = Field("production", description="Target environment: 'production' or 'staging'")


class DeploymentResult(BaseModel):
    """Audit response after CMS deployment and preflight verification."""
    deployment_id: str
    draft_id: str
    environment: str
    status: str  # 'success', 'failed', 'rolled_back'
    preflight_checks: Dict[str, Any]
    live_url: str
    deployed_at: datetime

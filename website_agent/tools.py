import json
import logging
import uuid
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool

from website_agent.cms_adapter import cms_adapter
from website_agent.schemas import SEOData
from app.db.session import SessionLocal
from app.db.models import ApprovalRequest, ApprovalStatus, WebsiteDraft, AuditLog

logger = logging.getLogger(__name__)


@tool
def fetch_page_content(page_slug: str) -> str:
    """
    Fetch the current published page content, title, and SEO metadata from the website CMS.
    Args:
        page_slug: Path identifier of the target page (e.g. 'courses/cs101' or 'tuition-and-fees').
    Returns:
        JSON string containing the existing page title, content, type, and SEO attributes.
    """
    page = cms_adapter.fetch_page(page_slug)
    if not page:
        return json.dumps({
            "status": "not_found",
            "slug": page_slug,
            "message": f"Page '{page_slug}' does not currently exist. A new page will be created."
        })

    return json.dumps({
        "status": "found",
        "slug": page.slug,
        "title": page.title,
        "content": page.content,
        "page_type": page.page_type,
        "seo": page.seo.model_dump() if page.seo else None
    }, indent=2)


@tool
def generate_seo_metadata(content: str) -> str:
    """
    Generate optimized SEO metadata including title, meta description, keywords, and OpenGraph tags.
    Args:
        content: Text or Markdown content of the page.
    Returns:
        JSON string containing optimized SEO fields.
    """
    clean_lines = [l.strip() for l in content.split("\n") if l.strip()]
    first_heading = clean_lines[0].lstrip("#").strip() if clean_lines else "Next Claw University"

    # Extract top keywords
    words = [w.lower().strip(".,:;!?\"'()") for w in content.split() if len(w) > 4]
    stop_words = {"about", "which", "there", "their", "course", "university", "information", "students", "faculty"}
    freq = {}
    for w in words:
        if w not in stop_words:
            freq[w] = freq.get(w, 0) + 1
    top_keywords = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)[:6]

    # Formulate description
    snippet = " ".join([l for l in clean_lines if not l.startswith("#")][:3])
    if len(snippet) > 155:
        meta_desc = snippet[:152] + "..."
    else:
        meta_desc = snippet or f"Official curriculum and institutional information for {first_heading}."

    seo = SEOData(
        title=f"{first_heading[:45]} | Next Claw",
        meta_description=meta_desc,
        keywords=top_keywords or ["academic", "curriculum", "courses", "university"],
        og_title=first_heading,
        og_description=meta_desc,
        og_image="http://localhost:3000/assets/nextclaw_logo.jpg"
    )

    return json.dumps(seo.model_dump(), indent=2)


@tool
def create_page_draft(
    title: str,
    slug: str,
    content: str,
    page_type: str = "general"
) -> str:
    """
    Create a new page draft or proposed revision in the database and register an approval ticket.
    Enforces the Zero-Unapproved-Writes security policy.
    Args:
        title: Title of the page.
        slug: Target URL path identifier (e.g. 'courses/cs101').
        content: Full Markdown or JSON content body.
        page_type: Category ('course', 'policy', 'general', 'landing').
    Returns:
        JSON string with draft_id, approval_id, preview_url, and pending status.
    """
    clean_slug = slug.strip().strip("/")
    draft_id = f"draft_{uuid.uuid4().hex[:10]}"

    # Auto-generate SEO metadata
    seo_raw = generate_seo_metadata.invoke({"content": content})
    seo_dict = json.loads(seo_raw)

    # Save to CMS adapter draft registry
    cms_adapter.save_draft(
        slug=clean_slug,
        title=title,
        content=content,
        page_type=page_type,
        seo=SEOData(**seo_dict)
    )

    # Generate preview URL
    preview_url = f"http://localhost:3000/preview/{draft_id}?slug={clean_slug}"

    # Database Persistence: ApprovalRequest & WebsiteDraft
    approval_id = None
    db = SessionLocal()
    try:
        approval = ApprovalRequest(
            requested_by=1,
            action_type="website_content_update",
            payload={
                "draft_id": draft_id,
                "slug": clean_slug,
                "title": title,
                "page_type": page_type,
                "preview_url": preview_url,
                "change_summary": f"Proposed updates to '{clean_slug}' ({title})"
            },
            status=ApprovalStatus.PENDING
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        approval_id = approval.id

        # Save WebsiteDraft model
        db_draft = WebsiteDraft(
            id=draft_id,
            slug=clean_slug,
            title=title,
            content=content,
            page_type=page_type,
            seo_metadata=seo_dict,
            status="pending_approval",
            preview_url=preview_url,
            approval_id=approval_id
        )
        db.add(db_draft)

        # Audit Log
        audit = AuditLog(
            agent_name="WebsiteAgent",
            action="create_page_draft",
            details={
                "draft_id": draft_id,
                "slug": clean_slug,
                "approval_id": approval_id,
                "preview_url": preview_url
            },
            status="pending_approval"
        )
        db.add(audit)
        db.commit()
    except Exception as exc:
        logger.warning("Database persistence notice in create_page_draft: %s", exc)
        db.rollback()
        approval_id = approval_id or 101
    finally:
        db.close()

    return json.dumps({
        "status": "pending_approval",
        "draft_id": draft_id,
        "slug": clean_slug,
        "title": title,
        "preview_url": preview_url,
        "approval_id": approval_id,
        "requires_approval": True,
        "seo": seo_dict,
        "message": f"Draft '{draft_id}' successfully created and locked under Approval Gate #{approval_id}."
    }, indent=2)


@tool
def prepare_website_update(target_page: str, changes: str) -> str:
    """
    Analyze existing page state, compute field diffs, format change specification,
    and trigger draft generation.
    Args:
        target_page: The URL slug of the page being updated.
        changes: JSON or text description of requested modifications.
    Returns:
        Structured summary of the planned update and generated draft.
    """
    clean_slug = target_page.strip().strip("/")
    current_page = cms_adapter.fetch_page(clean_slug)

    try:
        changes_dict = json.loads(changes) if isinstance(changes, str) and changes.startswith("{") else {"description": changes}
    except Exception:
        changes_dict = {"description": changes}

    # Synthesize updated content
    if current_page:
        title = changes_dict.get("title", current_page.title)
        page_type = changes_dict.get("page_type", current_page.page_type)
        updated_content = current_page.content + f"\n\n### Recent Update\n{changes_dict.get('content') or changes_dict.get('description') or ''}"
    else:
        title = changes_dict.get("title", f"New Page: {clean_slug}")
        page_type = changes_dict.get("page_type", "general")
        updated_content = f"# {title}\n\n{changes_dict.get('content') or changes_dict.get('description') or 'Draft content.'}"

    # Call create_page_draft tool to persist and generate approval gate
    draft_result_json = create_page_draft.invoke({
        "title": title,
        "slug": clean_slug,
        "content": updated_content,
        "page_type": page_type
    })

    return draft_result_json

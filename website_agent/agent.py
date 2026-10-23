import os
import json
import logging
import uuid
from typing import Optional, Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver

from website_agent.tools import (
    fetch_page_content,
    generate_seo_metadata,
    create_page_draft,
    prepare_website_update
)
from website_agent.cms_adapter import cms_adapter
from website_agent.schemas import PageUpdateResponse, SEOData, DeploymentResult
from app.db.session import SessionLocal
from app.db.models import WebsiteDraft, ApprovalRequest, ApprovalStatus, DeploymentAuditLog, AuditLog

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are the Website Agent for the Nextserve / Next Claw AI Operating Assistant. "
    "You handle automated CMS operations, website content updates, page drafting, and SEO optimization.\n\n"
    "CRITICAL SECURITY POLICY:\n"
    "1. You operate under a strict 'Zero-Unapproved-Writes' policy. Every write, edit, or publish action "
    "MUST create a draft and an approval ticket via `create_page_draft` or `prepare_website_update`.\n"
    "2. Before modifying an existing page, ALWAYS inspect its current state using `fetch_page_content`.\n"
    "3. Ensure every page has complete, optimized SEO metadata using `generate_seo_metadata`.\n"
    "4. Return structured draft information including the draft_id, preview_url, and approval status."
)

WEBSITE_TOOLS = [
    fetch_page_content,
    generate_seo_metadata,
    create_page_draft,
    prepare_website_update
]


def _build_langgraph_website_agent(api_key: Optional[str] = None):
    """Build LangGraph ReAct agent using ChatOpenAI(model='gpt-4o')."""
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=api_key or os.getenv("OPENAI_API_KEY")
    )
    checkpointer = MemorySaver()
    return create_react_agent(
        model=llm,
        tools=WEBSITE_TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )


class WebsiteAgent:
    """
    Principal Website Agent managing CMS content updates, drafting workflows,
    SEO generation, preflight checks, and safe deployment gates.
    """

    def __init__(self):
        self._agent = None
        self._checkpointer = MemorySaver()
        self._init_agent()

    def _init_agent(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("mock-"):
            try:
                self._agent = _build_langgraph_website_agent(openai_key)
                logger.info("WebsiteAgent: Initialized LangGraph ReAct agent with ChatOpenAI (gpt-4o).")
            except Exception as exc:
                logger.warning("WebsiteAgent: Could not build live OpenAI agent (%s). Using fallback runner.", exc)
                self._agent = None
        else:
            logger.info("WebsiteAgent: OPENAI_API_KEY not configured. Operating in deterministic tool-calling mode.")
            self._agent = None

    def update_page(
        self,
        query: Optional[str] = None,
        target_page: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        page_type: str = "general",
        changes: Optional[Dict[str, Any]] = None
    ) -> PageUpdateResponse:
        """
        Processes a page update directive and generates a locked draft with approval gate.
        """
        # 1. Deduce target slug and parameters
        prompt_text = query or ""
        slug = target_page or self._deduce_slug(prompt_text)

        # 2. If explicit title/content are provided or deduced
        if not title:
            title = self._deduce_title(slug, prompt_text)
        if not content:
            content = self._generate_draft_content(slug, title, prompt_text, changes)

        # 3. Create draft and approval request via tool
        draft_json_str = create_page_draft.invoke({
            "title": title,
            "slug": slug,
            "content": content,
            "page_type": page_type
        })
        draft_info = json.loads(draft_json_str)

        # 4. Construct PageUpdateResponse
        seo_meta = SEOData(**draft_info["seo"]) if draft_info.get("seo") else None
        preview_text = content[:220] + "..." if len(content) > 220 else content

        return PageUpdateResponse(
            draft_id=draft_info["draft_id"],
            slug=draft_info["slug"],
            title=draft_info["title"],
            content_preview=preview_text,
            proposed_changes=changes or {"action": "page_content_update", "instruction": prompt_text},
            seo=seo_meta,
            preview_url=draft_info["preview_url"],
            approval_id=draft_info["approval_id"],
            requires_approval=True,
            status=draft_info["status"],
            message=f"Page draft '{draft_info['draft_id']}' created for '{slug}'. Awaiting Level 3 Approval sign-off."
        )

    def publish_draft(self, draft_id: str, environment: str = "production", user_role: str = "Support Admin") -> DeploymentResult:
        """
        Publishes an approved draft to the CMS.
        Enforces approval verification: blocks publishing if approval is still pending or rejected.
        """
        db = SessionLocal()
        try:
            # Check draft in database
            db_draft = db.query(WebsiteDraft).filter(WebsiteDraft.id == draft_id).first()
            if db_draft and db_draft.approval_id:
                approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == db_draft.approval_id).first()
                if approval and approval.status != ApprovalStatus.APPROVED:
                    raise PermissionError(
                        f"Cannot publish draft '{draft_id}': Approval gate #{approval.id} is '{approval.status.value}'. "
                        "Action requires designated administrator sign-off."
                    )
            
            # Execute CMS publishing & preflight checks
            deploy_result = cms_adapter.publish_draft(draft_id, environment=environment)

            # Update database draft status
            if db_draft:
                db_draft.status = "published"
                db.commit()

            # Record deployment audit log
            audit_log = DeploymentAuditLog(
                draft_id=draft_id,
                environment=environment,
                status=deploy_result.status,
                preflight_results=deploy_result.preflight_checks,
                deployment_url=deploy_result.live_url,
                triggered_by=f"role:{user_role}"
            )
            db.add(audit_log)

            general_audit = AuditLog(
                agent_name="WebsiteAgent",
                action="publish_draft",
                details={
                    "draft_id": draft_id,
                    "deployment_id": deploy_result.deployment_id,
                    "environment": environment,
                    "preflight": deploy_result.preflight_checks
                },
                status="success"
            )
            db.add(general_audit)
            db.commit()

            return deploy_result
        except PermissionError:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            logger.error("Error publishing draft %s: %s", draft_id, exc)
            raise
        finally:
            db.close()

    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve draft specifications and current approval status."""
        db = SessionLocal()
        try:
            db_draft = db.query(WebsiteDraft).filter(WebsiteDraft.id == draft_id).first()
            if not db_draft:
                # Check CMS adapter fallback registry
                draft_data = cms_adapter._drafts.get(draft_id)
                if not draft_data:
                    return None
                return {
                    "draft_id": draft_id,
                    "slug": draft_data["slug"],
                    "title": draft_data["title"],
                    "content": draft_data["content"],
                    "page_type": draft_data.get("page_type", "general"),
                    "seo": draft_data.get("seo").model_dump() if draft_data.get("seo") else None,
                    "status": draft_data.get("status", "pending_approval"),
                    "preview_url": f"http://localhost:3000/preview/{draft_id}?slug={draft_data['slug']}"
                }

            return {
                "draft_id": db_draft.id,
                "slug": db_draft.slug,
                "title": db_draft.title,
                "content": db_draft.content,
                "page_type": db_draft.page_type,
                "seo": db_draft.seo_metadata,
                "status": db_draft.status,
                "preview_url": db_draft.preview_url,
                "approval_id": db_draft.approval_id,
                "created_at": db_draft.created_at.isoformat() if db_draft.created_at else None
            }
        finally:
            db.close()

    def _deduce_slug(self, text: str) -> str:
        text_lower = text.lower()
        if "cs101" in text_lower or "python" in text_lower:
            return "courses/cs101"
        elif "cs201" in text_lower or "data structure" in text_lower:
            return "courses/cs201"
        elif "cs350" in text_lower or "machine learning" in text_lower or "ai" in text_lower:
            return "courses/cs350"
        elif "tuition" in text_lower or "refund" in text_lower or "fee" in text_lower:
            return "tuition-and-fees"
        elif "admission" in text_lower or "enroll" in text_lower:
            return "admissions"
        elif "about" in text_lower:
            return "about"
        
        # Generic slugify
        words = [w for w in text_lower.split() if len(w) > 3][:3]
        return "-".join(words) if words else "updates/general"

    def _deduce_title(self, slug: str, prompt: str) -> str:
        existing = cms_adapter.fetch_page(slug)
        if existing:
            return existing.title
        clean_name = slug.replace("-", " ").replace("/", " - ").title()
        return clean_name or "Academic Program Update"

    def _generate_draft_content(self, slug: str, title: str, prompt: str, changes: Optional[Dict[str, Any]]) -> str:
        existing = cms_adapter.fetch_page(slug)
        base_body = existing.content if existing else f"# {title}\n\nOfficial university program description."
        update_note = prompt or "Updated course schedule, tuition fees, and curriculum details."
        return f"{base_body}\n\n### Proposed Revisions\n{update_note}"


# Singleton agent instance
website_agent = WebsiteAgent()

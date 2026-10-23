"""NextClaw OS - Website & CMS Staging Skill (skill_cms.py).

Handles draft content generation, HTML/Markdown preview generation,
and website CMS updates.
Execution Tier: TIER 2 (Draft & Review) | TIER 3 (Publish Live).
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

from skills import BaseSkill

logger = logging.getLogger("nextclaw.skills.cms")

STAGING_DRAFTS_DIR = Path(__file__).resolve().parent.parent / "configs" / "drafts"


class CMSSkill(BaseSkill):
    """Handles website announcements, course catalog updates, HTML previews, and live publishing."""

    name: str = "skill_cms"
    tier: int = 2
    description: str = "Website CMS drafting, HTML preview staging, and live site publishing."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        STAGING_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    def execute(self, action: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes CMS and website actions."""
        if action in ["draft_announcement", "create_draft", "draft"]:
            return self.create_draft_announcement(
                title=params.get("title", "Nextserve School Announcement"),
                category=params.get("category", "admissions"),
                content_markdown=params.get("content") or params.get("body", ""),
                target_audience=params.get("audience", "All Students")
            )

        elif action in ["generate_preview", "preview"]:
            draft_id = params.get("draft_id")
            return self.generate_preview(draft_id=draft_id)

        elif action in ["publish", "publish_live"]:
            # TIER 3: High Risk / Administrative
            draft_id = params.get("draft_id")
            approved = params.get("approved", False)
            if not approved:
                return {
                    "status": "approval_required",
                    "tier": 3,
                    "action": "publish_live",
                    "draft_id": draft_id,
                    "message": "Direct website publishing is a Tier 3 action and requires Telegram Admin approval."
                }
            return self.publish_draft_live(draft_id=draft_id)

        elif action == "list_drafts":
            return self.list_staged_drafts()

        else:
            return {
                "status": "error",
                "message": f"Unknown CMS action '{action}'. Valid actions: draft_announcement, generate_preview, publish_live, list_drafts"
            }

    def create_draft_announcement(
        self,
        title: str,
        category: str,
        content_markdown: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """Generates draft content and staging preview card (Tier 2)."""
        draft_id = f"CMS-DRAFT-{int(datetime.now(timezone.utc).timestamp())}"
        slug = title.lower().replace(" ", "-").replace(":", "").replace("/", "")[:50]

        html_preview = f"""
<div class="nextserve-announcement-card" style="border:1px solid #e2e8f0; border-radius:12px; padding:24px; font-family:'Segoe UI', sans-serif; background:#ffffff; max-width:680px; margin:0 auto; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
  <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
    <span style="background:#0284c7; color:#fff; font-size:12px; font-weight:bold; padding:4px 10px; border-radius:16px; text-transform:uppercase;">{category}</span>
    <span style="color:#64748b; font-size:13px;">Target: {target_audience}</span>
  </div>
  <h2 style="color:#0f172a; margin-top:0; font-size:22px; font-weight:700;">{title}</h2>
  <div style="color:#334155; line-height:1.6; font-size:15px;">
    {content_markdown.replace(chr(10), '<br>')}
  </div>
  <div style="margin-top:20px; padding-top:16px; border-top:1px solid #f1f5f9; display:flex; justify-content:space-between; align-items:center;">
    <span style="color:#94a3b8; font-size:12px;">Nextserve School CMS Staging • Draft ID: {draft_id}</span>
    <a href="https://nextserveschool.com/preview/{draft_id}" style="color:#0284c7; text-decoration:none; font-weight:600; font-size:13px;">Open Webview ↗</a>
  </div>
</div>
""".strip()

        draft_record = {
            "draft_id": draft_id,
            "title": title,
            "slug": slug,
            "category": category,
            "audience": target_audience,
            "content_markdown": content_markdown,
            "html_preview": html_preview,
            "preview_url": f"https://nextserveschool.com/staging/preview/{draft_id}",
            "status": "staged_for_review",
            "tier": 2,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Save to local drafts folder
        draft_file = STAGING_DRAFTS_DIR / f"{draft_id}.json"
        with open(draft_file, "w", encoding="utf-8") as f:
            json.dump(draft_record, f, indent=2)

        return {
            "status": "draft_created",
            "tier": 2,
            "draft_id": draft_id,
            "title": title,
            "preview_url": draft_record["preview_url"],
            "html_preview": html_preview,
            "message": "Draft created successfully and staged for administrative review. To publish live, submit for Tier 3 Admin approval."
        }

    def generate_preview(self, draft_id: str) -> Dict[str, Any]:
        """Loads and returns the HTML/Markdown preview for a staged draft."""
        draft_file = STAGING_DRAFTS_DIR / f"{draft_id}.json"
        if not draft_file.exists():
            return {"status": "not_found", "message": f"Draft '{draft_id}' not found."}

        with open(draft_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "status": "success",
            "draft_id": draft_id,
            "title": data.get("title"),
            "html_preview": data.get("html_preview"),
            "preview_url": data.get("preview_url"),
            "status_flag": data.get("status")
        }

    def publish_draft_live(self, draft_id: str) -> Dict[str, Any]:
        """Executes live publishing after receiving Tier 3 approval."""
        draft_file = STAGING_DRAFTS_DIR / f"{draft_id}.json"
        if not draft_file.exists():
            return {"status": "not_found", "message": f"Draft '{draft_id}' not found."}

        with open(draft_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["status"] = "published_live"
        data["published_at"] = datetime.now(timezone.utc).isoformat()

        with open(draft_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Published website announcement live: {data.get('title')} ({draft_id})")

        return {
            "status": "published",
            "tier": 3,
            "draft_id": draft_id,
            "live_url": f"https://nextserveschool.com/news/{data.get('slug')}",
            "title": data.get("title"),
            "published_at": data["published_at"]
        }

    def list_staged_drafts(self) -> Dict[str, Any]:
        """Returns all staged CMS drafts."""
        drafts = []
        for file in STAGING_DRAFTS_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    drafts.append(json.load(f))
            except Exception:
                pass
        return {"status": "success", "count": len(drafts), "drafts": drafts}

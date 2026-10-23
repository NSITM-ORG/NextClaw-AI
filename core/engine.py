"""NextClaw OS - Core Orchestrator Engine (core/engine.py).

Loads SOUL.md identity, MEMORY.md domain intelligence, and SKILLS.json.
Orchestrates LLM & skill execution with strict 3-Tier Security Gate enforcement.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from skills import skill_registry
from core.approval_gate import security_gate

logger = logging.getLogger("nextclaw.engine")

CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"
SOUL_PATH = CONFIGS_DIR / "SOUL.md"
MEMORY_PATH = CONFIGS_DIR / "MEMORY.md"
SKILLS_PATH = CONFIGS_DIR / "SKILLS.json"


class NextClawEngine:
    """Orchestrates Nextserve operational requests using file-driven blueprints & skills."""

    def __init__(self):
        self.soul_prompt = self._load_file(SOUL_PATH)
        self.memory_context = self._load_file(MEMORY_PATH)
        self.skills_config = self._load_json(SKILLS_PATH)
        logger.info("NextClaw OS Engine initialized with SOUL.md, MEMORY.md, and active skills.")

    def _load_file(self, path: Path) -> str:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def process_request(
        self,
        query: str,
        channel: str = "web",
        sender_id: str = "guest_user",
        sender_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processes an incoming inquiry or action command across any channel."""
        ctx = context or {}
        ctx["channel"] = channel
        ctx["sender_id"] = sender_id
        ctx["sender_name"] = sender_name

        query_clean = query.strip()
        query_lower = query_clean.lower()

        # ── 1. Intent Analysis & Skill Selection ──────────────────────

        # Check for High Risk / Administrative Tier 3 intents (e.g. Deferrals, Balance override)
        if any(term in query_lower for term in ["defer my admission", "defer enrollment", "deferral request", "postpone cohort"]):
            return self._handle_deferral_request(query_clean, ctx)

        elif any(term in query_lower for term in ["publish website", "publish announcement", "push to live website"]):
            return self._handle_cms_publish(query_clean, ctx)

        # Check for Tier 2 Draft & Review intents (e.g. Draft announcement, schedule event, draft email)
        elif any(term in query_lower for term in ["draft announcement", "draft a website post", "create announcement"]):
            return self._handle_cms_draft(query_clean, ctx)

        elif any(term in query_lower for term in ["schedule event", "create calendar event", "schedule webinar"]):
            return self._handle_calendar_schedule(query_clean, ctx)

        elif any(term in query_lower for term in ["draft email", "prepare student email"]):
            return self._handle_email_draft(query_clean, ctx)

        # Check for Calendar lookups (Tier 1)
        elif any(term in query_lower for term in ["cohort", "calendar", "webinar", "orientation", "when does class start", "start date", "schedule"]):
            cal_skill = skill_registry.get_skill("skill_calendar")
            if cal_skill:
                events_res = security_gate.enforce_gate(
                    "skill_calendar", "get_events", {"days_ahead": 45}, ctx,
                    execute_fn=lambda: cal_skill.execute("get_events", {"days_ahead": 45}, ctx)
                )
                return self._format_calendar_response(events_res, channel)

        # Check for Tuition Instalment breakdown calculation (Tier 1)
        elif any(term in query_lower for term in ["instalment", "installment", "pay in parts", "spread payment", "tranche"]):
            rag_skill = skill_registry.get_skill("skill_rag")
            if rag_skill:
                # Find course match
                calc_res = security_gate.enforce_gate(
                    "skill_rag", "calculate_instalments", {"name": query_clean}, ctx,
                    execute_fn=lambda: rag_skill.execute("calculate_instalments", {"name": query_clean}, ctx)
                )
                if calc_res.get("status") == "success":
                    return self._format_instalment_response(calc_res, channel)

        # Check for Specific Course or General Knowledge Base Search (Tier 1)
        rag_skill = skill_registry.get_skill("skill_rag")
        if rag_skill:
            rag_res = security_gate.enforce_gate(
                "skill_rag", "query", {"query": query_clean, "top_k": 3}, ctx,
                execute_fn=lambda: rag_skill.execute("query", {"query": query_clean, "top_k": 3}, ctx)
            )
            return self._format_rag_response(rag_res, query_clean, channel)

        return {
            "status": "success",
            "tier": 1,
            "channel": channel,
            "response": (
                "Welcome to Nextserve School of Information Technology and Management (NSITM)! "
                "We offer 26 accredited practical programmes. You can ask about course curriculums, "
                "tuition fees, 3-tranche instalment plans, or upcoming cohort start dates."
            )
        }

    # ── Handlers for Tier 2 and Tier 3 workflows ──────────────────────

    def _handle_deferral_request(self, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Handles student deferral submission (Tier 3 Gate)."""
        student_name = ctx.get("sender_name") or "Enrolled Student"
        params = {
            "student_name": student_name,
            "sender_id": ctx.get("sender_id"),
            "action": "approve_deferral",
            "reason": f"Student requested deferral: '{query}'",
            "target": f"Student {student_name} ({ctx.get('sender_id')})"
        }

        # Intercept via 3-Tier Security Gate
        gate_res = security_gate.enforce_gate(
            skill_name="skill_telegram",
            action="approve_deferral",
            params=params,
            context=ctx,
            execute_fn=lambda: {
                "status": "deferral_approved",
                "message": f"Admission for {student_name} deferred to the next cohort successfully."
            }
        )

        reply_text = (
            f"Dear {student_name}, your request to defer your admission has been logged. "
            f"Because cohort deferrals are administrative actions, your request has been routed to the "
            f"Academic Director via our Telegram Approval Gate [Ticket: {gate_res.get('ticket_id')}]. "
            f"You will receive an official confirmation once reviewed."
        )

        return {
            "status": "approval_required",
            "tier": 3,
            "ticket_id": gate_res.get("ticket_id"),
            "response": reply_text,
            "gate_details": gate_res
        }

    def _handle_cms_draft(self, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a website draft and stages preview (Tier 2 Gate)."""
        cms_skill = skill_registry.get_skill("skill_cms")
        title = "Nextserve Admissions & Cohort Announcement"
        if "title:" in query.lower():
            title = query.split("title:")[-1].split("\n")[0].strip()

        params = {
            "title": title,
            "category": "admissions",
            "content": f"Official Announcement from Nextserve School of IT & Management:\n\n{query}",
            "audience": "Prospective & Current Students"
        }

        gate_res = security_gate.enforce_gate(
            skill_name="skill_cms",
            action="draft_announcement",
            params=params,
            context=ctx,
            execute_fn=lambda: cms_skill.execute("draft_announcement", params, ctx) if cms_skill else {}
        )

        return {
            "status": "draft_created",
            "tier": 2,
            "draft_id": gate_res.get("draft_id"),
            "preview_url": gate_res.get("preview_url"),
            "response": (
                f"📝 Draft created: '{title}' [Draft ID: {gate_res.get('draft_id')}].\n"
                f"Staging preview link: {gate_res.get('preview_url')}\n"
                f"This draft is paused for review. To publish live to the public website, approve via Tier 3."
            ),
            "gate_details": gate_res
        }

    def _handle_cms_publish(self, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Publishes a CMS draft live (Tier 3 Gate)."""
        draft_id = "CMS-DRAFT-SAMPLE"
        for word in query.split():
            if word.startswith("CMS-DRAFT-"):
                draft_id = word.strip()

        params = {"draft_id": draft_id, "action": "publish_live", "target": f"Public Website ({draft_id})"}

        cms_skill = skill_registry.get_skill("skill_cms")
        gate_res = security_gate.enforce_gate(
            skill_name="skill_cms",
            action="publish_live",
            params=params,
            context=ctx,
            execute_fn=lambda: cms_skill.execute("publish_live", {"draft_id": draft_id, "approved": True}, ctx) if cms_skill else {}
        )

        return {
            "status": "approval_required",
            "tier": 3,
            "ticket_id": gate_res.get("ticket_id"),
            "response": (
                f"⚠️ Website publishing is a Tier 3 action. "
                f"An interactive Approval Card [Ticket {gate_res.get('ticket_id')}] has been sent to the Admin Telegram channel."
            ),
            "gate_details": gate_res
        }

    def _handle_calendar_schedule(self, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Schedules a calendar event draft (Tier 2 Gate)."""
        cal_skill = skill_registry.get_skill("skill_calendar")
        params = {
            "title": "Scheduled Academic Session",
            "type": "lecture",
            "location": "Lagos Hub Campus & Zoom",
            "description": query
        }

        gate_res = security_gate.enforce_gate(
            skill_name="skill_calendar",
            action="schedule_event",
            params=params,
            context=ctx,
            execute_fn=lambda: cal_skill.execute("schedule_event", params, ctx) if cal_skill else {}
        )

        return {
            "status": "draft_created",
            "tier": 2,
            "response": (
                f"📅 Event drafted: '{params['title']}'. "
                f"Status: Staged for review. Will be pushed to student calendar upon confirmation."
            ),
            "gate_details": gate_res
        }

    def _handle_email_draft(self, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Drafts a student email (Tier 2 Gate)."""
        params = {"subject": "Nextserve Admissions Update", "body": query}
        gate_res = security_gate.enforce_gate(
            skill_name="skill_messaging",
            action="draft_email",
            params=params,
            context=ctx,
            execute_fn=lambda: {
                "status": "draft_ready",
                "subject": params["subject"],
                "draft_body": params["body"],
                "preview": f"To: student@example.com\nSubject: {params['subject']}\n\n{params['body']}"
            }
        )

        return {
            "status": "draft_created",
            "tier": 2,
            "response": (
                f"✉️ Email draft prepared: '{params['subject']}'.\n"
                f"Held for review before dispatch."
            ),
            "gate_details": gate_res
        }

    # ── Formatting Helpers ────────────────────────────────────────────

    def _format_rag_response(self, rag_res: Dict[str, Any], query: str, channel: str) -> Dict[str, Any]:
        results = rag_res.get("results", [])
        if not results:
            reply = (
                "Thank you for contacting Nextserve School of IT & Management. "
                "We couldn't find an exact match for your request. "
                "Feel free to chat with our Admissions team on WhatsApp at +2348093344991."
            )
            return {"status": "success", "tier": 1, "response": reply}

        top = results[0]
        snippets = "\n\n".join([f"• <b>{r['title']}</b>:\n{r['snippet']}" for r in results[:2]])

        if channel == "whatsapp":
            reply = (
                f"🎓 *Nextserve School of IT & Management*\n\n"
                f"{snippets.replace('<b>', '*').replace('</b>', '*').replace('<i>', '_').replace('</i>', '_')}\n\n"
                f"📲 Need more details or want to enroll? Chat us directly on WhatsApp: +2348093344991"
            )
        else:
            reply = (
                f"🎓 <b>Nextserve School of IT & Management</b>\n\n"
                f"{snippets}\n\n"
                f"<i>All programmes feature hands-on projects, industry mentors, and portfolio defense.</i>"
            )

        return {"status": "success", "tier": 1, "channel": channel, "response": reply, "sources": results}

    def _format_instalment_response(self, calc_res: Dict[str, Any], channel: str) -> Dict[str, Any]:
        cname = calc_res.get("course_name")
        one_off = calc_res.get("one_off_discounted_tuition")
        total = calc_res.get("instalment_total")
        sched = calc_res.get("schedule", [])

        lines = [f"• {item['due']} ({item['percentage']}): <b>{item['amount']}</b>" for item in sched]
        sched_text = "\n".join(lines)

        reply = (
            f"💰 <b>Flexible Tuition Plan for {cname}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <b>One-Off Discounted Tuition:</b> {one_off}\n"
            f"💳 <b>3-Tranche Instalment Total:</b> {total}\n\n"
            f"<b>Payment Schedule:</b>\n{sched_text}\n\n"
            f"📌 <i>Note: A non-refundable application fee of {calc_res.get('registration_fee')} applies.</i>"
        )
        if channel == "whatsapp":
            reply = reply.replace("<b>", "*").replace("</b>", "*").replace("<i>", "_").replace("</i>", "_")

        return {"status": "success", "tier": 1, "response": reply, "breakdown": calc_res}

    def _format_calendar_response(self, events_res: Dict[str, Any], channel: str) -> Dict[str, Any]:
        events = events_res.get("events", [])
        if not events:
            return {"status": "success", "tier": 1, "response": "No upcoming events scheduled at this moment."}

        event_items = []
        for e in events[:3]:
            time_str = e.get("formatted_date", e.get("start_time"))
            event_items.append(
                f"📌 <b>{e['title']}</b>\n"
                f"  ⏰ {time_str} ({e.get('time_until', '')})\n"
                f"  📍 Location: {e.get('location', 'Online')}"
            )

        events_text = "\n\n".join(event_items)
        reply = (
            f"📅 <b>Upcoming Nextserve School Events & Cohorts</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{events_text}\n\n"
            f"⚡ <i>Join us live or visit our Lagos Hub Campus!</i>"
        )
        if channel == "whatsapp":
            reply = reply.replace("<b>", "*").replace("</b>", "*").replace("<i>", "_").replace("</i>", "_")

        return {"status": "success", "tier": 1, "response": reply, "events": events}


engine = NextClawEngine()

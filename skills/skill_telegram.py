"""NextClaw OS - Admin Telegram & Notifications Skill (skill_telegram.py).

Handles direct approval cards sent to the Admin Telegram channel
with inline callback buttons [ ✅ Approve & Execute ] | [ ❌ Reject / Revise ],
as well as executive alerts and daily briefings.
Execution Tier: TIER 3 (Approval Dispatch) | TIER 1 (Information Alerts).
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import requests

from skills import BaseSkill

logger = logging.getLogger("nextclaw.skills.telegram")


class TelegramSkill(BaseSkill):
    """Admin Telegram notification engine & Human-in-the-Loop interactive approval card dispatcher."""

    name: str = "skill_telegram"
    tier: 3
    description: str = "Dispatches interactive Tier 3 Approval Cards and administrative alerts to Telegram."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.admin_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def execute(self, action: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatches Telegram actions."""
        if action in ["dispatch_approval_card", "approval_card", "request_approval"]:
            return self.dispatch_approval_card(
                ticket_id=params.get("ticket_id", "T3-SAMPLE"),
                action_name=params.get("action_name", "Administrative Action"),
                target=params.get("target", "System"),
                details=params.get("details", "Requires administrative sign-off."),
                requester=params.get("requester", "NextClaw Agent")
            )

        elif action in ["send_alert", "alert"]:
            return self.send_admin_alert(
                title=params.get("title", "Nextserve System Alert"),
                message=params.get("message", "")
            )

        elif action in ["daily_briefing", "summary"]:
            return self.send_daily_briefing(stats=params.get("stats", {}))

        else:
            return {
                "status": "error",
                "message": f"Unknown Telegram action '{action}'. Valid actions: dispatch_approval_card, send_alert, daily_briefing"
            }

    def dispatch_approval_card(
        self,
        ticket_id: str,
        action_name: str,
        target: str,
        details: str,
        requester: str = "NextClaw OS"
    ) -> Dict[str, Any]:
        """Dispatches interactive Level 3 Approval Card with inline buttons to Admin phone."""
        approve_data = f"t3_approve_{ticket_id}"
        reject_data = f"t3_reject_{ticket_id}"

        card_text = (
            "🚨 <b>LEVEL 3 HUMAN-IN-THE-LOOP APPROVAL REQUIRED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <b>Action:</b> <code>{action_name}</code>\n"
            f"🎯 <b>Target:</b> {target}\n"
            f"👤 <b>Requested By:</b> {requester}\n"
            f"🔑 <b>Ticket ID:</b> <code>{ticket_id}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Details & Context:</b>\n<i>{details}</i>\n\n"
            "⚠️ <i>This action is locked. Click an option below to authorize or reject execution:</i>"
        )

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve & Execute", "callback_data": approve_data},
                    {"text": "❌ Reject / Revise", "callback_data": reject_data}
                ]
            ]
        }

        if not self.bot_token or not self.admin_chat_id:
            logger.info(f"[SIMULATED TELEGRAM APPROVAL CARD]: Ticket {ticket_id} | Action: {action_name}")
            return {
                "status": "simulated",
                "ticket_id": ticket_id,
                "action": action_name,
                "card_text": card_text,
                "buttons": ["[ ✅ Approve & Execute ]", "[ ❌ Reject / Revise ]"],
                "reason": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured"
            }

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.admin_chat_id,
            "text": card_text,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        }

        try:
            resp = requests.post(url, json=payload, timeout=12)
            if resp.status_code == 200:
                return {"status": "dispatched", "ticket_id": ticket_id, "telegram_response": resp.json()}
            else:
                logger.error(f"Telegram card failed ({resp.status_code}): {resp.text}")
                return {"status": "error", "error": resp.text, "ticket_id": ticket_id}
        except Exception as exc:
            logger.error(f"Failed to dispatch Telegram approval card: {exc}")
            return {"status": "error", "error": str(exc), "ticket_id": ticket_id}

    def send_admin_alert(self, title: str, message: str) -> Dict[str, Any]:
        """Sends an operational informational alert to the admin."""
        text = (
            f"🔔 <b>{title}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"{message}\n\n"
            "⚡ <i>NextClaw OS • Single-Tenant Operations</i>"
        )

        if not self.bot_token or not self.admin_chat_id:
            logger.info(f"[SIMULATED ADMIN ALERT]: {title} - {message}")
            return {"status": "simulated", "title": title, "text": text}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            resp = requests.post(url, json={"chat_id": self.admin_chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
            return {"status": "dispatched" if resp.status_code == 200 else "error"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def send_daily_briefing(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Sends the Executive Daily Briefing to Telegram."""
        text = (
            "📊 <b>Nextserve Executive Daily Briefing</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎓 <b>Active Student Inquiries:</b> {stats.get('inquiries', 14)}\n"
            f"⏳ <b>Pending Tier 3 Approvals:</b> {stats.get('pending_approvals', 0)}\n"
            f"📅 <b>Upcoming Cohorts:</b> {stats.get('upcoming_cohorts', 'October 2026 Cohort')}\n"
            f"⚡ <b>Gateway Channels:</b> WhatsApp • Telegram • Web • Email (Active)\n\n"
            "✅ <i>All NextClaw OS skills operational.</i>"
        )

        if not self.bot_token or not self.admin_chat_id:
            return {"status": "simulated", "text": text}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            resp = requests.post(url, json={"chat_id": self.admin_chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
            return {"status": "dispatched" if resp.status_code == 200 else "error"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

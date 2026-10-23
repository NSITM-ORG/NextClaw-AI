"""Telegram Notification Service for Nextserve AI.

Integrates with Telegram Bot API to send instant alerts and interactive
Human-in-the-Loop approval requests.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables using python-dotenv
# Check for .env in current working directory and repo root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

logger = logging.getLogger("telegram_service")


class TelegramService:
    """Service to interact with Telegram Bot API."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    def is_configured(self) -> bool:
        """Check if bot token and default chat ID are configured."""
        return bool(self.bot_token and self.chat_id)

    def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a message via Telegram Bot API."""
        target_chat_id = chat_id or self.chat_id
        if not self.bot_token or not target_chat_id:
            raise ValueError(
                "Telegram bot token or chat ID is missing. "
                "Ensure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set in .env"
            )

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload: Dict[str, Any] = {
            "chat_id": target_chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        last_exc = None
        for attempt in range(3):
            try:
                response = requests.post(url, json=payload, timeout=20)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, Exception) as exc:
                last_exc = exc
                logger.warning("Telegram sendMessage attempt %d failed: %s. Retrying...", attempt + 1, exc)
                time.sleep(1.0 * (attempt + 1))
        raise last_exc

    def send_registration_alert(
        self,
        student_name: str = "Paschal Okpalaugo",
        course: str = "Full-Stack AI Course",
        registration_id: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends an instant alert notification for a new student registration."""
        reg_id_line = f"🆔 <b>Registration ID:</b> <code>{registration_id}</code>\n" if registration_id else ""
        text = (
            "🎓 <b>New Student Registration Alert</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Student Name:</b> {student_name}\n"
            f"📚 <b>Programme:</b> {course}\n"
            f"{reg_id_line}"
            "⚡ <i>Status:</i> Logged successfully in Nextserve AI."
        )
        return self.send_message(text=text, chat_id=chat_id)

    def send_payment_alert(
        self,
        student_name: str,
        email: str,
        programme: str,
        amount: Any,
        plan_type: str = "Full Payment",
        tranche: Optional[int] = None,
        receipt_url: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an instant alert when a student makes a tuition or instalment payment on the website."""
        tranche_str = f" (Tranche {tranche})" if tranche else ""
        receipt_str = f"🧾 <b>Receipt:</b> <a href='{receipt_url}'>View Receipt</a>\n" if receipt_url else ""
        # Format currency
        if isinstance(amount, (int, float)):
            amount_str = f"₦{amount:,.2f}"
        else:
            amount_str = f"₦{amount}"

        text = (
            "💰 <b>Tuition Payment Received!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Student:</b> {student_name}\n"
            f"📧 <b>Email:</b> <code>{email}</code>\n"
            f"📚 <b>Programme:</b> {programme}\n"
            f"💵 <b>Amount Paid:</b> <b>{amount_str}</b>\n"
            f"💳 <b>Plan:</b> {plan_type}{tranche_str}\n"
            f"{receipt_str}"
            "⚡ <i>Action:</i> Please verify bank transaction in GTBank portal."
        )
        return self.send_message(text=text, chat_id=chat_id)

    def send_partial_enrollment_alert(
        self,
        student_name: str,
        email: str,
        phone: Optional[str] = None,
        programme: Optional[str] = None,
        delivery_format: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an alert when a prospective student starts enrollment (Step 1 lead capture)."""
        phone_str = f"📞 <b>Phone:</b> {phone}\n" if phone else ""
        prog_str = f"📚 <b>Interested Programme:</b> {programme}\n" if programme else ""
        format_str = f"📍 <b>Format:</b> {delivery_format}\n" if delivery_format else ""

        text = (
            "📝 <b>New Enrollment Lead (Step 1 Started)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Name:</b> {student_name}\n"
            f"📧 <b>Email:</b> <code>{email}</code>\n"
            f"{phone_str}"
            f"{prog_str}"
            f"{format_str}"
            "⚡ <i>Status:</i> Student initiated enrollment form on the website."
        )
        return self.send_message(text=text, chat_id=chat_id)

    def send_community_join_alert(
        self,
        name: str,
        email: str,
        role: str,
        portfolio_or_github: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an alert when a developer applies to join the Nextserve Community on the website."""
        port_str = f"🔗 <b>Portfolio/GitHub:</b> {portfolio_or_github}\n" if portfolio_or_github else ""
        text = (
            "🚀 <b>New Developer Community Application</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Name:</b> {name}\n"
            f"📧 <b>Email:</b> <code>{email}</code>\n"
            f"💻 <b>Role:</b> {role}\n"
            f"{port_str}"
            "⚡ <i>Status:</i> Submitted via website homepage community portal."
        )
        return self.send_message(text=text, chat_id=chat_id)

    def send_website_chat_alert(
        self,
        visitor_query: str,
        bot_response: str,
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an alert when a visitor engages with the website AI chatbot."""
        text = (
            "💬 <b>Website Chatbot Interaction</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"❓ <b>Visitor Asked:</b> <i>\"{visitor_query[:180]}\"</i>\n"
            f"🤖 <b>NextClaw Replied:</b> {bot_response[:220]}...\n"
            "⚡ <i>Channel:</i> Live Website Chat Widget"
        )
        return self.send_message(text=text, chat_id=chat_id)

    def send_approval_request(
        self,
        title: str = "Draft Student Notification Email",
        details: str = "Email draft prepared for enrolled student regarding course orientation schedule.",
        request_id: Optional[str] = None,
        approve_callback_data: Optional[str] = None,
        reject_callback_data: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends an interactive Human-in-the-Loop approval request with inline buttons."""
        req_id = request_id or "REQ-7311"
        approve_cb = approve_callback_data or f"approve_{req_id}"
        reject_cb = reject_callback_data or f"reject_{req_id}"

        text = (
            "⚠️ <b>Level 3 Human-in-the-Loop Approval Required</b>\n\n"
            f"📋 <b>Action:</b> {title}\n"
            f"📝 <b>Details:</b> {details}\n"
            f"🔑 <b>Request ID:</b> <code>{req_id}</code>\n\n"
            "Please review and choose an action below:"
        )

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": approve_cb},
                    {"text": "❌ Reject", "callback_data": reject_cb},
                ]
            ]
        }

        return self.send_message(text=text, chat_id=chat_id, reply_markup=reply_markup)

    def send_daily_summary(
        self,
        total_students: int,
        pending_approvals: int,
        agent_health: Optional[Dict[str, str]] = None,
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an Executive Daily Summary Briefing to Telegram."""
        agents = agent_health or {
            "School Agent": "Operational",
            "Website Agent": "Operational",
        }
        agents_text = "\n".join([f"  • <b>{k}:</b> <code>{v}</code>" for k, v in agents.items()])

        text = (
            "📊 <b>Nextserve Executive Daily Briefing</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎓 <b>Total Registered Students:</b> {total_students}\n"
            f"⏳ <b>Pending Level 3 Approvals:</b> {pending_approvals} tickets\n"
            f"⚡ <b>Database Engine:</b> PostgreSQL 16 (pgvector active)\n\n"
            "🤖 <b>Specialist Agent Status:</b>\n"
            f"{agents_text}\n\n"
            "✅ <i>All core systems and workflows are running optimally.</i>"
        )
        return self.send_message(text=text, chat_id=chat_id)

    def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = "Decision recorded!",
        show_alert: bool = False,
    ) -> Dict[str, Any]:
        """Acknowledge a Telegram button callback query."""
        if not self.bot_token:
            raise ValueError("Telegram bot token is missing.")
        url = f"https://api.telegram.org/bot{self.bot_token}/answerCallbackQuery"
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
        }
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()

    def edit_message_text(
        self,
        text: str,
        chat_id: Optional[str] = None,
        message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """Edit an existing message text in Telegram chat."""
        target_chat_id = chat_id or self.chat_id
        if not self.bot_token or not target_chat_id or not message_id:
            return self.send_message(text=text, chat_id=target_chat_id, parse_mode=parse_mode)

        url = f"https://api.telegram.org/bot{self.bot_token}/editMessageText"
        payload = {
            "chat_id": target_chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        # Fallback: send as a new message if editing fails
        return self.send_message(text=text, chat_id=target_chat_id, parse_mode=parse_mode)


# Global default instance
telegram_service = TelegramService()


def send_registration_alert(
    student_name: str = "Paschal Okpalaugo",
    course: str = "Full-Stack AI Course",
    registration_id: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Module-level helper to send a registration alert."""
    return telegram_service.send_registration_alert(
        student_name=student_name,
        course=course,
        registration_id=registration_id,
        chat_id=chat_id,
    )


def send_approval_request(
    title: str = "Draft Student Notification Email",
    details: str = "Email draft prepared for enrolled student regarding course orientation schedule.",
    request_id: Optional[str] = None,
    approve_callback_data: Optional[str] = None,
    reject_callback_data: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Module-level helper to send an interactive approval request."""
    return telegram_service.send_approval_request(
        title=title,
        details=details,
        request_id=request_id,
        approve_callback_data=approve_callback_data,
        reject_callback_data=reject_callback_data,
        chat_id=chat_id,
    )


def send_daily_summary(
    total_students: int,
    pending_approvals: int,
    agent_health: Optional[Dict[str, str]] = None,
    chat_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Module-level helper to send an executive daily summary briefing."""
    return telegram_service.send_daily_summary(
        total_students=total_students,
        pending_approvals=pending_approvals,
        agent_health=agent_health,
        chat_id=chat_id,
    )

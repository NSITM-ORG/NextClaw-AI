"""Gmail Live Service for Nextserve AI.

Provides live integration with Gmail:
- fetch_latest_unread() using imaplib and email parser
- generate_reply_draft(sender, subject, body) to construct AI assistant response drafts
- send_email(to_email, subject, body) using smtplib with STARTTLS on smtp.gmail.com:587
- In-memory/persistent store for pending approval drafts keyed by short tokens
"""

import os
import re
import uuid
import imaplib
import smtplib
import logging
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from app.core.config import settings

logger = logging.getLogger("gmail_service")

# Global in-memory draft cache for Human-in-the-Loop approvals
# Maps short draft_id -> draft details
_PENDING_DRAFTS: Dict[str, Dict[str, Any]] = {}


def _decode_header_value(header_val: Optional[str]) -> str:
    """Safely decode an RFC 2047 email header string."""
    if not header_val:
        return ""
    decoded_fragments = []
    for fragment, encoding in decode_header(header_val):
        if isinstance(fragment, bytes):
            charset = encoding or "utf-8"
            try:
                decoded_fragments.append(fragment.decode(charset, errors="replace"))
            except (LookupError, UnicodeDecodeError):
                decoded_fragments.append(fragment.decode("utf-8", errors="replace"))
        else:
            decoded_fragments.append(str(fragment))
    return "".join(decoded_fragments).strip()


def _extract_email_address(from_str: str) -> Tuple[str, str]:
    """Extract display name and pure email address from a 'From' header string.
    
    Example: 'John Doe <john@example.com>' -> ('John Doe', 'john@example.com')
    """
    match = re.search(r"<([^>]+)>", from_str)
    if match:
        email_addr = match.group(1).strip()
        display_name = from_str[:match.start()].strip().strip("\"'")
        return display_name or email_addr.split("@")[0], email_addr
    email_addr = from_str.strip().strip("\"'")
    return email_addr.split("@")[0] if "@" in email_addr else email_addr, email_addr


class GmailService:
    """Service to interact with Gmail via IMAP and SMTP."""

    def __init__(
        self,
        user: Optional[str] = None,
        app_password: Optional[str] = None,
        imap_server: Optional[str] = None,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
    ):
        self.user = user or os.getenv("GMAIL_USER") or getattr(settings, "GMAIL_USER", "chigbookpalaugo@gmail.com")
        self.app_password = app_password or os.getenv("GMAIL_APP_PASSWORD") or getattr(settings, "GMAIL_APP_PASSWORD", None)
        self.imap_server = imap_server or getattr(settings, "GMAIL_IMAP_SERVER", "imap.gmail.com")
        self.smtp_server = smtp_server or getattr(settings, "GMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = smtp_port or getattr(settings, "GMAIL_SMTP_PORT", 587)

    def is_configured(self) -> bool:
        """Check if Gmail credentials are provided."""
        return bool(self.user and self.app_password)

    def fetch_latest_unread(self, mark_as_read: bool = False) -> Optional[Dict[str, Any]]:
        """Connects to Gmail via IMAP and retrieves the latest unread email.

        Args:
            mark_as_read: If True, marks the email as read in Gmail. Defaults to False.

        Returns:
            Dictionary containing email details (id, sender, sender_name, subject, date, body),
            or None if no unread messages are found.
        """
        if not self.is_configured():
            raise ValueError(
                "Gmail credentials missing. Ensure GMAIL_USER and GMAIL_APP_PASSWORD are set in .env"
            )

        last_error = None
        raw_email_bytes = None
        latest_id_val = None

        for attempt in range(1, 4):
            mail = None
            try:
                logger.info("Connecting to Gmail IMAP at %s:993 (Attempt %d)...", self.imap_server, attempt)
                mail = imaplib.IMAP4_SSL(self.imap_server, 993)
                mail.login(self.user, self.app_password)
                mail.select("INBOX")

                status, response = mail.search(None, "UNSEEN")
                if status != "OK":
                    logger.warning("Failed to search UNSEEN emails: status %s", status)
                    return None

                email_ids = response[0].split()
                if not email_ids:
                    logger.info("No unread emails found in INBOX for %s", self.user)
                    return None

                latest_id = email_ids[-1]
                latest_id_val = latest_id.decode("utf-8") if isinstance(latest_id, bytes) else str(latest_id)
                fetch_cmd = "(RFC822)" if mark_as_read else "(BODY.PEEK[])"
                res_status, msg_data = mail.fetch(latest_id, fetch_cmd)
                if res_status != "OK" or not msg_data:
                    logger.warning("Failed to fetch email ID %s", latest_id)
                    return None

                for part in msg_data:
                    if isinstance(part, tuple) and len(part) >= 2:
                        raw_email_bytes = part[1]
                        break

                if raw_email_bytes:
                    break
            except Exception as e:
                last_error = e
                logger.warning("IMAP fetch attempt %d encountered error: %s", attempt, e)
                if attempt < 3:
                    import time
                    time.sleep(2.0 * attempt)
            finally:
                if mail:
                    try:
                        mail.close()
                    except Exception:
                        pass
                    try:
                        mail.logout()
                    except Exception:
                        pass

        if not raw_email_bytes:
            if last_error:
                logger.error("Error fetching unread email from Gmail after retries: %s", last_error)
                raise last_error
            return None

        try:
            msg = email.message_from_bytes(raw_email_bytes)

            raw_from = _decode_header_value(msg.get("From", ""))
            sender_name, sender_email = _extract_email_address(raw_from)
            subject = _decode_header_value(msg.get("Subject", "(No Subject)"))
            date_str = msg.get("Date", "")

            # Extract body
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition") or "")
                    if "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            try:
                                decoded_content = payload.decode(charset, errors="replace")
                            except Exception:
                                decoded_content = payload.decode("utf-8", errors="replace")
                            if content_type == "text/plain":
                                body_text = decoded_content
                                break
                            elif content_type == "text/html" and not body_text:
                                body_text = re.sub(r"<[^>]+>", " ", decoded_content)
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    try:
                        body_text = payload.decode(charset, errors="replace")
                    except Exception:
                        body_text = payload.decode("utf-8", errors="replace")

            body_cleaned = " ".join(body_text.strip().split()) if body_text else "(No body content)"
            preview = body_cleaned[:1000] if len(body_cleaned) <= 1000 else body_cleaned[:997] + "..."

            email_details = {
                "id": latest_id_val,
                "sender": sender_email,
                "sender_name": sender_name,
                "raw_sender": raw_from,
                "subject": subject,
                "date": date_str,
                "body": body_cleaned,
                "body_preview": preview,
            }
            logger.info("Successfully fetched unread email from: %s | Subject: %s", sender_email, subject)
            return email_details

        except Exception as e:
            logger.error("Error parsing email message: %s", e)
            raise

    def generate_reply_draft(
        self,
        sender: str,
        subject: str,
        body: str,
        sender_name: Optional[str] = None,
    ) -> Dict[str, str]:
        """Constructs an AI/templated draft response for Nextserve AI Assistant.

        Args:
            sender: Recipient email address
            subject: Original email subject
            body: Original email content
            sender_name: Display name of the sender

        Returns:
            Dict containing to_email, subject, and draft body
        """
        name = sender_name or _extract_email_address(sender)[0] or "Student / Inquirer"
        reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"

        # Contextual response drafting
        greeting = f"Hello {name},"
        closing = (
            "Best regards,\n"
            "NextClaw (Nextserve AI Operational Assistant)\n"
            "Nextserve Education Inc."
        )

        body_lower = body.lower()
        if any(term in body_lower for term in ["enroll", "register", "admission", "course", "fee"]):
            content = (
                "Thank you for contacting Nextserve regarding course enrollment and admissions.\n\n"
                "NextClaw has received your inquiry and our academic admissions team is actively reviewing your request. "
                "All course orientations, schedules, and curriculum details are synchronized with our "
                "student portal.\n\n"
                "If you need immediate verification of your profile credentials, please feel free to "
                "reply directly to this email."
            )
        elif any(term in body_lower for term in ["schedule", "meeting", "call", "time", "orientation"]):
            content = (
                "Thank you for reaching out regarding the schedule.\n\n"
                "Our orientation sessions take place weekly on Monday at 10:00 AM UTC via the Nextserve "
                "Student Portal. A confirmation invite with complete video link credentials will be "
                "delivered to your inbox."
            )
        else:
            content = (
                f"Thank you for reaching out to Nextserve.\n\n"
                f"NextClaw has logged your inquiry: \"{body[:120]}{'...' if len(body) > 120 else ''}\".\n\n"
                "Our operational assistance pipeline has recorded your ticket and an advisor will follow up "
                "with full details shortly."
            )

        draft_body = f"{greeting}\n\n{content}\n\n{closing}"

        return {
            "to_email": sender,
            "subject": reply_subject,
            "body": draft_body,
        }

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an email using smtplib via smtp.gmail.com:587 with STARTTLS.

        Args:
            to_email: Destination email address
            subject: Subject line
            body: Plain text content
            html_body: Optional HTML formatted content

        Returns:
            Dict with delivery confirmation details
        """
        if not self.is_configured():
            raise ValueError(
                "Gmail credentials missing. Ensure GMAIL_USER and GMAIL_APP_PASSWORD are set in .env"
            )

        logger.info("Connecting to Gmail SMTP at %s:%d...", self.smtp_server, self.smtp_port)
        server = None
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"NextClaw Operational Assistant <{self.user}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg["Date"] = email.utils.formatdate(localtime=True)
            msg["Message-ID"] = email.utils.make_msgid(domain="gmail.com")

            part_text = MIMEText(body, "plain", "utf-8")
            msg.attach(part_text)

            if html_body:
                part_html = MIMEText(html_body, "html", "utf-8")
                msg.attach(part_html)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=25)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.user, self.app_password)
            server.send_message(msg)

            logger.info("Email dispatched successfully to %s via %s", to_email, self.user)
            return {
                "status": "sent",
                "to": to_email,
                "sender": self.user,
                "subject": subject,
                "message_id": msg["Message-ID"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error("Failed to send email to %s via Gmail SMTP: %s", to_email, e)
            raise
        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass


# Singleton instance
gmail_service = GmailService()


# Store and retrieval helpers for Human-in-the-Loop pending drafts
def store_pending_draft(draft_id: str, draft_data: Dict[str, Any]) -> str:
    """Save a pending draft by ID."""
    _PENDING_DRAFTS[draft_id] = draft_data
    return draft_id


def get_pending_draft(draft_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a pending draft by ID."""
    return _PENDING_DRAFTS.get(draft_id)


def pop_pending_draft(draft_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve and delete a pending draft by ID."""
    return _PENDING_DRAFTS.pop(draft_id, None)


def create_and_store_draft(
    sender: str,
    subject: str,
    body: str,
    sender_name: Optional[str] = None,
    email_uid: Optional[str] = None,
    received_date: Optional[str] = None,
) -> Tuple[str, Dict[str, str]]:
    """Convenience helper: generates draft, creates short ID, registers in store and saves to PostgreSQL."""
    token = f"d_{uuid.uuid4().hex[:8]}"
    draft = gmail_service.generate_reply_draft(
        sender=sender,
        subject=subject,
        body=body,
        sender_name=sender_name,
    )
    draft_record = {
        "id": token,
        "sender": sender,
        "sender_name": sender_name,
        "subject": draft["subject"],
        "body": draft["body"],
        "email_uid": email_uid,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store_pending_draft(token, draft_record)

    # Persist into PostgreSQL emails table with Status='PENDING'
    try:
        from app.services.email_repository import email_repository
        email_repository.save_incoming_email(
            sender=sender,
            subject=subject,
            body=body,
            received_date=received_date,
            sender_name=sender_name,
            email_uid=email_uid,
            token=token,
        )
    except Exception as exc:
        logger.warning("Could not persist incoming email to DB in create_and_store_draft: %s", exc)

    return token, draft


def format_telegram_approval_card(
    sender: str,
    subject: str,
    body: str,
    draft_body: str,
    token: str,
    sender_name: Optional[str] = None,
    is_simulated: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """Constructs HTML text and inline keyboard markup for a Telegram approval card.

    - Truncates long body previews to max 1,000 characters.
    - Provides [✅ Approve & Send] and [❌ Reject] action buttons.
    """
    import html

    header = (
        "📬 <b>🧪 SIMULATED INCOMING EMAIL INQUIRY</b>"
        if is_simulated
        else "📬 <b>🔴 LIVE UNREAD EMAIL RECEIVED</b>"
    )
    safe_name = html.escape(str(sender_name or sender))
    safe_sender = html.escape(str(sender))
    safe_subject = html.escape(str(subject))

    # Truncate long body previews for Telegram cards (max 1,000 chars)
    raw_preview = body[:1000] if len(body) <= 1000 else body[:997] + "..."
    safe_preview = html.escape(raw_preview)
    safe_draft = html.escape(str(draft_body))

    telegram_text = (
        f"{header}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>From:</b> {safe_name} (<code>{safe_sender}</code>)\n"
        f"📌 <b>Subject:</b> <i>{safe_subject}</i>\n\n"
        f"💬 <b>Message Preview:</b>\n"
        f"<i>{safe_preview}</i>\n\n"
        "🤖 <b>Proposed NextClaw (Nextserve AI Operational Assistant) Reply:</b>\n"
        f"<pre>{safe_draft}</pre>\n\n"
        f"🔑 <b>Approval Token:</b> <code>{token}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Tap an option below to approve or cancel email dispatch:</i>"
    )

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve & Send", "callback_data": f"approve_{token}"},
                {"text": "❌ Reject", "callback_data": f"reject_{token}"},
            ]
        ]
    }

    return telegram_text, reply_markup


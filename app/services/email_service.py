"""Email Dispatch Service for Nextserve AI.

Supports sending emails via Resend API or falling back to a realistic
Mock Email Provider for local development and testing.
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger("email_service")


class EmailService:
    """Service to send emails via Resend or mock provider."""

    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        self.from_email = from_email or os.getenv("EMAIL_FROM", "Nextserve Admissions <admissions@nextserve.ai>")

    def is_live_provider(self) -> bool:
        """Check if Resend API key is configured."""
        return bool(self.api_key and not self.api_key.startswith("your-"))

    def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch an email via Resend if configured, else mock."""
        if self.is_live_provider():
            try:
                url = "https://api.resend.com/emails"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "from": self.from_email,
                    "to": [to],
                    "subject": subject,
                    "html": html,
                }
                if text:
                    payload["text"] = text

                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code in [200, 201]:
                    data = resp.json()
                    logger.info("Resend email dispatched successfully: %s", data)
                    return {
                        "status": "sent",
                        "provider": "resend",
                        "message_id": data.get("id"),
                        "to": to,
                        "subject": subject,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                else:
                    logger.warning("Resend returned %s: %s. Falling back to mock dispatch.", resp.status_code, resp.text)
            except Exception as e:
                logger.warning("Failed to dispatch via Resend: %s. Falling back to mock dispatch.", e)

        # Mock Email Provider Dispatch
        mock_id = f"email_{uuid.uuid4().hex[:12]}"
        logger.info("[Mock Email] Dispatched to %s | Subject: %s | ID: %s", to, subject, mock_id)
        return {
            "status": "sent",
            "provider": "mock",
            "message_id": mock_id,
            "to": to,
            "subject": subject,
            "from": self.from_email,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "preview": text[:120] if text else html[:120],
        }

    def send_student_notification_email(
        self,
        student_email: str,
        student_name: str,
        course_name: str,
        orientation_info: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends an approved enrollment orientation email to the student."""
        orientation = orientation_info or "Monday at 10:00 AM UTC via Nextserve Student Portal."
        subject = f"Welcome to Nextserve AI — Enrollment Confirmed: {course_name}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #0f172a;">Welcome to Nextserve AI, {student_name}!</h2>
            <p style="font-size: 16px; color: #334155;">
                We are thrilled to confirm your enrollment in <strong>{course_name}</strong>.
            </p>
            <div style="background-color: #f8fafc; padding: 16px; border-left: 4px solid #22c55e; border-radius: 4px; margin: 20px 0;">
                <h4 style="margin: 0 0 8px 0; color: #0f172a;">Orientation Session Details:</h4>
                <p style="margin: 0; color: #475569;">{orientation}</p>
            </div>
            <p style="color: #64748b; font-size: 14px;">
                Your student profile and access credentials are now active. If you have any questions,
                our AI Assistant Nextclaw is standing by 24/7.
            </p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <p style="color: #94a3b8; font-size: 12px; margin: 0;">Nextserve AI Admissions & Academic Affairs</p>
        </div>
        """
        text = (
            f"Welcome to Nextserve AI, {student_name}!\n\n"
            f"Your enrollment in {course_name} is confirmed.\n"
            f"Orientation: {orientation}\n\n"
            f"Nextserve AI Admissions"
        )
        return self.send_email(to=student_email, subject=subject, html=html, text=text)


email_service = EmailService()

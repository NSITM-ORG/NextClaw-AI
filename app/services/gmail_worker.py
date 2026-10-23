"""Continuous NextClaw Gmail Worker.

Polls Gmail via IMAP every 20 seconds:
- Offloads blocking IMAP checks and persistence calls to worker threads via asyncio.to_thread.
- Automatically handles IMAP socket timeouts and connection errors with graceful retry.
- Uses BODY.PEEK[] to preserve inbox unread state.
- Deduplicates using an in-memory UID cache and PostgreSQL queries.
- Persists unread emails to PostgreSQL as PENDING.
- Formats draft reply signed by NextClaw (Nextserve AI Operational Assistant).
- Dispatches interactive Telegram card with truncated preview (max 1,000 chars)
  and [✅ Approve & Send] / [❌ Reject] action buttons.
"""

import os
import socket
import imaplib
import logging
import asyncio
from typing import Optional, Dict, Any, Set

from app.services.gmail_service import (
    gmail_service,
    create_and_store_draft,
    format_telegram_approval_card,
    GmailService,
)
from app.services.telegram_service import telegram_service
from app.services.email_repository import email_repository

logger = logging.getLogger("gmail_worker")


class GmailWorker:
    """Continuous background worker polling Gmail for unread messages."""

    def __init__(
        self,
        service: Optional[GmailService] = None,
        poll_interval: float = 20.0,
    ):
        self.service = service or gmail_service
        self.poll_interval = poll_interval
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None
        self._processed_uids: Set[str] = set()

    @property
    def is_running(self) -> bool:
        """Indicates whether the worker loop is currently active."""
        return self._running

    async def start(self) -> None:
        """Start the background polling task via asyncio.create_task."""
        if self._running:
            logger.warning("GmailWorker is already running.")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="nextclaw_gmail_worker")
        logger.info(
            "NextClaw GmailWorker started (polling every %s seconds).",
            self.poll_interval,
        )

    async def stop(self) -> None:
        """Cleanly cancel and stop the background polling task."""
        if not self._running:
            return

        logger.info("Stopping NextClaw GmailWorker...")
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("NextClaw GmailWorker stopped cleanly.")

    async def _run_loop(self) -> None:
        """Continuous polling loop running every poll_interval seconds."""
        logger.info("GmailWorker continuous loop initiated.")
        while self._running:
            try:
                await self.check_once()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Unexpected error in GmailWorker tick: %s", exc, exc_info=True)

            try:
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break

    async def check_once(self) -> Optional[Dict[str, Any]]:
        """Single check cycle, offloading synchronous IMAP/DB/Telegram work to a thread."""
        if not self.service.is_configured():
            logger.debug("GmailService credentials not configured. Skipping poll tick.")
            return None

        # Offload synchronous IMAP / database / network operations
        return await asyncio.to_thread(self._sync_check_and_process)

    def _sync_check_and_process(self) -> Optional[Dict[str, Any]]:
        """Synchronous check logic with auto-reconnect on IMAP socket timeouts."""
        unread = None
        try:
            # fetch_latest_unread uses BODY.PEEK[] when mark_as_read=False
            unread = self.service.fetch_latest_unread(mark_as_read=False)
        except (socket.timeout, TimeoutError, OSError) as sock_err:
            logger.warning(
                "IMAP socket timeout encountered during Gmail check: %s. Auto-reconnecting on next cycle.",
                sock_err,
            )
            return None
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error) as imap_err:
            logger.warning(
                "IMAP protocol error or connection abort: %s. Auto-reconnecting on next cycle.",
                imap_err,
            )
            return None
        except Exception as exc:
            logger.error("Failed to check unread emails via Gmail IMAP: %s", exc)
            return None

        if not unread:
            return None

        email_uid = str(unread.get("id") or "")
        # Prevent re-alerting on the same unread email
        if email_uid and email_uid in self._processed_uids:
            return None

        # Check if already registered in PostgreSQL database
        try:
            existing_record = email_repository.get_email_by_uid(email_uid)
            if existing_record:
                self._processed_uids.add(email_uid)
                return None
        except Exception as db_err:
            logger.warning("Database lookup for email UID %s error: %s", email_uid, db_err)

        # Generate draft, register token, and persist to PostgreSQL with status 'PENDING'
        sender = unread.get("sender", "")
        subject = unread.get("subject", "")
        body = unread.get("body", "")
        sender_name = unread.get("sender_name")
        received_date = unread.get("date")

        token, draft = create_and_store_draft(
            sender=sender,
            subject=subject,
            body=body,
            sender_name=sender_name,
            email_uid=email_uid,
            received_date=received_date,
        )

        if email_uid:
            self._processed_uids.add(email_uid)

        # Format Telegram card with max 1,000 char preview and action buttons
        telegram_text, reply_markup = format_telegram_approval_card(
            sender=sender,
            subject=subject,
            body=body,
            draft_body=draft.get("body", ""),
            token=token,
            sender_name=sender_name,
            is_simulated=False,
        )

        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        tg_res = None
        try:
            tg_res = telegram_service.send_message(
                text=telegram_text,
                chat_id=chat_id,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            logger.info("Forwarded email %s to Telegram with approval token %s", email_uid, token)
        except Exception as tg_err:
            logger.error("Failed to forward email card to Telegram: %s", tg_err)

        return {
            "status": "processed",
            "email_uid": email_uid,
            "sender": sender,
            "token": token,
            "telegram_response": tg_res,
        }


# Global singleton instance
gmail_worker = GmailWorker()

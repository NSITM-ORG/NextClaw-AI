"""Continuous Telegram Bot Worker for NextClaw.

Runs as a background asyncio task:
- Long-polls Telegram for updates via getUpdates.
- Dispatches button clicks to handle_approval_callback ([✅ Approve & Send] / [❌ Reject]).
- Dispatches conversational text messages to handle_telegram_message so anyone
  can talk to NextClaw in real-time on Telegram without needing a public tunnel or webhook!
"""

import os
import logging
import asyncio
import requests
from typing import Optional

from app.services.telegram_service import telegram_service
from app.routers.telegram import handle_approval_callback, handle_telegram_message

logger = logging.getLogger("telegram_bot_worker")


class TelegramBotWorker:
    """Continuous polling worker for interactive Telegram bot messages & button callbacks."""

    def __init__(self, bot_token: Optional[str] = None, poll_interval: float = 1.0):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.poll_interval = poll_interval
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None
        self._last_offset: int = 0

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self) -> None:
        """Starts the background polling listener."""
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN missing; TelegramBotWorker will not start.")
            return

        if self._running:
            return

        self._running = True
        # Clear any external webhook to ensure Telegram routes updates to getUpdates polling
        await asyncio.to_thread(self._clear_webhook)
        self._task = asyncio.create_task(self._run_loop(), name="nextclaw_telegram_bot_worker")
        logger.info("NextClaw TelegramBotWorker started (real-time chat & callbacks enabled).")

    def _clear_webhook(self):
        """Clears Telegram webhook to enable local getUpdates polling."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook"
            requests.get(url, timeout=10)
            logger.info("Telegram webhook cleared for local real-time polling.")
        except Exception as exc:
            logger.warning("Could not clear Telegram webhook: %s", exc)

    async def stop(self) -> None:
        """Stops the background polling listener cleanly."""
        if not self._running:
            return

        logger.info("Stopping NextClaw TelegramBotWorker...")
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("NextClaw TelegramBotWorker stopped cleanly.")

    async def _run_loop(self) -> None:
        """Continuous polling loop."""
        while self._running:
            try:
                await self._poll_and_process()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Error in TelegramBotWorker loop: %s", exc)

            try:
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break

    async def _poll_and_process(self) -> None:
        """Fetch updates from Telegram and dispatch to handlers."""
        updates = await asyncio.to_thread(self._fetch_updates)
        if not updates:
            return

        for update in updates:
            self._last_offset = update.get("update_id", 0) + 1

            # 1. Handle Inline Button Click (Approvals)
            cb = update.get("callback_query")
            if cb:
                try:
                    handle_approval_callback(
                        callback_data=cb.get("data", ""),
                        callback_query_id=cb.get("id"),
                        chat_id=cb.get("message", {}).get("chat", {}).get("id"),
                        message_id=cb.get("message", {}).get("message_id"),
                        reviewer_name=cb.get("from", {}).get("first_name", "Telegram Admin"),
                    )
                except Exception as cb_err:
                    logger.warning("Error processing Telegram callback: %s", cb_err)
                continue

            # 2. Handle Text Chat Message (Real-Time Conversation)
            msg = update.get("message")
            if msg and "text" in msg:
                try:
                    await handle_telegram_message(msg)
                except Exception as msg_err:
                    logger.warning("Error processing Telegram text message: %s", msg_err)

    def _fetch_updates(self):
        """Synchronous fetch from Telegram API."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {"offset": self._last_offset, "timeout": 2}
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("result", [])
        except Exception:
            pass
        return []


# Global singleton instance
telegram_bot_worker = TelegramBotWorker()

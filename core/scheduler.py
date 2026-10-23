"""NextClaw OS - Background Event Scheduler (core/scheduler.py).

Background asyncio worker for:
- Monitoring school events, cohort kick-offs, and masterclasses.
- Triggering pre-event push and WhatsApp reminders before upcoming events.
- Dispatching scheduled executive briefings to Admin Telegram.
"""

import asyncio
import logging
from typing import Optional

from skills import skill_registry
from skills.skill_messaging import MessagingSkill

logger = logging.getLogger("nextclaw.scheduler")


class BackgroundScheduler:
    """Async background task runner for automated event reminders and health checks."""

    def __init__(self, check_interval_seconds: int = 3600):
        self.check_interval = check_interval_seconds
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None
        self.messaging = MessagingSkill()

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self):
        """Starts the background event scheduler loop."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="nextclaw_os_scheduler")
        logger.info("NextClaw OS BackgroundScheduler started successfully.")

    async def stop(self):
        """Stops the scheduler gracefully."""
        if not self._running:
            return

        logger.info("Stopping NextClaw OS BackgroundScheduler...")
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("NextClaw OS BackgroundScheduler stopped.")

    async def _run_loop(self):
        """Continuous event monitoring loop."""
        while self._running:
            try:
                await self.run_check_cycle()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Error in scheduler check cycle: {exc}")

            try:
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break

    async def run_check_cycle(self):
        """Executes a single reminder evaluation cycle."""
        cal_skill = skill_registry.get_skill("skill_calendar")
        if not cal_skill:
            return

        # Check for events starting within next 48 hours
        res = cal_skill.execute("check_reminders", {"window_hours": 48})
        reminders = res.get("reminders", [])

        if reminders:
            logger.info(f"Scheduler found {len(reminders)} upcoming event reminder(s) to dispatch.")
            for rem in reminders:
                msg_text = rem.get("whatsapp_message")
                logger.info(f"[TRIGGERED EVENT REMINDER]: {rem.get('event_title')} in {rem.get('hours_until')}h")
                # Dispatch alert to Admin Telegram channel
                tg_skill = skill_registry.get_skill("skill_telegram")
                if tg_skill:
                    tg_skill.execute("send_alert", {
                        "title": f"Pre-Event Reminder Triggered: {rem.get('event_title')}",
                        "message": f"Event begins in {rem.get('hours_until')} hours ({rem.get('formatted_date')}). Reminders prepared for enrolled cohorts."
                    })


scheduler = BackgroundScheduler(check_interval_seconds=3600)

"""NextClaw OS - Calendar & Event Notification Skill (skill_calendar.py).

Manages school events, cohort start dates, webinars, and exam schedules.
Automatically schedules and triggers push/WhatsApp reminders before upcoming events.
Execution Tier: TIER 1 (Read / Query) | TIER 2 (Draft New Events).
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

from skills import BaseSkill

logger = logging.getLogger("nextclaw.skills.calendar")


DEFAULT_EVENTS_FILE = Path(__file__).resolve().parent.parent / "configs" / "CALENDAR.json"


class CalendarSkill(BaseSkill):
    """Manages academic calendar, cohort intakes, masterclasses, and automated pre-event notifications."""

    name: str = "skill_calendar"
    tier: int = 1
    description: str = "Academic calendar manager and automated event reminder trigger generator."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.events_file = DEFAULT_EVENTS_FILE
        self._events: List[Dict[str, Any]] = []
        self._init_calendar()

    def _init_calendar(self):
        """Initializes or loads default Nextserve academic calendar events."""
        if self.events_file.exists():
            try:
                with open(self.events_file, "r", encoding="utf-8") as f:
                    self._events = json.load(f)
                return
            except Exception as err:
                logger.warning(f"Could not load calendar from {self.events_file}: {err}")

        # Seed realistic upcoming Nextserve events
        now = datetime.now(timezone.utc)
        self._events = [
            {
                "id": "EVT-2026-OCT-ORIENT",
                "title": "Nextserve October Cohort Orientation Webinar",
                "type": "webinar",
                "target_programmes": ["All Programmes"],
                "start_time": (now + timedelta(days=2, hours=4)).isoformat(),
                "duration_minutes": 90,
                "location": "Live Zoom & YouTube Stream",
                "link": "https://nextserveschool.com/orientation-live",
                "description": "Meet faculty directors, review curriculum roadmaps, and understand LMS access.",
                "reminders_sent": []
            },
            {
                "id": "EVT-2026-OCT-COHORT",
                "title": "October 2026 Cohort Official Kick-Off",
                "type": "cohort_start",
                "target_programmes": ["Fullstack Web Development", "AI & LLM Engineering", "Cybersecurity"],
                "start_time": (now + timedelta(days=9)).isoformat(),
                "duration_minutes": 180,
                "location": "Lagos Hub Campus & Virtual Classroom",
                "link": "https://lms.nextserveschool.com",
                "description": "Day 1 lectures, Git/GitHub setup, and development environment onboarding.",
                "reminders_sent": []
            },
            {
                "id": "EVT-2026-AI-MASTERCLASS",
                "title": "Hands-On Generative AI & Autonomous Agents Masterclass",
                "type": "masterclass",
                "target_programmes": ["AI & LLM Engineering", "Tech Development Track"],
                "start_time": (now + timedelta(days=16)).isoformat(),
                "duration_minutes": 120,
                "location": "Online Live Interactive",
                "link": "https://nextserveschool.com/masterclass/ai-agents",
                "description": "Building production RAG and agentic workflows with LangGraph and PostgreSQL.",
                "reminders_sent": []
            },
            {
                "id": "EVT-2026-CAPSTONE-DEF",
                "title": "Q3 Capstone Project Defense & Demo Day",
                "type": "exam",
                "target_programmes": ["Graduating Tech Cohort"],
                "start_time": (now + timedelta(days=25)).isoformat(),
                "duration_minutes": 240,
                "location": "Lagos Hub & Virtual Stage",
                "link": "https://nextserveschool.com/demoday",
                "description": "Final portfolio project presentations before tech hiring partners.",
                "reminders_sent": []
            }
        ]
        self._save_events()

    def _save_events(self):
        """Persists events list to JSON file."""
        try:
            with open(self.events_file, "w", encoding="utf-8") as f:
                json.dump(self._events, f, indent=2)
        except Exception as exc:
            logger.error(f"Error saving events to {self.events_file}: {exc}")

    def execute(self, action: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes calendar actions."""
        if action in ["list_events", "get_events", "calendar"]:
            return self.get_upcoming_events(days_ahead=int(params.get("days_ahead", 30)))

        elif action in ["get_next_cohort", "cohort"]:
            return self.get_next_cohort()

        elif action in ["schedule_event", "create_event", "add_event"]:
            # Tier 2: Draft & Review action
            return self.schedule_event(
                title=params.get("title", "Nextserve Academic Session"),
                event_type=params.get("type", "lecture"),
                start_time=params.get("start_time"),
                location=params.get("location", "Online"),
                description=params.get("description", "")
            )

        elif action in ["trigger_reminders", "check_reminders"]:
            window_hours = int(params.get("window_hours", 48))
            return self.check_and_trigger_reminders(window_hours=window_hours)

        elif action in ["send_telegram_notification", "notify_telegram", "send_telegram"]:
            chat_id = params.get("chat_id")
            return self.send_calendar_telegram_notification(chat_id=chat_id)

        else:
            return {
                "status": "error",
                "message": f"Unknown calendar action '{action}'. Valid actions: list_events, get_next_cohort, schedule_event, trigger_reminders, send_telegram_notification"
            }

    def get_upcoming_events(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Returns verified school events happening within the specified window."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=days_ahead)

        upcoming = []
        for e in self._events:
            try:
                evt_time = datetime.fromisoformat(e["start_time"])
                if evt_time.tzinfo is None:
                    evt_time = evt_time.replace(tzinfo=timezone.utc)
                if now <= evt_time <= cutoff:
                    days_left = (evt_time - now).days
                    hours_left = int((evt_time - now).total_seconds() // 3600)
                    upcoming.append({
                        **e,
                        "time_until": f"in {days_left} days ({hours_left} hours)",
                        "formatted_date": evt_time.strftime("%A, %B %d, %Y at %I:%M %p UTC")
                    })
            except Exception:
                upcoming.append(e)

        return {
            "status": "success",
            "total_upcoming": len(upcoming),
            "window_days": days_ahead,
            "events": upcoming
        }

    def get_next_cohort(self) -> Dict[str, Any]:
        """Finds the nearest upcoming cohort start event."""
        res = self.get_upcoming_events(days_ahead=90)
        cohort_events = [e for e in res["events"] if e.get("type") == "cohort_start"]
        if cohort_events:
            return {"status": "success", "next_cohort": cohort_events[0]}
        return {"status": "not_found", "message": "No cohort kick-off scheduled in the next 90 days."}

    def schedule_event(
        self,
        title: str,
        event_type: str,
        start_time: Optional[str],
        location: str,
        description: str
    ) -> Dict[str, Any]:
        """Drafts a calendar event (Tier 2: creates draft and awaits confirmation)."""
        event_id = f"EVT-DRAFT-{int(datetime.now(timezone.utc).timestamp())}"
        draft_event = {
            "id": event_id,
            "title": title,
            "type": event_type,
            "start_time": start_time or (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "location": location,
            "description": description,
            "status": "draft_pending_review"
        }

        # Return draft preview object for Tier 2 Review
        return {
            "status": "draft_created",
            "tier": 2,
            "event_id": event_id,
            "preview": {
                "title": f"📅 Proposed Event: {title}",
                "type": event_type,
                "scheduled_time": draft_event["start_time"],
                "location": location,
                "summary": description
            },
            "message": "Calendar event drafted successfully. Awaiting administrative review before adding to live student calendar."
        }

    def check_and_trigger_reminders(self, window_hours: int = 48) -> Dict[str, Any]:
        """Generates automated WhatsApp and push reminder notifications for upcoming events."""
        now = datetime.now(timezone.utc)
        threshold = now + timedelta(hours=window_hours)

        reminders_to_send = []
        for e in self._events:
            try:
                evt_time = datetime.fromisoformat(e["start_time"])
                if evt_time.tzinfo is None:
                    evt_time = evt_time.replace(tzinfo=timezone.utc)

                if now < evt_time <= threshold:
                    hours_until = int((evt_time - now).total_seconds() // 3600)
                    reminders_to_send.append({
                        "event_id": e["id"],
                        "event_title": e["title"],
                        "hours_until": hours_until,
                        "formatted_date": evt_time.strftime("%A, %d %B %Y at %I:%M %p"),
                        "location": e.get("location"),
                        "whatsapp_message": (
                            f"🔔 *Nextserve Reminder:* {e['title']}\n\n"
                            f"⏰ Starting in *{hours_until} hours* ({evt_time.strftime('%b %d, %I:%M %p')})\n"
                            f"📍 Venue: {e.get('location', 'Online')}\n"
                            f"🔗 Link: {e.get('link', 'https://nextserveschool.com')}\n\n"
                            f"Please arrive 10 minutes early. Need help? Chat us here!"
                        ),
                        "email_subject": f"Reminder: {e['title']} starts in {hours_until} hours"
                    })
            except Exception as err:
                logger.error(f"Error parsing event {e.get('id')}: {err}")

        return {
            "status": "success",
            "count": len(reminders_to_send),
            "window_hours": window_hours,
            "reminders": reminders_to_send
        }

    def send_calendar_telegram_notification(self, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches an instant academic calendar briefing & cohort reminder to the Admin Telegram channel."""
        from skills.skill_messaging import MessagingSkill
        messaging = MessagingSkill()

        upcoming = self.get_upcoming_events(days_ahead=60).get("events", [])
        if not upcoming:
            text = "📅 <b>Nextserve Academic Calendar:</b> No events scheduled in the next 60 days."
            return messaging.send_telegram_message(chat_id=chat_id, text=text)

        event_blocks = []
        for e in upcoming[:4]:
            event_blocks.append(
                f"📌 <b>{e['title']}</b>\n"
                f"   ⏰ <i>{e.get('formatted_date', e.get('start_time'))}</i> ({e.get('time_until', '')})\n"
                f"   📍 Venue: {e.get('location', 'Online')}\n"
                f"   🔗 Link: {e.get('link', 'https://nextserveschool.com')}"
            )

        events_str = "\n\n".join(event_blocks)

        text = (
            "📅 <b>Nextserve School Academic Calendar Alert</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Here are your upcoming cohorts, orientation webinars, and exams:\n\n"
            f"{events_str}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <i>Automated Calendar Sync • NextClaw Autonomous School System</i>"
        )

        return messaging.send_telegram_message(chat_id=chat_id, text=text)


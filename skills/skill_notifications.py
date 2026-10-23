"""NextClaw OS - Notifications Skill Alias (skill_notifications.py).

Provides compatibility with skill_telegram.py for direct approval cards
and admin alert notifications.
"""

from skills.skill_telegram import TelegramSkill

# NotificationSkill is functionally equivalent to TelegramSkill
NotificationSkill = TelegramSkill
__all__ = ["TelegramSkill", "NotificationSkill"]

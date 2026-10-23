"""NextClaw OS - Website Skill Alias (skill_website.py).

Provides compatibility with skill_cms.py for website drafting,
HTML/Markdown preview generation, and CMS updates.
"""

from skills.skill_cms import CMSSkill

# WebsiteSkill is functionally equivalent to CMSSkill
WebsiteSkill = CMSSkill
__all__ = ["CMSSkill", "WebsiteSkill"]

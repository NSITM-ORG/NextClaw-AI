"""NextClaw OS - Pluggable Skill System.

Provides the BaseSkill abstract class and dynamic skill loader
governed by configs/SKILLS.json.
"""

from abc import ABC, abstractmethod
import json
import logging
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, Type

logger = logging.getLogger("nextclaw.skills")

CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"
SKILLS_CONFIG_FILE = CONFIGS_DIR / "SKILLS.json"


class BaseSkill(ABC):
    """Abstract base class for all NextClaw pluggable skills."""

    name: str = "base_skill"
    tier: int = 1
    description: str = "Base Skill"
    enabled: bool = True

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

    @abstractmethod
    def execute(self, action: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    def get_tier(self, action: Optional[str] = None) -> int:
        return self.tier


class SkillRegistry:
    """Registry managing active skill instances loaded from SKILLS.json."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SkillRegistry, cls).__new__(cls)
            cls._instance._skills: Dict[str, BaseSkill] = {}
            cls._instance._config_data: Dict[str, Any] = {}
            cls._instance._load_skills()
        return cls._instance

    def _load_skills(self):
        """Loads and instantiates skills configured in SKILLS.json."""
        if not SKILLS_CONFIG_FILE.exists():
            logger.warning(f"SKILLS.json not found at {SKILLS_CONFIG_FILE}. Loading defaults.")
            return

        try:
            with open(SKILLS_CONFIG_FILE, "r", encoding="utf-8") as f:
                self._config_data = json.load(f)

            skills_dict = self._config_data.get("skills", {})
            for skill_id, skill_meta in skills_dict.items():
                if not skill_meta.get("enabled", True):
                    logger.info(f"Skill '{skill_id}' is disabled in SKILLS.json. Skipping.")
                    continue

                module_name = skill_meta.get("module")
                class_name = skill_meta.get("class_name")

                try:
                    # Dynamically import skill module
                    try:
                        mod = importlib.import_module(module_name)
                    except ModuleNotFoundError:
                        clean_mod = module_name.split(".")[-1]
                        mod = importlib.import_module(f"skills.{clean_mod}")

                    skill_cls: Type[BaseSkill] = getattr(mod, class_name)
                    instance = skill_cls(config=skill_meta)
                    self._skills[skill_id] = instance
                    logger.info(f"Loaded skill: {skill_id} ({instance.name}) [Tier {instance.tier}]")
                except Exception as exc:
                    logger.error(f"Failed to load skill '{skill_id}' ({module_name}.{class_name}): {exc}")

        except Exception as err:
            logger.error(f"Error parsing SKILLS.json: {err}")

    def get_skill(self, skill_id: str) -> Optional[BaseSkill]:
        """Retrieve an active skill by identifier."""
        return self._skills.get(skill_id)

    def list_active_skills(self) -> Dict[str, Dict[str, Any]]:
        """Returns metadata for all currently enabled skills."""
        return {
            sid: {
                "name": s.name,
                "tier": s.tier,
                "description": s.description,
                "enabled": s.enabled,
            }
            for sid, s in self._skills.items()
        }

    def reload(self):
        """Reloads skills configuration and instantiates active skills."""
        self._skills.clear()
        self._load_skills()


skill_registry = SkillRegistry()

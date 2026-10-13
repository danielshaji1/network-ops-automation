"""Google Antigravity SDK and Skill handler definitions."""
from typing import Any, Callable, Dict, Optional


class AntigravitySkill:
    """Mock or base representation of Antigravity SDK Skill pattern."""

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: Optional[str] = None,
        allowlist_paths: Optional[list] = None,
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.allowlist_paths = allowlist_paths or []
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register_tool(self, name: str, fn: Callable[..., Any]) -> None:
        """Registers an executable tool function with this skill."""
        self._tools[name] = fn

    def __repr__(self) -> str:
        return f"<AntigravitySkill name={self.name!r} tools={list(self._tools.keys())}>"


__all__ = ["AntigravitySkill"]

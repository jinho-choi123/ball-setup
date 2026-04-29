from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    pass


@dataclass
class Tool:
    name: str
    category: str
    check_cmd: str | list[str] | None = None
    description: str = ""
    pkg: dict[str, str] = field(default_factory=dict)
    post_install: dict[str, str] = field(default_factory=dict)
    custom_installer: Callable[..., None] | None = None


CATEGORIES: dict[str, dict[str, Any]] = {
    "essential": {"locked": True, "label": "Essential"},
    "shell": {"locked": True, "label": "Shell"},
    "dev": {"locked": False, "label": "Dev Tools"},
    "runtime": {"locked": False, "label": "Runtime"},
    "ai": {"locked": False, "label": "AI Tools"},
}


# Populated in Task 7 after custom installers are defined
TOOLS: list[Tool] = []


def get_tools_by_category(category: str) -> list[Tool]:
    return [t for t in TOOLS if t.category == category]

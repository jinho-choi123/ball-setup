from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from rich.console import Console

from .installer import command_exists
from .registry import CATEGORIES, TOOLS, Tool

if TYPE_CHECKING:
    from .detector import System


def is_installed(tool: Tool) -> bool:
    if tool.check_cmd is None:
        return False  # custom_installer handles its own idempotency
    cmds = tool.check_cmd if isinstance(tool.check_cmd, list) else [tool.check_cmd]
    return any(command_exists(cmd) for cmd in cmds)


def create_console() -> Console:
    return Console()


def has_tty() -> bool:
    return sys.stdin.isatty()


def select_tools(system: System, console: Console) -> list[Tool]:
    from InquirerPy import inquirer

    choices = []
    for cat_id, cat_info in CATEGORIES.items():
        cat_tools = [t for t in TOOLS if t.category == cat_id]
        if not cat_tools:
            continue

        # Add separator for category
        choices.append({"name": f"── {cat_info['label']} ──", "value": None, "enabled": False})

        for tool in cat_tools:
            already = is_installed(tool)
            label = f"{tool.name} (installed)" if already else tool.name
            choices.append({
                "name": label,
                "value": tool,
                "enabled": cat_info["locked"] or not already,
            })

    selected = inquirer.checkbox(
        message="Select tools to install:",
        choices=[c for c in choices if c["value"] is not None],
        instruction="(space: toggle, a: all, enter: confirm)",
    ).execute()

    # Always include locked categories
    locked_tools = [t for t in TOOLS if CATEGORIES[t.category]["locked"]]
    result = list(set(locked_tools + selected))

    # Preserve registry order
    tool_order = {t: i for i, t in enumerate(TOOLS)}
    result.sort(key=lambda t: tool_order.get(t, 999))
    return result


def get_all_tools() -> list[Tool]:
    return list(TOOLS)


def get_tools_for_categories(categories: list[str]) -> list[Tool]:
    locked = [t for t in TOOLS if CATEGORIES[t.category]["locked"]]
    selected = [t for t in TOOLS if t.category in categories]
    seen: set[str] = set()
    result: list[Tool] = []
    for t in locked + selected:
        if t.name not in seen:
            seen.add(t.name)
            result.append(t)
    return result

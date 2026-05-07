from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from . import __version__
from .detector import detect_system
from .installer import PackageManager, command_exists, run_shell
from .registry import TOOLS, Tool
from .shell import configure_shell_env, configure_zsh_plugins
from .tui import (
    create_console,
    get_all_tools,
    get_tools_for_categories,
    has_tty,
    is_installed,
    select_tools,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ball-setup",
        description="Remote server setup tool",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Install all tools (non-interactive)",
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help="Install only specific categories (comma-separated: dev,runtime,ai)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be installed without installing",
    )
    return parser.parse_args(argv)


def install_tool(
    tool: Tool,
    system,
    pkg_mgr: PackageManager,
    console: Console,
    dry_run: bool = False,
) -> bool:
    if is_installed(tool):
        console.print(f" [green]✓[/] {tool.name} (already installed)")
        return False

    if dry_run:
        console.print(f" [blue]○[/] {tool.name} (would install)")
        return False

    console.print(f" [blue]▸[/] Installing {tool.name}...")
    try:
        if tool.custom_installer:
            tool.custom_installer(system, console, pkg_mgr)
        elif pkg_name := tool.pkg.get(system.os.value):
            pkg_mgr.install(pkg_name)
        else:
            return False

        # Post-install commands
        if post_cmd := tool.post_install.get(system.os.value):
            run_shell(post_cmd)

        console.print(f" [green]✓[/] {tool.name} installed")
        return True
    except Exception as e:
        console.print(f" [red]✗[/] {tool.name} failed: {e}")
        return False


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    console = create_console()

    console.print(f"\n [bold]ball-setup[/] v{__version__}\n")

    # Detect system
    system = detect_system()
    console.print(f" [blue]▸[/] Detected OS: {system.os.value} ({system.arch})\n")

    # Select tools
    if args.only:
        categories = [c.strip() for c in args.only.split(",")]
        tools = get_tools_for_categories(categories)
    elif args.all or not has_tty():
        tools = get_all_tools()
    else:
        tools = select_tools(system, console)

    if args.dry_run:
        console.print(" [bold]Dry run — no changes will be made:[/]\n")

    # Install
    pkg_mgr = PackageManager(system)
    installed_count = 0
    for tool in tools:
        if install_tool(tool, system, pkg_mgr, console, args.dry_run):
            installed_count += 1

    # Post-install: configure shell
    if not args.dry_run:
        zshrc = Path.home() / ".zshrc"
        if zshrc.exists():
            configure_zsh_plugins(zshrc)
            configure_shell_env(zshrc)

    console.print(f"\n [green]✓[/] Setup complete! Restart shell or run: exec zsh\n")

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from .installer import command_exists, run_cmd, sudo_prefix

if TYPE_CHECKING:
    from rich.console import Console
    from .detector import System
    from .installer import PackageManager


def install_zsh(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    from .detector import OS

    match system.os:
        case OS.MACOS:
            pass  # zsh is default on macOS
        case _:
            pkg_mgr.install("zsh")

    # Change default shell
    import os
    current_shell = os.environ.get("SHELL", "")
    if "zsh" not in current_shell:
        zsh_path = subprocess.run(
            ["which", "zsh"], capture_output=True, text=True
        ).stdout.strip()
        if zsh_path:
            sudo = sudo_prefix(system)
            result = subprocess.run(
                [*sudo, "chsh", "-s", zsh_path, os.environ.get("USER", "")],
            )
            if result.returncode != 0:
                console.print(
                    " [yellow]⚠[/] Could not change shell — run manually: "
                    "chsh -s $(which zsh)"
                )


def install_ohmyzsh(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    omz_dir = Path.home() / ".oh-my-zsh"
    if omz_dir.exists():
        return
    with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
        result = subprocess.run(
            ["curl", "-fsSL",
             "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"],
            capture_output=True, check=True,
        )
        f.write(result.stdout)
        f.flush()
        import os
        env = os.environ.copy()
        env["RUNZSH"] = "no"
        run_cmd(["sh", f.name, "--unattended"], env=env)


def install_zsh_plugin(name: str, repo_url: str) -> None:
    import os
    custom_dir = os.environ.get(
        "ZSH_CUSTOM",
        str(Path.home() / ".oh-my-zsh" / "custom"),
    )
    dest = Path(custom_dir) / "plugins" / name
    if dest.exists():
        return
    run_cmd(["git", "clone", "--depth", "1", repo_url, str(dest)])


def install_zsh_autosuggestions(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    install_zsh_plugin(
        "zsh-autosuggestions",
        "https://github.com/zsh-users/zsh-autosuggestions",
    )


def install_zsh_syntax_highlighting(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    install_zsh_plugin(
        "zsh-syntax-highlighting",
        "https://github.com/zsh-users/zsh-syntax-highlighting",
    )


def install_zsh_completions(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    install_zsh_plugin(
        "zsh-completions",
        "https://github.com/zsh-users/zsh-completions",
    )


def configure_zsh_plugins(zshrc_path: Path) -> None:
    if not zshrc_path.exists():
        return
    content = zshrc_path.read_text()
    if "zsh-autosuggestions" in content:
        return
    new_plugins = "plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions)"
    content = re.sub(r"^plugins=\(.*\)", new_plugins, content, flags=re.MULTILINE)
    zshrc_path.write_text(content)


def configure_shell_env(zshrc_path: Path) -> None:
    if zshrc_path.exists() and "# ball-setup managed" in zshrc_path.read_text():
        return
    block = """
# ball-setup managed
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.bun/bin:$PATH"
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env --shell zsh)"
"""
    with zshrc_path.open("a") as f:
        f.write(block)

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    pass

from .installer import (
    install_build_tools,
    install_ca_certificates,
    install_gh_cli,
    install_lazygit,
    install_bun,
    install_fnm,
    install_node_lts,
    install_claude_code,
    install_codex_cli,
    install_kilo_cli,
    install_cline_cli,
    install_plugins,
    install_skills,
)
from .shell import (
    install_zsh,
    install_ohmyzsh,
    install_zsh_autosuggestions,
    install_zsh_syntax_highlighting,
    install_zsh_completions,
)


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


TOOLS: list[Tool] = [
    # ── Essential ──
    Tool(
        name="git", category="essential", check_cmd="git",
        pkg={"ubuntu": "git", "debian": "git", "rocky": "git", "macos": "git"},
    ),
    Tool(
        name="curl", category="essential", check_cmd="curl",
        pkg={"ubuntu": "curl", "debian": "curl", "rocky": "curl", "macos": "curl"},
    ),
    Tool(
        name="unzip", category="essential", check_cmd="unzip",
        pkg={"ubuntu": "unzip", "debian": "unzip", "rocky": "unzip"},
    ),
    Tool(
        name="ca-certificates", category="essential", check_cmd="openssl",
        custom_installer=install_ca_certificates,
    ),
    Tool(
        name="build-tools", category="essential", check_cmd="make",
        custom_installer=install_build_tools,
    ),
    # ── Shell ──
    Tool(
        name="zsh", category="shell", check_cmd="zsh",
        custom_installer=install_zsh,
    ),
    Tool(
        name="oh-my-zsh", category="shell",
        custom_installer=install_ohmyzsh,
    ),
    Tool(
        name="zsh-autosuggestions", category="shell",
        custom_installer=install_zsh_autosuggestions,
    ),
    Tool(
        name="zsh-syntax-highlighting", category="shell",
        custom_installer=install_zsh_syntax_highlighting,
    ),
    Tool(
        name="zsh-completions", category="shell",
        custom_installer=install_zsh_completions,
    ),
    # ── Dev Tools ──
    Tool(
        name="tmux", category="dev", check_cmd="tmux",
        pkg={"ubuntu": "tmux", "debian": "tmux", "rocky": "tmux", "macos": "tmux"},
    ),
    Tool(
        name="jq", category="dev", check_cmd="jq",
        pkg={"ubuntu": "jq", "debian": "jq", "rocky": "jq", "macos": "jq"},
    ),
    Tool(
        name="ripgrep", category="dev", check_cmd="rg",
        pkg={"ubuntu": "ripgrep", "debian": "ripgrep", "rocky": "ripgrep", "macos": "ripgrep"},
    ),
    Tool(
        name="fd", category="dev", check_cmd=["fd", "fdfind"],
        pkg={"ubuntu": "fd-find", "debian": "fd-find", "rocky": "fd-find", "macos": "fd"},
        post_install={"ubuntu": "sudo ln -sf $(which fdfind) /usr/local/bin/fd",
                      "debian": "sudo ln -sf $(which fdfind) /usr/local/bin/fd"},
    ),
    Tool(
        name="fzf", category="dev", check_cmd="fzf",
        pkg={"ubuntu": "fzf", "debian": "fzf", "rocky": "fzf", "macos": "fzf"},
    ),
    Tool(
        name="htop", category="dev", check_cmd="htop",
        pkg={"ubuntu": "htop", "debian": "htop", "rocky": "htop", "macos": "htop"},
    ),
    Tool(
        name="make", category="dev", check_cmd="make",
        pkg={"ubuntu": "make", "debian": "make", "rocky": "make", "macos": "make"},
    ),
    Tool(
        name="gh", category="dev", check_cmd="gh",
        custom_installer=install_gh_cli,
    ),
    Tool(
        name="lazygit", category="dev", check_cmd="lazygit",
        custom_installer=install_lazygit,
    ),
    # ── Runtime ──
    Tool(
        name="bun", category="runtime", check_cmd="bun",
        custom_installer=install_bun,
    ),
    Tool(
        name="fnm", category="runtime", check_cmd="fnm",
        custom_installer=install_fnm,
    ),
    Tool(
        name="node", category="runtime", check_cmd="node",
        custom_installer=install_node_lts,
    ),
    # ── AI Tools ──
    Tool(
        name="claude-code", category="ai", check_cmd="claude",
        custom_installer=install_claude_code,
    ),
    Tool(
        name="codex-cli", category="ai", check_cmd="codex",
        custom_installer=install_codex_cli,
    ),
    Tool(
        name="kilo-cli", category="ai", check_cmd="kilo",
        custom_installer=install_kilo_cli,
    ),
    Tool(
        name="cline-cli", category="ai", check_cmd="cline",
        custom_installer=install_cline_cli,
    ),
    Tool(
        name="plugins", category="ai",
        custom_installer=install_plugins,
    ),
    Tool(
        name="skills", category="ai",
        custom_installer=install_skills,
    ),
]


def get_tools_by_category(category: str) -> list[Tool]:
    return [t for t in TOOLS if t.category == category]

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING

from rich.console import Console

from .detector import OS

if TYPE_CHECKING:
    from .detector import System


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def sudo_prefix(system: System) -> list[str]:
    return [] if system.is_root else ["sudo"]


def run_cmd(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kwargs)


def run_shell(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, check=True, **kwargs)


class PackageManager:
    def __init__(self, system: System):
        self.system = system
        self._index_updated = False

    def ensure_index(self) -> None:
        if self._index_updated:
            return
        sudo = sudo_prefix(self.system)
        match self.system.os:
            case OS.UBUNTU | OS.DEBIAN:
                run_cmd([*sudo, "apt-get", "update", "-y"])
            case OS.ROCKY:
                result = subprocess.run(
                    [*sudo, "dnf", "repolist", "enabled"],
                    capture_output=True, text=True,
                )
                if "epel" not in result.stdout:
                    run_cmd([*sudo, "dnf", "install", "-y", "epel-release"])
                run_cmd([*sudo, "dnf", "makecache", "-y"])
            case OS.MACOS:
                if not command_exists("brew"):
                    raise SystemExit(
                        "Homebrew not found. Install from https://brew.sh first."
                    )
        self._index_updated = True

    def install(self, package: str) -> None:
        self.ensure_index()
        sudo = sudo_prefix(self.system)
        match self.system.os:
            case OS.UBUNTU | OS.DEBIAN:
                run_cmd([*sudo, "apt-get", "install", "-y", package])
            case OS.ROCKY:
                run_cmd([*sudo, "dnf", "install", "-y", package])
            case OS.MACOS:
                run_cmd(["brew", "install", package])

    def reset_index(self) -> None:
        self._index_updated = False


def install_build_tools(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    sudo = sudo_prefix(system)
    match system.os:
        case OS.UBUNTU | OS.DEBIAN:
            pkg_mgr.install("build-essential")
        case OS.ROCKY:
            run_cmd([*sudo, "dnf", "groupinstall", "-y", "Development Tools"])
        case OS.MACOS:
            result = subprocess.run(
                ["xcode-select", "-p"], capture_output=True
            )
            if result.returncode != 0:
                console.print(
                    " [yellow]⚠[/] Run 'xcode-select --install' manually"
                )


def install_ca_certificates(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    match system.os:
        case OS.UBUNTU | OS.DEBIAN | OS.ROCKY:
            pkg_mgr.install("ca-certificates")
        case OS.MACOS:
            pass  # not needed on macOS


def install_gh_cli(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    sudo = sudo_prefix(system)
    match system.os:
        case OS.UBUNTU | OS.DEBIAN:
            run_cmd(
                [
                    "bash", "-c",
                    "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg "
                    f"| {'sudo ' if not system.is_root else ''}tee /usr/share/keyrings/githubcli-archive-keyring.gpg > /dev/null",
                ]
            )
            arch_result = subprocess.run(
                ["dpkg", "--print-architecture"],
                capture_output=True, text=True, check=True,
            )
            arch = arch_result.stdout.strip()
            repo_line = (
                f"deb [arch={arch} signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] "
                "https://cli.github.com/packages stable main"
            )
            run_cmd(
                [*sudo, "tee", "/etc/apt/sources.list.d/github-cli.list"],
                input=repo_line.encode(),
                stdout=subprocess.DEVNULL,
            )
            pkg_mgr.reset_index()
            pkg_mgr.install("gh")
        case OS.ROCKY:
            run_cmd(
                [*sudo, "dnf", "install", "-y", "dnf-command(config-manager)"],
            )
            run_cmd(
                [*sudo, "dnf", "config-manager", "--add-repo",
                 "https://cli.github.com/packages/rpm/gh-cli.repo"],
            )
            run_cmd([*sudo, "dnf", "install", "-y", "gh"])
        case OS.MACOS:
            pkg_mgr.install("gh")


def install_lazygit(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    if system.os == OS.MACOS:
        pkg_mgr.install("lazygit")
        return
    arch_map = {"x86_64": "x86_64", "arm64": "arm64"}
    lg_arch = arch_map.get(system.arch)
    if not lg_arch:
        console.print(f" [yellow]⚠[/] Unsupported arch for lazygit: {system.arch}")
        return
    result = subprocess.run(
        ["curl", "-s", "https://api.github.com/repos/jesseduffield/lazygit/releases/latest"],
        capture_output=True, text=True, check=True,
    )
    version = json.loads(result.stdout)["tag_name"].lstrip("v")
    with tempfile.TemporaryDirectory() as tmp:
        url = (
            f"https://github.com/jesseduffield/lazygit/releases/download/"
            f"v{version}/lazygit_{version}_Linux_{lg_arch}.tar.gz"
        )
        run_cmd(["curl", "-Lo", f"{tmp}/lazygit.tar.gz", url])
        run_cmd(["tar", "xf", f"{tmp}/lazygit.tar.gz", "-C", tmp, "lazygit"])
        run_cmd([*sudo_prefix(system), "install", f"{tmp}/lazygit", "/usr/local/bin"])


def install_bun(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
        result = subprocess.run(
            ["curl", "-fsSL", "https://bun.sh/install"],
            capture_output=True, check=True,
        )
        f.write(result.stdout)
        f.flush()
        run_cmd(["bash", f.name])


def _load_fnm_env() -> None:
    import os
    result = subprocess.run(
        ["fnm", "env", "--shell", "bash"],
        capture_output=True, text=True, check=True,
    )
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line.startswith("export "):
            continue
        assignment = line[len("export "):].rstrip(";")
        if "=" not in assignment:
            continue
        key, _, value = assignment.partition("=")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        os.environ[key] = os.path.expandvars(value)


def install_fnm(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
        result = subprocess.run(
            ["curl", "-fsSL", "https://fnm.vercel.app/install"],
            capture_output=True, check=True,
        )
        f.write(result.stdout)
        f.flush()
        run_cmd(["bash", f.name, "--skip-shell"])
    import os
    os.environ["PATH"] = os.path.expanduser("~/.local/share/fnm") + ":" + os.environ["PATH"]
    _load_fnm_env()


def install_node_lts(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    if command_exists("fnm"):
        _load_fnm_env()
    run_cmd(["fnm", "install", "--lts"])
    run_cmd(["fnm", "default", "lts-latest"])
    run_cmd(["fnm", "use", "lts-latest"])


def install_claude_code(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    run_cmd(["bun", "install", "-g", "@anthropic-ai/claude-code"])
    console.print(" [blue]▸[/] Logging in to Claude Code...")
    subprocess.run(["claude", "login"], stdin=open("/dev/tty"))


def install_codex_cli(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    run_cmd(["bun", "install", "-g", "@openai/codex"])


def install_kilo_cli(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    run_cmd(["bun", "install", "-g", "@kilocode/cli"])


def install_cline_cli(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    run_cmd(["bun", "install", "-g", "cline"])


def install_plugins(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    marketplaces = [
        "https://github.com/Yeachan-Heo/oh-my-claudecode.git",
        "thedotmack/claude-mem",
        "JuliusBrussee/caveman",
    ]
    for mp in marketplaces:
        subprocess.run(["claude", "plugin", "marketplace", "add", mp])

    plugins = [
        "oh-my-claudecode@omc",
        "claude-mem@thedotmack",
        "caveman@caveman",
        "superpowers@claude-plugins-official",
    ]
    for plugin in plugins:
        subprocess.run(["claude", "plugin", "install", plugin])


def install_skills(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    repos = [
        "shubhamsaboo/awesome-llm-apps",
        "juliusbrussee/caveman",
        "github/awesome-copilot",
        "mattpocock/skills",
        "tavily-ai/skills",
        "vercel-labs/skills",
        "anthropics/skills",
        "Astro-Han/karpathy-llm-wiki",
    ]
    for repo in repos:
        console.print(f" [blue]▸[/] Installing skills from {repo}...")
        subprocess.run(["bunx", "skills", "add", repo, "-g", "-y"])

    # Custom skills from this repo
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            ["git", "clone", "--depth", "1",
             "https://github.com/jinho-choi123/ball-setup.git", tmp],
            capture_output=True,
        )
        if result.returncode != 0:
            console.print(" [yellow]⚠[/] Failed to clone custom skills repo")
            return

        import os
        from pathlib import Path
        custom_skills_dir = Path(tmp) / "custom-skills"
        if not custom_skills_dir.exists():
            console.print(" [yellow]⚠[/] No custom-skills directory found")
            return

        agents_dir = Path.home() / ".agents" / "skills"
        claude_dir = Path.home() / ".claude" / "skills"
        agents_dir.mkdir(parents=True, exist_ok=True)
        claude_dir.mkdir(parents=True, exist_ok=True)

        for skill_dir in custom_skills_dir.iterdir():
            if skill_dir.is_dir():
                dest = agents_dir / skill_dir.name
                shutil.copytree(skill_dir, dest, dirs_exist_ok=True)
                link = claude_dir / skill_dir.name
                if not link.exists():
                    link.symlink_to(dest)

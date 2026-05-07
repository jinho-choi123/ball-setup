# ball-setup Python Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite ball-setup from bash to Python with uv bootstrap, adding interactive TUI for tool selection while preserving curl|bash one-liner deployment.

**Architecture:** Thin bash bootstrap installs uv, then `uvx` runs the Python package from git. Python package uses declarative tool registry with InquirerPy TUI for selection and rich for output. Non-interactive fallback preserves current bash behavior.

**Tech Stack:** Python 3.12+, uv/uvx, rich, InquirerPy, pytest

---

## File Structure

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package config, dependencies, entry point |
| `bootstrap.sh` | 5-line bash bootstrap (uv install + uvx) |
| `src/ball_setup/__init__.py` | Package init with version |
| `src/ball_setup/cli.py` | Entry point, arg parsing, main orchestration |
| `src/ball_setup/detector.py` | OS and architecture detection |
| `src/ball_setup/registry.py` | Tool dataclass + declarative TOOLS list |
| `src/ball_setup/installer.py` | PackageManager, command_exists, custom installers |
| `src/ball_setup/tui.py` | Interactive checkbox selection + rich output helpers |
| `src/ball_setup/shell.py` | zsh, oh-my-zsh, plugins, .zshrc configuration |
| `tests/test_detector.py` | OS detection tests |
| `tests/test_registry.py` | Registry validation tests |
| `tests/test_installer.py` | PackageManager tests |
| `tests/test_cli.py` | CLI arg parsing tests |
| `tests/test_shell.py` | Shell configuration tests |

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/ball_setup/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "ball-setup"
version = "1.0.0"
description = "Remote server setup tool with interactive TUI"
requires-python = ">=3.12"
dependencies = [
    "rich>=13.0",
    "InquirerPy>=0.3.4",
]

[project.scripts]
ball-setup = "ball_setup.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = ["pytest>=8.0"]
```

- [ ] **Step 2: Create package init**

`src/ball_setup/__init__.py`:

```python
__version__ = "1.0.0"
```

- [ ] **Step 3: Create test init**

`tests/__init__.py`: empty file.

- [ ] **Step 4: Verify uv recognizes the project**

Run: `uv sync`
Expected: creates `.venv/`, installs dependencies

- [ ] **Step 5: Verify pytest runs**

Run: `uv run pytest --co`
Expected: "no tests ran" (no test files yet), exit 0 or 5 (no tests collected)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "feat: scaffold Python package with pyproject.toml"
```

---

### Task 2: OS Detection

**Files:**
- Create: `src/ball_setup/detector.py`
- Create: `tests/test_detector.py`

- [ ] **Step 1: Write failing tests**

`tests/test_detector.py`:

```python
from unittest.mock import patch, mock_open
import pytest
from ball_setup.detector import OS, detect_os, detect_arch, detect_system


class TestDetectOS:
    @patch("ball_setup.detector.platform.system", return_value="Darwin")
    def test_macos(self, _mock):
        assert detect_os() == OS.MACOS

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_ubuntu(self, _mock):
        content = 'ID=ubuntu\nVERSION_ID="24.04"\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                assert detect_os() == OS.UBUNTU

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_debian(self, _mock):
        content = 'ID=debian\nVERSION_ID="12"\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                assert detect_os() == OS.DEBIAN

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_rocky(self, _mock):
        content = 'ID="rocky"\nVERSION_ID="9.3"\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                assert detect_os() == OS.ROCKY

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_unsupported_os(self, _mock):
        content = 'ID=arch\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                with pytest.raises(SystemExit, match="Unsupported OS: arch"):
                    detect_os()


class TestDetectArch:
    @patch("ball_setup.detector.platform.machine", return_value="x86_64")
    def test_x86_64(self, _mock):
        assert detect_arch() == "x86_64"

    @patch("ball_setup.detector.platform.machine", return_value="aarch64")
    def test_aarch64(self, _mock):
        assert detect_arch() == "arm64"

    @patch("ball_setup.detector.platform.machine", return_value="arm64")
    def test_arm64(self, _mock):
        assert detect_arch() == "arm64"

    @patch("ball_setup.detector.platform.machine", return_value="riscv64")
    def test_unsupported(self, _mock):
        with pytest.raises(SystemExit, match="Unsupported architecture"):
            detect_arch()


class TestDetectSystem:
    @patch("ball_setup.detector.os.getuid", return_value=0)
    @patch("ball_setup.detector.platform.machine", return_value="x86_64")
    @patch("ball_setup.detector.platform.system", return_value="Darwin")
    def test_root_macos(self, *_):
        system = detect_system()
        assert system.os == OS.MACOS
        assert system.arch == "x86_64"
        assert system.is_root is True

    @patch("ball_setup.detector.os.getuid", return_value=1000)
    @patch("ball_setup.detector.platform.machine", return_value="aarch64")
    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_non_root_linux(self, *_):
        content = 'ID=ubuntu\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                system = detect_system()
                assert system.os == OS.UBUNTU
                assert system.arch == "arm64"
                assert system.is_root is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_detector.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ball_setup.detector'`

- [ ] **Step 3: Implement detector.py**

`src/ball_setup/detector.py`:

```python
from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OS(Enum):
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    ROCKY = "rocky"
    MACOS = "macos"


@dataclass(frozen=True)
class System:
    os: OS
    arch: str
    is_root: bool


def _parse_os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            result[key] = value.strip('"')
    return result


def detect_os() -> OS:
    if platform.system() == "Darwin":
        return OS.MACOS
    info = _parse_os_release()
    os_id = info.get("ID", "")
    match os_id:
        case "ubuntu":
            return OS.UBUNTU
        case "debian":
            return OS.DEBIAN
        case "rocky" | "rocky-linux":
            return OS.ROCKY
        case _:
            raise SystemExit(f"Unsupported OS: {os_id or 'unknown'}")


def detect_arch() -> str:
    match platform.machine():
        case "x86_64" | "AMD64":
            return "x86_64"
        case "aarch64" | "arm64":
            return "arm64"
        case other:
            raise SystemExit(f"Unsupported architecture: {other}")


def detect_system() -> System:
    return System(
        os=detect_os(),
        arch=detect_arch(),
        is_root=os.getuid() == 0,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_detector.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/ball_setup/detector.py tests/test_detector.py
git commit -m "feat: add OS and architecture detection module"
```

---

### Task 3: Tool Registry Foundation

**Files:**
- Create: `src/ball_setup/registry.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write failing tests**

`tests/test_registry.py`:

```python
from ball_setup.registry import Tool, CATEGORIES, TOOLS


class TestTool:
    def test_tool_creation(self):
        tool = Tool(
            name="test-tool",
            category="dev",
            check_cmd="test-cmd",
            pkg={"ubuntu": "test-pkg"},
        )
        assert tool.name == "test-tool"
        assert tool.category == "dev"
        assert tool.check_cmd == "test-cmd"
        assert tool.pkg == {"ubuntu": "test-pkg"}

    def test_tool_list_check_cmd(self):
        tool = Tool(name="fd", category="dev", check_cmd=["fd", "fdfind"])
        assert isinstance(tool.check_cmd, list)


class TestCategories:
    def test_essential_locked(self):
        assert CATEGORIES["essential"]["locked"] is True

    def test_shell_locked(self):
        assert CATEGORIES["shell"]["locked"] is True

    def test_dev_unlocked(self):
        assert CATEGORIES["dev"]["locked"] is False

    def test_all_categories_have_label(self):
        for cat_id, cat in CATEGORIES.items():
            assert "label" in cat, f"Category '{cat_id}' missing label"


class TestToolsRegistry:
    def test_no_duplicate_names(self):
        names = [t.name for t in TOOLS]
        assert len(names) == len(set(names)), f"Duplicates: {[n for n in names if names.count(n) > 1]}"

    def test_all_tools_have_valid_category(self):
        for tool in TOOLS:
            assert tool.category in CATEGORIES, f"{tool.name} has invalid category '{tool.category}'"

    def test_tools_with_check_cmd_have_valid_type(self):
        for tool in TOOLS:
            if tool.check_cmd is not None:
                assert isinstance(tool.check_cmd, (str, list)), f"{tool.name} has invalid check_cmd type"

    def test_tools_without_check_cmd_have_custom_installer(self):
        for tool in TOOLS:
            if tool.check_cmd is None:
                assert tool.custom_installer is not None, f"{tool.name} has no check_cmd and no custom_installer"

    def test_all_tools_have_install_method(self):
        for tool in TOOLS:
            has_pkg = bool(tool.pkg)
            has_custom = tool.custom_installer is not None
            assert has_pkg or has_custom, f"{tool.name} has no install method"

    def test_essential_tools_exist(self):
        names = {t.name for t in TOOLS}
        for expected in ["git", "curl", "unzip"]:
            assert expected in names, f"Essential tool '{expected}' missing"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_registry.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement registry.py with Tool dataclass and empty TOOLS**

`src/ball_setup/registry.py`:

```python
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
```

Note: TOOLS is empty here. It will be populated in Task 7 after custom installer functions are available.

- [ ] **Step 4: Run tests — some pass, some fail**

Run: `uv run pytest tests/test_registry.py -v`
Expected: `test_tool_creation`, `test_tool_list_check_cmd`, category tests PASS. Registry validation tests FAIL because TOOLS is empty.

- [ ] **Step 5: Commit partial (tests will fully pass after Task 7)**

```bash
git add src/ball_setup/registry.py tests/test_registry.py
git commit -m "feat: add Tool dataclass and category definitions"
```

---

### Task 4: Package Manager & Helpers

**Files:**
- Create: `src/ball_setup/installer.py`
- Create: `tests/test_installer.py`

- [ ] **Step 1: Write failing tests**

`tests/test_installer.py`:

```python
from unittest.mock import patch, MagicMock
import pytest
from ball_setup.installer import command_exists, sudo_prefix, run_cmd, PackageManager
from ball_setup.detector import OS, System


@pytest.fixture
def ubuntu_system():
    return System(os=OS.UBUNTU, arch="x86_64", is_root=False)


@pytest.fixture
def rocky_system():
    return System(os=OS.ROCKY, arch="x86_64", is_root=False)


@pytest.fixture
def macos_system():
    return System(os=OS.MACOS, arch="arm64", is_root=False)


@pytest.fixture
def root_system():
    return System(os=OS.UBUNTU, arch="x86_64", is_root=True)


class TestCommandExists:
    @patch("ball_setup.installer.shutil.which", return_value="/usr/bin/git")
    def test_exists(self, _mock):
        assert command_exists("git") is True

    @patch("ball_setup.installer.shutil.which", return_value=None)
    def test_not_exists(self, _mock):
        assert command_exists("nonexistent") is False


class TestSudoPrefix:
    def test_non_root(self, ubuntu_system):
        assert sudo_prefix(ubuntu_system) == ["sudo"]

    def test_root(self, root_system):
        assert sudo_prefix(root_system) == []


class TestPackageManager:
    @patch("ball_setup.installer.run_cmd")
    def test_apt_install(self, mock_run, ubuntu_system):
        pm = PackageManager(ubuntu_system)
        pm._index_updated = True  # skip update for this test
        pm.install("ripgrep")
        mock_run.assert_called_with(["sudo", "apt-get", "install", "-y", "ripgrep"])

    @patch("ball_setup.installer.run_cmd")
    def test_dnf_install(self, mock_run, rocky_system):
        pm = PackageManager(rocky_system)
        pm._index_updated = True
        pm.install("ripgrep")
        mock_run.assert_called_with(["sudo", "dnf", "install", "-y", "ripgrep"])

    @patch("ball_setup.installer.run_cmd")
    def test_brew_install(self, mock_run, macos_system):
        pm = PackageManager(macos_system)
        pm._index_updated = True
        pm.install("ripgrep")
        mock_run.assert_called_with(["brew", "install", "ripgrep"])

    @patch("ball_setup.installer.run_cmd")
    def test_apt_update_called_once(self, mock_run, ubuntu_system):
        pm = PackageManager(ubuntu_system)
        pm.ensure_index()
        pm.ensure_index()
        mock_run.assert_called_once()

    def test_reset_index(self, ubuntu_system):
        pm = PackageManager(ubuntu_system)
        pm._index_updated = True
        pm.reset_index()
        assert pm._index_updated is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_installer.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement installer.py core**

`src/ball_setup/installer.py`:

```python
from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_installer.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/ball_setup/installer.py tests/test_installer.py
git commit -m "feat: add PackageManager and install helpers"
```

---

### Task 5: Custom Tool Installers

**Files:**
- Modify: `src/ball_setup/installer.py` — add custom installer functions

All custom installer functions follow the same signature:

```python
def install_<name>(system: System, console: Console, pkg_mgr: PackageManager) -> None:
```

- [ ] **Step 1: Add build tools installer**

Append to `src/ball_setup/installer.py`:

```python
from rich.console import Console
import tempfile
import json


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
```

- [ ] **Step 2: Add GitHub CLI installer**

Append to `src/ball_setup/installer.py`:

```python
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
```

- [ ] **Step 3: Add lazygit installer**

Append to `src/ball_setup/installer.py`:

```python
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
```

- [ ] **Step 4: Add script-based installers (bun, fnm, Node.js)**

Append to `src/ball_setup/installer.py`:

```python
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


def install_node_lts(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    # fnm must be installed first
    run_cmd(["fnm", "install", "--lts"])
    run_cmd(["fnm", "default", "lts-latest"])
    run_cmd(["fnm", "use", "lts-latest"])
```

- [ ] **Step 5: Add Claude Code, plugins, and skills installers**

Append to `src/ball_setup/installer.py`:

```python
def install_claude_code(
    system: System, console: Console, pkg_mgr: PackageManager
) -> None:
    run_cmd(["bun", "install", "-g", "@anthropic-ai/claude-code"])
    console.print(" [blue]▸[/] Logging in to Claude Code...")
    subprocess.run(["claude", "login"], stdin=open("/dev/tty"))


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
```

- [ ] **Step 6: Commit**

```bash
git add src/ball_setup/installer.py
git commit -m "feat: add all custom tool installer functions"
```

---

### Task 6: Shell Configuration

**Files:**
- Create: `src/ball_setup/shell.py`
- Create: `tests/test_shell.py`

- [ ] **Step 1: Write failing tests**

`tests/test_shell.py`:

```python
import tempfile
from pathlib import Path
from ball_setup.shell import configure_shell_env, configure_zsh_plugins


class TestConfigureShellEnv:
    def test_adds_marker_block(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zshrc", delete=False) as f:
            f.write("# existing content\n")
            path = Path(f.name)
        configure_shell_env(path)
        content = path.read_text()
        assert "# ball-setup managed" in content
        assert 'eval "$(fnm env --shell zsh)"' in content
        assert "$HOME/.bun/bin" in content
        path.unlink()

    def test_skips_if_marker_exists(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zshrc", delete=False) as f:
            f.write("# ball-setup managed\nexisting config\n")
            path = Path(f.name)
        original = path.read_text()
        configure_shell_env(path)
        assert path.read_text() == original
        path.unlink()


class TestConfigureZshPlugins:
    def test_updates_plugins_line(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zshrc", delete=False) as f:
            f.write('plugins=(git)\n')
            path = Path(f.name)
        configure_zsh_plugins(path)
        content = path.read_text()
        assert "zsh-autosuggestions" in content
        assert "zsh-syntax-highlighting" in content
        assert "zsh-completions" in content
        path.unlink()

    def test_skips_if_already_configured(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zshrc", delete=False) as f:
            f.write('plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions)\n')
            path = Path(f.name)
        original = path.read_text()
        configure_zsh_plugins(path)
        assert path.read_text() == original
        path.unlink()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_shell.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement shell.py**

`src/ball_setup/shell.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_shell.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/ball_setup/shell.py tests/test_shell.py
git commit -m "feat: add shell configuration module"
```

---

### Task 7: Complete Tool Registry

**Files:**
- Modify: `src/ball_setup/registry.py` — populate TOOLS list with all tools

- [ ] **Step 1: Populate TOOLS list**

Replace the empty `TOOLS` list in `src/ball_setup/registry.py` with the full list. Add imports at the top:

```python
from .installer import (
    install_build_tools,
    install_ca_certificates,
    install_gh_cli,
    install_lazygit,
    install_bun,
    install_fnm,
    install_node_lts,
    install_claude_code,
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
```

Replace `TOOLS: list[Tool] = []` with:

```python
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
        name="oh-my-zsh", category="shell", custom_installer=install_ohmyzsh,
    ),
    Tool(
        name="zsh-autosuggestions", category="shell", custom_installer=install_zsh_autosuggestions,
    ),
    Tool(
        name="zsh-syntax-highlighting", category="shell", custom_installer=install_zsh_syntax_highlighting,
    ),
    Tool(
        name="zsh-completions", category="shell", custom_installer=install_zsh_completions,
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
        name="plugins", category="ai", custom_installer=install_plugins,
    ),
    Tool(
        name="skills", category="ai", custom_installer=install_skills,
    ),
]
```

- [ ] **Step 2: Run registry tests — all should pass now**

Run: `uv run pytest tests/test_registry.py -v`
Expected: all pass (including `test_essential_tools_exist`, `test_no_duplicate_names`, etc.)

- [ ] **Step 3: Run full test suite**

Run: `uv run pytest -v`
Expected: all tests pass

- [ ] **Step 4: Commit**

```bash
git add src/ball_setup/registry.py
git commit -m "feat: populate complete tool registry with all tools"
```

---

### Task 8: Interactive TUI

**Files:**
- Create: `src/ball_setup/tui.py`

- [ ] **Step 1: Implement tui.py**

`src/ball_setup/tui.py`:

```python
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
    result = list(dict.fromkeys(locked + selected))  # dedupe preserving order
    return result
```

- [ ] **Step 2: Verify import works**

Run: `uv run python -c "from ball_setup.tui import select_tools, get_all_tools; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/ball_setup/tui.py
git commit -m "feat: add interactive TUI for tool selection"
```

---

### Task 9: CLI Entry Point

**Files:**
- Create: `src/ball_setup/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

`tests/test_cli.py`:

```python
from ball_setup.cli import parse_args


class TestParseArgs:
    def test_default(self):
        args = parse_args([])
        assert args.all is False
        assert args.only is None
        assert args.dry_run is False

    def test_all_flag(self):
        args = parse_args(["--all"])
        assert args.all is True

    def test_only_flag(self):
        args = parse_args(["--only", "dev,runtime"])
        assert args.only == "dev,runtime"

    def test_dry_run(self):
        args = parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_combined(self):
        args = parse_args(["--all", "--dry-run"])
        assert args.all is True
        assert args.dry_run is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL

- [ ] **Step 3: Implement cli.py**

`src/ball_setup/cli.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli.py -v`
Expected: all pass

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: all pass

- [ ] **Step 6: Verify entry point works**

Run: `uv run ball-setup --dry-run`
Expected: prints detected OS, lists all tools with "would install" / "already installed"

- [ ] **Step 7: Commit**

```bash
git add src/ball_setup/cli.py tests/test_cli.py
git commit -m "feat: add CLI entry point with arg parsing and install orchestration"
```

---

### Task 10: Bootstrap & Integration

**Files:**
- Create: `bootstrap.sh`
- Modify: `README.md`

- [ ] **Step 1: Create bootstrap.sh**

`bootstrap.sh`:

```bash
#!/bin/bash
set -euo pipefail
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uvx --from "git+https://github.com/jinho-choi123/ball-setup" ball-setup "$@"
```

- [ ] **Step 2: Make bootstrap executable**

Run: `chmod +x bootstrap.sh`

- [ ] **Step 3: Run full test suite one final time**

Run: `uv run pytest -v`
Expected: all pass

- [ ] **Step 4: Test dry-run end to end**

Run: `uv run ball-setup --dry-run`
Expected: prints all tools with their status, no actual installs

- [ ] **Step 5: Test --only flag**

Run: `uv run ball-setup --only dev --dry-run`
Expected: only essential (locked) + dev tools listed

- [ ] **Step 6: Update README.md**

Update the Usage section of `README.md` to document:
- New `curl ... bootstrap.sh | bash` usage
- `--all`, `--only`, `--dry-run` flags
- Interactive TUI description

- [ ] **Step 7: Commit**

```bash
git add bootstrap.sh README.md
git commit -m "feat: add bootstrap.sh and update README for Python rewrite"
```

- [ ] **Step 8: Final — remove old setup.sh**

Only after confirming the Python version works:

```bash
git rm setup.sh
git commit -m "chore: remove old bash setup.sh, replaced by Python package"
```

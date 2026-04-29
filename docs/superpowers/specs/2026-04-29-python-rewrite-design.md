# ball-setup: Bash → Python Rewrite Design

## Motivation

- Bash debugging/maintenance is painful (quoting, error handling, readability)
- Need complex features: interactive TUI (tool selection)
- Current setup.sh is 523 lines with repetitive if/else patterns per tool

## Constraints

- `curl -fsSL .../bootstrap.sh | bash` one-liner must work on bare servers
- No runtime pre-installed on target (Ubuntu, Debian, Rocky Linux, macOS)
- Existing behavior preserved: same tools, same OS support

## Approach: Python + uv Bootstrap

Thin bash bootstrap installs uv, then `uvx` runs the Python package from git.

### Bootstrap (`bootstrap.sh`)

```bash
#!/bin/bash
set -euo pipefail
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uvx --from "git+https://github.com/jinho-choi123/ball-setup" ball-setup "$@"
```

`uv` auto-downloads Python 3.12 if not present. No system Python dependency.
Args (`--all`, `--only`, etc.) are forwarded from bootstrap to the Python CLI.

### Package Structure

```
ball-setup/
├── bootstrap.sh
├── pyproject.toml
├── src/
│   └── ball_setup/
│       ├── __init__.py
│       ├── cli.py           # entry point, arg parsing
│       ├── detector.py      # OS/arch detection
│       ├── registry.py      # declarative tool definitions
│       ├── installer.py     # package manager abstraction + custom installers
│       ├── tui.py           # interactive tool selection
│       └── shell.py         # .zshrc configuration
├── custom-skills/
│   └── linear-manager/
├── README.md
└── docs/
```

### Dependencies (pyproject.toml)

- `rich` — colored output, progress bars, tables
- `InquirerPy` — checkbox prompts, confirmations

## Tool Registry (Declarative)

Replace repetitive bash if/else with declarative tool definitions:

```python
TOOLS = [
    Tool(
        name="git",
        category="essential",
        check_cmd="git",
        pkg={"ubuntu": "git", "debian": "git", "rocky": "git", "macos": "git"},
    ),
    Tool(
        name="ripgrep",
        category="dev",
        check_cmd="rg",
        pkg={"ubuntu": "ripgrep", "debian": "ripgrep", "rocky": "ripgrep", "macos": "ripgrep"},
    ),
    Tool(
        name="fd",
        category="dev",
        check_cmd=["fd", "fdfind"],
        pkg={"ubuntu": "fd-find", "debian": "fd-find", "rocky": "fd-find", "macos": "fd"},
        post_install={"ubuntu": "ln -sf $(which fdfind) /usr/local/bin/fd"},
    ),
    Tool(
        name="lazygit",
        category="dev",
        check_cmd="lazygit",
        pkg={"macos": "lazygit"},
        custom_installer=install_lazygit_binary,
    ),
    Tool(
        name="gh",
        category="dev",
        check_cmd="gh",
        pkg={"macos": "gh"},
        custom_installer=install_gh_cli,
    ),
]
```

Adding a new tool = one `Tool(...)` entry. No install logic changes.

### Categories

| Category | Tools | Selection |
|----------|-------|-----------|
| `essential` | git, curl, unzip, ca-certificates, build-essential | Always installed (locked) |
| `shell` | zsh, oh-my-zsh, zsh-autosuggestions, zsh-syntax-highlighting, zsh-completions | Always installed |
| `dev` | tmux, jq, ripgrep, fd, fzf, htop, make, gh, lazygit | Default checked |
| `runtime` | bun, fnm, Node.js LTS | Default checked |

Note: `uv` is installed by the bootstrap itself and is always present. It is not part of the TUI selection.

| `ai` | Claude Code, plugins, skills | Default checked |

## TUI Design

### Interactive Mode (tty detected)

Checkbox selection grouped by category. Essential/shell categories locked (always installed). Dev/runtime/ai categories default checked but toggleable.

Controls: arrow keys to move, space to select, `a` to toggle all, enter to confirm.

### Installation Progress (rich)

```
 ✓ git (already installed)
 ✓ curl (already installed)
 ▸ Installing ripgrep...  ━━━━━━━━━━━━━━━━━━━╸ 80%
 · fd
 · fzf
```

### Non-interactive Mode

```bash
# All tools (CI/automation, or no tty)
curl ... | bash -s -- --all

# Specific categories only
curl ... | bash -s -- --only dev,runtime

```

When tty is not available (piped input), auto-fallback to `--all` — preserving current bash behavior.

## CLI Interface

```
ball-setup                  # interactive TUI install
ball-setup --all            # install everything (non-interactive)
ball-setup --only dev,ai    # install specific categories
ball-setup --dry-run        # show what would be installed
```

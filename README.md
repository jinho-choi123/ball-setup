# ball-setup

One-line remote server provisioning: zsh, dev tools, and Claude Code.

```bash
curl -fsSL https://raw.githubusercontent.com/jinho-choi123/ball-setup/main/bootstrap.sh | bash
```

The bootstrap script installs [uv](https://docs.astral.sh/uv/) and runs `ball-setup` via `uvx` — no Python environment setup required.

## Supported OS

Ubuntu, Debian, Rocky Linux, macOS

## Usage

```
ball-setup [OPTIONS]

Options:
  --all          Install all tools non-interactively
  --only GROUPS  Comma-separated categories to install (e.g. --only dev,ai)
  --dry-run      Print what would be installed without making changes
  (no flags)     Launch interactive TUI to select tools
```

### Interactive TUI

Running `ball-setup` without flags opens a checkbox menu. Use space to toggle, `a` to select all, and enter to confirm. Essential tools (shell, base) are always included and cannot be deselected.

## What gets installed

| Category | Tools |
|----------|-------|
| essential | git, curl, unzip, ca-certificates, build-tools |
| shell | zsh, oh-my-zsh, zsh-autosuggestions, zsh-syntax-highlighting, zsh-completions |
| dev | tmux, jq, ripgrep, fd, fzf, htop, make, gh, lazygit |
| runtime | bun, fnm, Node.js LTS |
| ai | Claude Code, oh-my-claudecode + claude-mem plugins, custom skills |

`essential` and `shell` categories are locked — they always install regardless of flags.

All installs are idempotent — safe to re-run.

## Auth

After install, run `claude login` interactively. Requires a TTY.

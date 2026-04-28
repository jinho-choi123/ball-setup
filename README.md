# ball-setup

One-line remote server provisioning: zsh, dev tools, and Claude Code.

```bash
curl -fsSL https://raw.githubusercontent.com/jinho-choi123/ball-setup/main/setup.sh | bash
```

## Supported OS

Ubuntu, Debian, Rocky Linux, macOS

## What gets installed

| Category | Tools |
|----------|-------|
| Shell | zsh, oh-my-zsh, zsh-autosuggestions, zsh-syntax-highlighting, zsh-completions |
| Runtimes | fnm + Node.js LTS, bun, uv (Python) |
| Build | build-essential / Xcode CLI tools, make |
| CLI | git, curl, jq, ripgrep, fd, fzf, tmux, htop, lazygit, gh |
| AI | Claude Code + plugins (oh-my-claudecode, claude-mem, caveman, superpowers) + skills |

All installs are idempotent -- safe to re-run.

## Auth

Script runs `claude login` interactively. Requires TTY.

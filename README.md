# Remote Setup

One-shot script to provision a remote server with zsh, dev tools, and Claude Code.

## Supported OS

- Ubuntu
- Debian
- Rocky Linux
- macOS

## Usage

```bash
curl -fsSL https://raw.githubusercontent.com/jinho-choi123/ball-setup/main/setup.sh | bash
```

## What it installs

1. zsh + oh-my-zsh (default config)
2. git, unzip, uv, bun
3. Claude Code (via bun)
4. Plugins: oh-my-claudecode, claude-mem, caveman, superpowers
5. Skills: academic-researcher, caveman, gh-cli, grill-me, tavily-*, find-skills, pdf, karpathy-llm-wiki
6. Custom skills: linear-manager

## Authentication

Script runs `claude login` interactively for authentication.

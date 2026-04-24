#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────
# Remote Server Setup Script
# Usage: curl -fsSL https://raw.githubusercontent.com/<owner>/remote-setup/main/setup.sh | bash
# Supported OS: Ubuntu, Debian, macOS
# ──────────────────────────────────────────────

# Colors (disabled if not a terminal)
if [[ -t 1 ]]; then
    RED=$(tput setaf 1) GREEN=$(tput setaf 2) YELLOW=$(tput setaf 3) BLUE=$(tput setaf 4) RESET=$(tput sgr0)
else
    RED="" GREEN="" YELLOW="" BLUE="" RESET=""
fi

info()    { echo "${BLUE}▸${RESET} $*"; }
success() { echo "${GREEN}✓${RESET} $*"; }
warn()    { echo "${YELLOW}⚠${RESET} $*"; }
error()   { echo "${RED}✗${RESET} $*" >&2; }

trap 'error "Failed at line $LINENO"' ERR

command_exists() { command -v "$1" &>/dev/null; }

OS=""
detect_os() {
    # placeholder — implemented in Task 2
    :
}

pkg_install() {
    # placeholder — implemented in Task 2
    :
}

main() {
    info "Starting remote server setup..."
    detect_os
    # remaining calls added in later tasks
    success "Setup complete! Restart shell or run: exec zsh"
}

main "$@"

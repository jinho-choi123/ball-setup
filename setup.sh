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

APT_UPDATED=false
apt_update_once() {
    if [[ "$APT_UPDATED" == false && "$OS" != "macos" ]]; then
        info "Updating package index..."
        sudo apt-get update -y
        APT_UPDATED=true
    fi
}

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        case "$ID" in
            ubuntu) OS="ubuntu" ;;
            debian) OS="debian" ;;
            *) error "Unsupported OS: $ID"; exit 1 ;;
        esac
    else
        error "Unsupported OS: cannot detect"; exit 1
    fi
    info "Detected OS: $OS"
}

pkg_install() {
    case "$OS" in
        ubuntu|debian)
            apt_update_once
            sudo apt-get install -y "$@"
            ;;
        macos)
            if ! command_exists brew; then
                error "Homebrew not found. Install from https://brew.sh first."
                exit 1
            fi
            brew install "$@"
            ;;
    esac
}

install_zsh() {
    if command_exists zsh; then
        success "zsh already installed"
        return 0
    fi
    info "Installing zsh..."
    case "$OS" in
        ubuntu|debian) pkg_install zsh ;;
        macos) success "zsh is default on macOS"; return 0 ;;
    esac
    # Change default shell to zsh
    if [[ "$SHELL" != *"zsh"* ]]; then
        info "Changing default shell to zsh..."
        sudo chsh -s "$(which zsh)" "$(whoami)" 2>/dev/null || warn "Could not change shell — run manually: chsh -s \$(which zsh)"
    fi
    success "zsh installed"
}

install_ohmyzsh() {
    if [[ -d "$HOME/.oh-my-zsh" ]]; then
        success "oh-my-zsh already installed"
        return 0
    fi
    info "Installing oh-my-zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    success "oh-my-zsh installed"
}

install_tools() {
    info "Installing dev tools..."

    # git
    if command_exists git; then
        success "git already installed"
    else
        info "Installing git..."
        pkg_install git
    fi

    # unzip
    if command_exists unzip; then
        success "unzip already installed"
    else
        info "Installing unzip..."
        case "$OS" in
            ubuntu|debian) pkg_install unzip ;;
            macos) success "unzip built-in on macOS" ;;
        esac
    fi

    # uv
    if command_exists uv; then
        success "uv already installed"
    else
        info "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    # bun
    if command_exists bun; then
        success "bun already installed"
    else
        info "Installing bun..."
        curl -fsSL https://bun.sh/install | bash
    fi

    success "Dev tools ready"
}

main() {
    info "Starting remote server setup..."
    detect_os
    install_zsh
    install_ohmyzsh
    install_tools
    # remaining calls added in later tasks
    success "Setup complete! Restart shell or run: exec zsh"
}

main "$@"

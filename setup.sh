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

install_claude_code() {
    if command_exists claude; then
        success "Claude Code already installed"
    else
        info "Installing Claude Code..."
        bun install -g @anthropic-ai/claude-code
        success "Claude Code installed"
    fi

    # API key setup
    if grep -q "ANTHROPIC_API_KEY" "$HOME/.zshrc" 2>/dev/null; then
        success "ANTHROPIC_API_KEY already in .zshrc"
        return 0
    fi

    echo ""
    read -sp "Enter ANTHROPIC_API_KEY: " api_key
    echo ""
    if [[ -z "$api_key" ]]; then
        warn "No API key provided — set ANTHROPIC_API_KEY manually later"
        return 0
    fi
    echo "export ANTHROPIC_API_KEY=\"$api_key\"" >> "$HOME/.zshrc"
    export ANTHROPIC_API_KEY="$api_key"
    success "API key saved to .zshrc"
}

install_plugins() {
    info "Setting up Claude Code plugins..."

    # Register custom marketplaces
    info "Registering marketplaces..."
    claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode.git 2>/dev/null || true
    claude plugin marketplace add thedotmack/claude-mem 2>/dev/null || true
    claude plugin marketplace add JuliusBrussee/caveman 2>/dev/null || true
    success "Marketplaces registered"

    # Install plugins
    info "Installing plugins..."
    claude plugin install oh-my-claudecode@omc 2>/dev/null || true
    claude plugin install claude-mem@thedotmack 2>/dev/null || true
    claude plugin install caveman@caveman 2>/dev/null || true
    claude plugin install superpowers@claude-plugins-official 2>/dev/null || true
    success "Plugins installed"
}

install_skills() {
    info "Installing skills..."

    # Public skills via npx skills add
    local repos=(
        "shubhamsaboo/awesome-llm-apps"
        "juliusbrussee/caveman"
        "github/awesome-copilot"
        "mattpocock/skills"
        "tavily-ai/skills"
        "vercel-labs/skills"
        "anthropics/skills"
        "Astro-Han/karpathy-llm-wiki"
    )

    for repo in "${repos[@]}"; do
        info "Installing skills from $repo..."
        npx skills add "$repo" -g -y || warn "Failed to install from $repo"
    done
    success "Public skills installed"

    # Custom skills from this repo
    SCRIPT_REPO="https://github.com/<owner>/remote-setup.git"
    TMPDIR=$(mktemp -d)
    info "Cloning custom skills..."
    git clone --depth 1 "$SCRIPT_REPO" "$TMPDIR" 2>/dev/null

    if [[ -d "$TMPDIR/custom-skills" ]]; then
        mkdir -p "$HOME/.agents/skills"
        cp -r "$TMPDIR/custom-skills/"* "$HOME/.agents/skills/"
        success "Custom skills installed"
    else
        warn "No custom-skills directory found in repo"
    fi

    rm -rf "$TMPDIR"
}

main() {
    info "Starting remote server setup..."
    detect_os
    install_zsh
    install_ohmyzsh
    install_tools
    install_claude_code
    install_plugins
    install_skills
    echo ""
    success "Setup complete! Restart shell or run: exec zsh"
}

main "$@"

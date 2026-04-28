#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────
# Remote Server Setup Script
# Usage: curl -fsSL https://raw.githubusercontent.com/jinho-choi123/ball-setup/main/setup.sh | bash
# Supported OS: Ubuntu, Debian, Rocky Linux, macOS
# ──────────────────────────────────────────────

# Colors (disabled if not a terminal or tput unavailable)
RED="" GREEN="" YELLOW="" BLUE="" RESET=""
if [[ -t 1 ]] && command -v tput &>/dev/null && tput colors &>/dev/null; then
    RED=$(tput setaf 1 2>/dev/null) || true
    GREEN=$(tput setaf 2 2>/dev/null) || true
    YELLOW=$(tput setaf 3 2>/dev/null) || true
    BLUE=$(tput setaf 4 2>/dev/null) || true
    RESET=$(tput sgr0 2>/dev/null) || true
fi

info()    { echo "${BLUE}▸${RESET} $*"; }
success() { echo "${GREEN}✓${RESET} $*"; }
warn()    { echo "${YELLOW}⚠${RESET} $*"; }
error()   { echo "${RED}✗${RESET} $*" >&2; }

trap 'error "Failed at line $LINENO"' ERR

command_exists() { command -v "$1" &>/dev/null; }

# Use sudo only if not root
SUDO=""
if [[ "$(id -u)" -ne 0 ]]; then
    SUDO="sudo"
fi

OS=""

PKG_INDEX_UPDATED=false
pkg_update_once() {
    if [[ "$PKG_INDEX_UPDATED" == true ]]; then return 0; fi
    case "$OS" in
        ubuntu|debian)
            info "Updating package index..."
            $SUDO apt-get update -y
            ;;
        rocky)
            if ! $SUDO dnf repolist enabled | grep -q epel; then
                info "Enabling EPEL repository..."
                $SUDO dnf install -y epel-release
            fi
            info "Updating package index..."
            $SUDO dnf makecache -y
            ;;
        macos) ;;
    esac
    PKG_INDEX_UPDATED=true
}

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        case "$ID" in
            ubuntu) OS="ubuntu" ;;
            debian) OS="debian" ;;
            rocky|rocky-linux) OS="rocky" ;;
            *) error "Unsupported OS: $ID (from /etc/os-release)"; exit 1 ;;
        esac
    else
        error "Unsupported OS: cannot detect"; exit 1
    fi
    info "Detected OS: $OS"
}

pkg_install() {
    pkg_update_once
    case "$OS" in
        ubuntu|debian)
            $SUDO apt-get install -y "$@"
            ;;
        rocky)
            $SUDO dnf install -y "$@"
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
        ubuntu|debian|rocky) pkg_install zsh ;;
        macos) success "zsh is default on macOS"; return 0 ;;
    esac
    # Change default shell to zsh
    if [[ "$SHELL" != *"zsh"* ]]; then
        info "Changing default shell to zsh..."
        $SUDO chsh -s "$(which zsh)" "$(whoami)" 2>/dev/null || warn "Could not change shell — run manually: chsh -s \$(which zsh)"
    fi
    success "zsh installed"
}

install_ohmyzsh() {
    if [[ -d "$HOME/.oh-my-zsh" ]]; then
        success "oh-my-zsh already installed"
        return 0
    fi
    info "Installing oh-my-zsh..."
    local omz_installer
    omz_installer=$(mktemp)
    curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -o "$omz_installer"
    RUNZSH=no sh "$omz_installer" --unattended
    rm -f "$omz_installer"
    success "oh-my-zsh installed"
}

install_zsh_plugins() {
    local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

    # zsh-autosuggestions
    if [[ -d "$zsh_custom/plugins/zsh-autosuggestions" ]]; then
        success "zsh-autosuggestions already installed"
    else
        info "Installing zsh-autosuggestions..."
        git clone --depth 1 https://github.com/zsh-users/zsh-autosuggestions "$zsh_custom/plugins/zsh-autosuggestions"
    fi

    # zsh-syntax-highlighting
    if [[ -d "$zsh_custom/plugins/zsh-syntax-highlighting" ]]; then
        success "zsh-syntax-highlighting already installed"
    else
        info "Installing zsh-syntax-highlighting..."
        git clone --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting "$zsh_custom/plugins/zsh-syntax-highlighting"
    fi

    # zsh-completions
    if [[ -d "$zsh_custom/plugins/zsh-completions" ]]; then
        success "zsh-completions already installed"
    else
        info "Installing zsh-completions..."
        git clone --depth 1 https://github.com/zsh-users/zsh-completions "$zsh_custom/plugins/zsh-completions"
    fi

    # Update plugins list in .zshrc
    local zshrc="$HOME/.zshrc"
    if [[ -f "$zshrc" ]] && ! grep -q "zsh-autosuggestions" "$zshrc"; then
        info "Configuring zsh plugins in .zshrc..."
        local tmp
        tmp=$(mktemp)
        sed 's/^plugins=(.*/plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions)/' "$zshrc" > "$tmp"
        mv "$tmp" "$zshrc"
        success "zsh plugins configured"
    else
        success "zsh plugins already configured"
    fi
}

configure_shell_env() {
    local zshrc="$HOME/.zshrc"
    local marker="# ball-setup managed"

    if grep -q "$marker" "$zshrc" 2>/dev/null; then
        success "Shell environment already configured"
        return 0
    fi

    info "Configuring shell environment (PATH, fnm)..."
    cat >> "$zshrc" << 'SHELL_EOF'

# ball-setup managed
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.bun/bin:$PATH"
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env --shell zsh)"
SHELL_EOF
    success "Shell environment configured"
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
            ubuntu|debian|rocky) pkg_install unzip ;;
            macos) success "unzip built-in on macOS" ;;
        esac
    fi

    # uv
    if command_exists uv; then
        success "uv already installed"
    else
        info "Installing uv..."
        local uv_installer
        uv_installer=$(mktemp)
        curl -LsSf https://astral.sh/uv/install.sh -o "$uv_installer"
        sh "$uv_installer"
        rm -f "$uv_installer"
    fi

    # bun
    if command_exists bun; then
        success "bun already installed"
    else
        info "Installing bun..."
        local bun_installer
        bun_installer=$(mktemp)
        curl -fsSL https://bun.sh/install -o "$bun_installer"
        bash "$bun_installer"
        rm -f "$bun_installer"
    fi

    # fnm (Fast Node Manager)
    if command_exists fnm; then
        success "fnm already installed"
    else
        info "Installing fnm..."
        local fnm_installer
        fnm_installer=$(mktemp)
        curl -fsSL https://fnm.vercel.app/install -o "$fnm_installer"
        bash "$fnm_installer" --skip-shell
        rm -f "$fnm_installer"
        export PATH="$HOME/.local/share/fnm:$PATH"
        eval "$(fnm env)"
    fi

    # Node.js LTS via fnm
    if command_exists node; then
        success "node already installed ($(node -v))"
    else
        info "Installing Node.js LTS via fnm..."
        fnm install --lts
        fnm default lts-latest
        fnm use lts-latest
        success "Node.js $(node -v) installed"
    fi

    # curl
    if command_exists curl; then
        success "curl already installed"
    else
        info "Installing curl..."
        pkg_install curl
    fi

    # ca-certificates
    case "$OS" in
        ubuntu|debian|rocky)
            info "Ensuring ca-certificates..."
            pkg_install ca-certificates
            ;;
        macos) ;;
    esac

    # build tools (gcc, g++, make, etc.)
    case "$OS" in
        ubuntu|debian)
            if dpkg -s build-essential &>/dev/null 2>&1; then
                success "build-essential already installed"
            else
                info "Installing build-essential..."
                pkg_install build-essential
            fi
            ;;
        rocky)
            if command_exists gcc && command_exists make; then
                success "Development tools already installed"
            else
                info "Installing development tools..."
                $SUDO dnf groupinstall -y "Development Tools"
            fi
            ;;
        macos)
            if xcode-select -p &>/dev/null; then
                success "Xcode CLI tools already installed"
            else
                info "Installing Xcode CLI tools..."
                xcode-select --install 2>/dev/null || warn "Run 'xcode-select --install' manually"
            fi
            ;;
    esac

    # tmux
    if command_exists tmux; then
        success "tmux already installed"
    else
        info "Installing tmux..."
        pkg_install tmux
    fi

    # jq
    if command_exists jq; then
        success "jq already installed"
    else
        info "Installing jq..."
        pkg_install jq
    fi

    # ripgrep
    if command_exists rg; then
        success "ripgrep already installed"
    else
        info "Installing ripgrep..."
        pkg_install ripgrep
    fi

    # fd
    if command_exists fd || command_exists fdfind; then
        success "fd already installed"
    else
        info "Installing fd..."
        case "$OS" in
            ubuntu|debian)
                pkg_install fd-find
                $SUDO ln -sf "$(which fdfind)" /usr/local/bin/fd
                ;;
            rocky) pkg_install fd-find ;;
            macos) pkg_install fd ;;
        esac
    fi

    # fzf
    if command_exists fzf; then
        success "fzf already installed"
    else
        info "Installing fzf..."
        pkg_install fzf
    fi

    # htop
    if command_exists htop; then
        success "htop already installed"
    else
        info "Installing htop..."
        pkg_install htop
    fi

    # make (usually included in build tools, explicit check)
    if command_exists make; then
        success "make already installed"
    else
        info "Installing make..."
        pkg_install make
    fi

    # GitHub CLI (gh)
    if command_exists gh; then
        success "gh already installed"
    else
        info "Installing GitHub CLI..."
        case "$OS" in
            ubuntu|debian)
                curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
                    | $SUDO tee /usr/share/keyrings/githubcli-archive-keyring.gpg > /dev/null
                echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
                    | $SUDO tee /etc/apt/sources.list.d/github-cli.list > /dev/null
                PKG_INDEX_UPDATED=false
                pkg_install gh
                ;;
            rocky)
                $SUDO dnf install -y 'dnf-command(config-manager)' 2>/dev/null || true
                $SUDO dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
                $SUDO dnf install -y gh
                ;;
            macos)
                pkg_install gh
                ;;
        esac
    fi

    # lazygit
    if command_exists lazygit; then
        success "lazygit already installed"
    else
        info "Installing lazygit..."
        case "$OS" in
            macos)
                pkg_install lazygit
                ;;
            *)
                local lg_arch
                case "$(uname -m)" in
                    x86_64)       lg_arch="x86_64" ;;
                    aarch64|arm64) lg_arch="arm64" ;;
                    *)            warn "Unsupported arch for lazygit: $(uname -m)"; lg_arch="" ;;
                esac
                if [[ -n "$lg_arch" ]]; then
                    local lg_version lg_tmp
                    lg_version=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" \
                        | grep '"tag_name"' | sed 's/.*"v\(.*\)".*/\1/')
                    lg_tmp=$(mktemp -d)
                    curl -Lo "$lg_tmp/lazygit.tar.gz" \
                        "https://github.com/jesseduffield/lazygit/releases/download/v${lg_version}/lazygit_${lg_version}_Linux_${lg_arch}.tar.gz"
                    tar xf "$lg_tmp/lazygit.tar.gz" -C "$lg_tmp" lazygit
                    $SUDO install "$lg_tmp/lazygit" /usr/local/bin
                    rm -rf "$lg_tmp"
                fi
                ;;
        esac
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

    # Login to Claude
    info "Logging in to Claude Code..."
    claude login < /dev/tty
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

    # Public skills via bunx skills add
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
        bunx skills add "$repo" -g -y || warn "Failed to install from $repo"
    done
    success "Public skills installed"

    # Custom skills from this repo
    SCRIPT_REPO="https://github.com/jinho-choi123/ball-setup.git"
    TMPDIR=$(mktemp -d)
    info "Cloning custom skills..."
    git clone --depth 1 "$SCRIPT_REPO" "$TMPDIR" 2>/dev/null

    if [[ -d "$TMPDIR/custom-skills" ]]; then
        mkdir -p "$HOME/.agents/skills"
        cp -r "$TMPDIR/custom-skills/"* "$HOME/.agents/skills/"

        # Symlink each skill into ~/.claude/skills so Claude can find them
        mkdir -p "$HOME/.claude/skills"
        for skill_dir in "$HOME/.agents/skills"/*/; do
            local skill_name
            skill_name=$(basename "$skill_dir")
            if [[ ! -e "$HOME/.claude/skills/$skill_name" ]]; then
                ln -sf "$skill_dir" "$HOME/.claude/skills/$skill_name"
            fi
        done
        success "Custom skills installed and linked"
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
    install_zsh_plugins
    install_tools
    configure_shell_env
    install_claude_code
    install_plugins
    install_skills
    echo ""
    success "Setup complete! Restart shell or run: exec zsh"
}

main "$@"

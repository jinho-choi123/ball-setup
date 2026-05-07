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

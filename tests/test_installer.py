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

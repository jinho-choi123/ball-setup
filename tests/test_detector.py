from unittest.mock import patch, mock_open
import pytest
from ball_setup.detector import OS, detect_os, detect_arch, detect_system


class TestDetectOS:
    @patch("ball_setup.detector.platform.system", return_value="Darwin")
    def test_macos(self, _mock):
        assert detect_os() == OS.MACOS

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_ubuntu(self, _mock):
        content = 'ID=ubuntu\nVERSION_ID="24.04"\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                assert detect_os() == OS.UBUNTU

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_debian(self, _mock):
        content = 'ID=debian\nVERSION_ID="12"\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                assert detect_os() == OS.DEBIAN

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_rocky(self, _mock):
        content = 'ID="rocky"\nVERSION_ID="9.3"\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                assert detect_os() == OS.ROCKY

    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_unsupported_os(self, _mock):
        content = 'ID=arch\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                with pytest.raises(SystemExit, match="Unsupported OS: arch"):
                    detect_os()


class TestDetectArch:
    @patch("ball_setup.detector.platform.machine", return_value="x86_64")
    def test_x86_64(self, _mock):
        assert detect_arch() == "x86_64"

    @patch("ball_setup.detector.platform.machine", return_value="aarch64")
    def test_aarch64(self, _mock):
        assert detect_arch() == "arm64"

    @patch("ball_setup.detector.platform.machine", return_value="arm64")
    def test_arm64(self, _mock):
        assert detect_arch() == "arm64"

    @patch("ball_setup.detector.platform.machine", return_value="riscv64")
    def test_unsupported(self, _mock):
        with pytest.raises(SystemExit, match="Unsupported architecture"):
            detect_arch()


class TestDetectSystem:
    @patch("ball_setup.detector.os.getuid", return_value=0)
    @patch("ball_setup.detector.platform.machine", return_value="x86_64")
    @patch("ball_setup.detector.platform.system", return_value="Darwin")
    def test_root_macos(self, *_):
        system = detect_system()
        assert system.os == OS.MACOS
        assert system.arch == "x86_64"
        assert system.is_root is True

    @patch("ball_setup.detector.os.getuid", return_value=1000)
    @patch("ball_setup.detector.platform.machine", return_value="aarch64")
    @patch("ball_setup.detector.platform.system", return_value="Linux")
    def test_non_root_linux(self, *_):
        content = 'ID=ubuntu\n'
        with patch("ball_setup.detector.Path.exists", return_value=True):
            with patch("ball_setup.detector.Path.read_text", return_value=content):
                system = detect_system()
                assert system.os == OS.UBUNTU
                assert system.arch == "arm64"
                assert system.is_root is False

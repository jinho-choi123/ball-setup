from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

from .detector import OS

if TYPE_CHECKING:
    from .detector import System


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def sudo_prefix(system: System) -> list[str]:
    return [] if system.is_root else ["sudo"]


def run_cmd(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kwargs)


def run_shell(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, check=True, **kwargs)


class PackageManager:
    def __init__(self, system: System):
        self.system = system
        self._index_updated = False

    def ensure_index(self) -> None:
        if self._index_updated:
            return
        sudo = sudo_prefix(self.system)
        match self.system.os:
            case OS.UBUNTU | OS.DEBIAN:
                run_cmd([*sudo, "apt-get", "update", "-y"])
            case OS.ROCKY:
                result = subprocess.run(
                    [*sudo, "dnf", "repolist", "enabled"],
                    capture_output=True, text=True,
                )
                if "epel" not in result.stdout:
                    run_cmd([*sudo, "dnf", "install", "-y", "epel-release"])
                run_cmd([*sudo, "dnf", "makecache", "-y"])
            case OS.MACOS:
                if not command_exists("brew"):
                    raise SystemExit(
                        "Homebrew not found. Install from https://brew.sh first."
                    )
        self._index_updated = True

    def install(self, package: str) -> None:
        self.ensure_index()
        sudo = sudo_prefix(self.system)
        match self.system.os:
            case OS.UBUNTU | OS.DEBIAN:
                run_cmd([*sudo, "apt-get", "install", "-y", package])
            case OS.ROCKY:
                run_cmd([*sudo, "dnf", "install", "-y", package])
            case OS.MACOS:
                run_cmd(["brew", "install", package])

    def reset_index(self) -> None:
        self._index_updated = False

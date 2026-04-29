from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OS(Enum):
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    ROCKY = "rocky"
    MACOS = "macos"


@dataclass(frozen=True)
class System:
    os: OS
    arch: str
    is_root: bool


def _parse_os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            result[key] = value.strip('"')
    return result


def detect_os() -> OS:
    if platform.system() == "Darwin":
        return OS.MACOS
    info = _parse_os_release()
    os_id = info.get("ID", "")
    match os_id:
        case "ubuntu":
            return OS.UBUNTU
        case "debian":
            return OS.DEBIAN
        case "rocky" | "rocky-linux":
            return OS.ROCKY
        case _:
            raise SystemExit(f"Unsupported OS: {os_id or 'unknown'}")


def detect_arch() -> str:
    match platform.machine():
        case "x86_64" | "AMD64":
            return "x86_64"
        case "aarch64" | "arm64":
            return "arm64"
        case other:
            raise SystemExit(f"Unsupported architecture: {other}")


def detect_system() -> System:
    return System(
        os=detect_os(),
        arch=detect_arch(),
        is_root=os.getuid() == 0,
    )

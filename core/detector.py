"""Platform detection and backend selection."""

import os
import shutil

# Canonical platform identifiers used throughout the tool.
TERMUX = "termux"
DEBIAN = "debian"
FEDORA = "fedora"
ARCH = "arch"

# Maps a detected platform to the backend key used in packages.yaml.
BACKEND_KEYS = {
    TERMUX: "termux",
    DEBIAN: "apt",
    FEDORA: "dnf",
    ARCH: "pacman",
}


class PlatformInfo:
    def __init__(self, platform, backend_key, pretty_name):
        self.platform = platform
        self.backend_key = backend_key
        self.pretty_name = pretty_name

    def __repr__(self):
        return f"PlatformInfo(platform={self.platform!r}, backend={self.backend_key!r})"


def _read_os_release():
    path = "/etc/os-release"
    if not os.path.isfile(path):
        return {}
    fields = {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def _is_termux():
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix


def _match_os_release(fields):
    ids = fields.get("ID", "").lower()
    id_like = fields.get("ID_LIKE", "").lower()
    haystack = f"{ids} {id_like}"

    if any(tok in haystack for tok in ("debian", "ubuntu")):
        return DEBIAN
    if any(tok in haystack for tok in ("fedora", "rhel", "centos")):
        return FEDORA
    if any(tok in haystack for tok in ("arch", "blackarch", "manjaro")):
        return ARCH
    return None


def detect():
    """Return a PlatformInfo, or None if the platform is unrecognized."""
    if _is_termux():
        return PlatformInfo(TERMUX, BACKEND_KEYS[TERMUX], "Termux")

    fields = _read_os_release()
    platform = _match_os_release(fields)
    if platform is None:
        return None

    pretty = fields.get("PRETTY_NAME") or fields.get("NAME") or platform
    return PlatformInfo(platform, BACKEND_KEYS[platform], pretty)


def has_root():
    """True if running as root or if a privilege-escalation helper is present."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return True
    return shutil.which("sudo") is not None or shutil.which("tsu") is not None

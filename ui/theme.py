"""Centralized colors and status markers. No emojis anywhere."""

from core.packageManager import (
    ALREADY_INSTALLED,
    INSTALLED,
    UPGRADED,
    SKIPPED,
    FAILED,
)

# rich style strings keyed by status.
STATUS_COLORS = {
    ALREADY_INSTALLED: "green",
    INSTALLED: "green",
    UPGRADED: "cyan",
    SKIPPED: "yellow",
    FAILED: "red",
}

# Plain-text markers used where color alone is not enough.
MARKER_OK = "[OK]"
MARKER_FAIL = "[FAIL]"
MARKER_SKIP = "[SKIP]"
MARKER_LOCKED = "[LOCKED]"

BRAND = "bold cyan"
ACCENT = "magenta"
DIM = "dim"
HEADING = "bold white"
WARN = "yellow"
ERROR = "bold red"


def status_style(status):
    return STATUS_COLORS.get(status, "white")


def status_label(status):
    return status

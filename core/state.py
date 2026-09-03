"""Tracks cross-run state markers under .state/."""

import os
from datetime import datetime

_STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".state")
_PRIMARY_MARKER = os.path.join(_STATE_DIR, "primary_completed")


def mark_primary_completed():
    """Record that a Primary run finished. Best-effort; never raises."""
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
        with open(_PRIMARY_MARKER, "w", encoding="utf-8") as fh:
            fh.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    except OSError:
        pass


def primary_completed():
    """True if a Primary run has completed at least once."""
    return os.path.isfile(_PRIMARY_MARKER)

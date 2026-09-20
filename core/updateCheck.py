"""Checks GitHub releases for a newer version; caches the finding for startup. Inform-only."""

import json
import urllib.request
from collections import namedtuple
from datetime import datetime, timedelta

from core import state

_RELEASES_API = "https://api.github.com/repos/Antech-greyhat/LinuxSetupPro/releases/latest"
# Human-facing releases page, used as a fallback when the API omits the release URL.
RELEASES_PAGE = "https://github.com/Antech-greyhat/LinuxSetupPro/releases/latest"

# GitHub rejects API requests without a User-Agent; keep the read anonymous otherwise.
_HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "LinuxSetupPro"}
_DEFAULT_TIMEOUT = 5

# A cached "update available" finding only surfaces at startup while it is at most this old.
_CACHE_WINDOW = timedelta(days=7)
_TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"

# Statuses returned by check_for_update.
UPDATE_AVAILABLE = "update-available"
UP_TO_DATE = "up-to-date"
CHECK_FAILED = "check-failed"

# Outcome of one update check. latest/url are set only when known; error only on failure.
UpdateResult = namedtuple("UpdateResult", "status current latest url error")


def check_for_update(current_version, timeout=_DEFAULT_TIMEOUT):
    """Query GitHub for the latest release and compare it to current_version.

    Returns an UpdateResult; a network, HTTP, or parse failure yields CHECK_FAILED and never
    raises. A newer version is cached so startup can surface it without another network call;
    finding the tool already current clears any stale cache instead.
    """
    try:
        tag, url = _fetch_latest(timeout)
    except Exception as exc:  # network/HTTP/JSON — an update check must never crash the tool
        return UpdateResult(CHECK_FAILED, current_version, None, None, str(exc))
    if not tag:
        return UpdateResult(CHECK_FAILED, current_version, None, None, "no release tag returned")
    if is_newer(tag, current_version):
        state.write_update_cache(tag, url or RELEASES_PAGE)
        return UpdateResult(UPDATE_AVAILABLE, current_version, tag, url or RELEASES_PAGE, None)
    state.clear_update_cache()
    return UpdateResult(UP_TO_DATE, current_version, tag, None, None)


def startup_notice(current_version):
    """One-line notice when a recent cache shows a newer version, else None. Reads no network.

    A cache that has expired, is unreadable, or no longer outranks the running version is
    cleared, so a stale notice never lingers after the user has actually updated.
    """
    cache = state.read_update_cache()
    if not cache:
        return None
    latest = cache.get("latest", "")
    if not is_newer(latest, current_version) or _is_expired(cache.get("checked_at", "")):
        state.clear_update_cache()
        return None
    return (f'A newer version ({latest}) is available — '
            'run "Check for Updates" from the menu for details.')


def _fetch_latest(timeout):
    """Fetch (tag_name, html_url) for the latest release from GitHub. Raises on any failure."""
    request = urllib.request.Request(_RELEASES_API, headers=_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("tag_name") or "", data.get("html_url") or ""


def is_newer(latest, current):
    """True when latest is a strictly higher version than current. Unparseable latest is not newer."""
    latest_parts = _parse_version(latest)
    if not latest_parts:
        return False
    current_parts = _parse_version(current)
    # Pad to equal length so 2.1 and 2.1.0 compare equal rather than one outranking the other.
    length = max(len(latest_parts), len(current_parts))
    latest_parts += (0,) * (length - len(latest_parts))
    current_parts += (0,) * (length - len(current_parts))
    return latest_parts > current_parts


def _parse_version(text):
    """Parse a version string into a tuple of ints, ignoring a leading 'v' and any pre-release suffix."""
    core = str(text).strip().lstrip("vV").split("-")[0].split("+")[0]
    parts = []
    for chunk in core.split("."):
        if not chunk.isdigit():
            break
        parts.append(int(chunk))
    return tuple(parts)


def _is_expired(checked_at):
    """True when a cache timestamp is missing, unparseable, or older than the cache window."""
    try:
        stamp = datetime.strptime(checked_at, _TIMESTAMP_FMT)
    except (ValueError, TypeError):
        return True
    return datetime.now() - stamp > _CACHE_WINDOW

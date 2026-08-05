"""Interactive prompts: confirmations, pickers, and the secondary checkbox menu."""

import sys

import questionary
from questionary import Choice

from ui import theme

_SELECT_ALL = "__select_all__"


def _interactive():
    return sys.stdin.isatty() and sys.stdout.isatty()


def confirm(message, default=False):
    if not _interactive():
        return default
    answer = questionary.confirm(message, default=default).ask()
    return bool(answer)


def text(message, default=""):
    if not _interactive():
        return default
    answer = questionary.text(message, default=default).ask()
    return answer if answer is not None else default


def select(message, options, default=None):
    """Single-select. options is a list of (value, label) tuples."""
    if not _interactive():
        return default if default is not None else options[0][0]
    choices = [Choice(title=label, value=value) for value, label in options]
    answer = questionary.select(message, choices=choices).ask()
    return answer if answer is not None else (default if default is not None else options[0][0])


def editor_multiselect(entries):
    """Multi-select editors. entries is a list of catalog dicts. Returns selected names."""
    if not _interactive():
        return []
    choices = []
    for entry in entries:
        label = entry["name"]
        if entry.get("locked"):
            label = f"{entry['name']} {theme.MARKER_LOCKED}"
        choices.append(Choice(title=f"{label} - {entry.get('description', '')}", value=entry["name"]))
    selected = questionary.checkbox("Select editors to install (space to toggle, enter to confirm):",
                                    choices=choices).ask()
    return selected or []


def secondary_menu(entries):
    """Checkbox menu over secondary tools with a select-all option. Returns selected names."""
    if not _interactive():
        return []
    choices = [Choice(title="[Select all]", value=_SELECT_ALL)]
    for entry in entries:
        name = entry["name"]
        marker = f" {theme.MARKER_LOCKED}" if entry.get("locked") else ""
        title = f"{name}{marker} - {entry.get('description', '')}"
        choices.append(Choice(title=title, value=name))

    selected = questionary.checkbox(
        "Select security tools to install (space to toggle, enter to confirm):",
        choices=choices,
    ).ask()
    selected = selected or []
    if _SELECT_ALL in selected:
        return [entry["name"] for entry in entries]
    return selected

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


def _read_choice(prompt, valid):
    """Prompt until the user enters one of valid (case-insensitive), or None on cancel."""
    if not _interactive():
        return None
    while True:
        try:
            answer = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if answer in valid:
            return answer
        print("  Please enter one of: " + ", ".join(sorted(valid)))


def main_menu(console):
    """Render the top-level menu and return the chosen number as a string, or None to exit."""
    if not _interactive():
        return None
    console.print()
    console.print("LinuxSetupPro — Main Menu", style=theme.HEADING)
    console.print()
    console.print("  1) Run Primary Setup        (Basic / Required — install this first)", highlight=False)
    console.print("  2) Run Secondary Setup      (Advanced/Security Tools — requires Primary)", highlight=False)
    console.print("  3) Generate Terminal Banner (Installs figlet/lolcat if needed)", highlight=False)
    console.print("  4) View Last Report", highlight=False)
    console.print("  5) Exit", highlight=False)
    console.print()
    return _read_choice("  > ", {"1", "2", "3", "4", "5"})


def report_menu(console):
    """Render the View Last Report submenu and return the chosen option, or None to go back."""
    if not _interactive():
        return None
    console.print()
    console.print("     4a) Primary Report", highlight=False)
    console.print("     4b) Secondary Report", highlight=False)
    console.print("     4c) Both Reports", highlight=False)
    console.print("     4d) Back to Main Menu", highlight=False)
    console.print()
    return _read_choice("     > ", {"4a", "4b", "4c", "4d"})

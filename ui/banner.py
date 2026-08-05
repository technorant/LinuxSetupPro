"""Startup and end-of-run banners with the developer info block."""

import shutil
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core import detector
from ui import theme

_LOGO = r"""
 _     _                  ____       _               ____
| |   (_)_ __  _   ___  _/ ___|  ___| |_ _   _ _ __ |  _ \ _ __ ___
| |   | | '_ \| | | \ \/ \___ \ / _ \ __| | | | '_ \| |_) | '__/ _ \
| |___| | | | | |_| |>  <  ___) |  __/ |_| |_| | |_) |  __/| | | (_) |
|_____|_|_| |_|\__,_/_/\_\|____/ \___|\__|\__,_| .__/|_|   |_|  \___/
                                               |_|
""".strip("\n")

_DEV = [
    ("Author", "Antech"),
    ("GitHub", "https://github.com/Antech-greyhat"),
    ("Telegram", "https://t.me/AntechDevSecOps"),
    ("X", "https://x.com/Antech1629"),
    ("LinkedIn", "https://www.linkedin.com/in/antony-mwendwa-07679336b"),
]


def show_startup(version, console=None):
    console = console or Console()
    console.print(Text(_LOGO, style=theme.BRAND))
    console.print(Text(f"LinuxSetupPro v{version}", style=theme.HEADING))
    console.print()
    for label, value in _DEV:
        line = Text()
        line.append(f"{label:<9}", style=theme.ACCENT)
        line.append(value, style="white")
        console.print(line)
    console.print()
    console.print(Text("If this tool saves you time, a star on GitHub is appreciated.", style=theme.DIM))
    console.print()


def show_end(version, platform_info, console=None, ask_open=True, input_fn=input):
    console = console or Console()
    console.print()
    console.rule("Done", style=theme.BRAND)
    console.print(Text(f"LinuxSetupPro v{version} by Antech", style=theme.HEADING))
    console.print(Text("GitHub:   https://github.com/Antech-greyhat", style="white"))
    console.print(Text("Telegram: https://t.me/AntechDevSecOps", style="white"))
    console.print()
    console.print(Text("Support development:", style=theme.HEADING))
    console.print(Text("  GitHub: https://github.com/Antech-greyhat", style="white"))
    console.print()

    if not ask_open:
        return
    answer = input_fn("Open in browser now? [y/n] ").strip().lower()
    if answer in ("y", "yes"):
        _open_url("https://github.com/Antech-greyhat", platform_info)


def _open_url(url, platform_info):
    if platform_info and platform_info.platform == detector.TERMUX and shutil.which("termux-open-url"):
        opener = ["termux-open-url", url]
    elif shutil.which("xdg-open"):
        opener = ["xdg-open", url]
    else:
        return
    try:
        subprocess.Popen(opener, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass

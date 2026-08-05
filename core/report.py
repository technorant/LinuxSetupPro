"""Builds the terminal report and writes JSON and plain-text logs per run."""

import json
import os
from datetime import datetime

from rich.console import Console
from rich.text import Text

from ui import theme
from core.packageManager import FAILED

_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


class PackageRecord:
    """One package's outcome, carrying enough detail for both the report and the JSON log."""

    def __init__(self, category, name, description, status, locked=False,
                 result=None, cause=None, suggestion=None, available=True):
        self.category = category
        self.name = name
        self.description = description
        self.status = status
        self.locked = locked
        self.result = result
        self.cause = cause
        self.suggestion = suggestion
        self.available = available

    def as_dict(self):
        data = {
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "locked": self.locked,
            "available": self.available,
            "cause": self.cause,
            "suggestion": self.suggestion,
        }
        if self.result is not None:
            data["operation"] = self.result.as_dict()
        return data


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_log_dir():
    os.makedirs(_LOG_DIR, exist_ok=True)


def _group_by_category(records):
    grouped = {}
    for record in records:
        grouped.setdefault(record.category, []).append(record)
    return grouped


class Report:
    def __init__(self, kind, platform_name, backend_key, console=None):
        self.kind = kind  # "primary" or "secondary"
        self.platform_name = platform_name
        self.backend_key = backend_key
        self.console = console or Console()

    def render(self, records, elapsed, log_path, notes=None):
        self.console.print()
        self.console.rule(f"{self.kind.capitalize()} report", style=theme.BRAND)
        for category, items in _group_by_category(records).items():
            self.console.print(Text(category, style=theme.HEADING))
            for record in items:
                self._render_line(record)
            self.console.print()

        if notes:
            for note in notes:
                self.console.print(Text(note, style=theme.DIM))
            self.console.print()

        self._render_summary(records, elapsed)
        self.console.print(Text(f"Full log: {log_path}", style=theme.DIM))

    def _render_line(self, record):
        line = Text("  ")
        line.append(f"{record.name} ", style="white")
        if record.locked:
            line.append(f"{theme.MARKER_LOCKED} ", style=theme.WARN)
        line.append(record.status, style=theme.status_style(record.status))
        line.append(f"  {record.description}", style=theme.DIM)
        self.console.print(line)

        if record.status == FAILED:
            if record.cause:
                self.console.print(Text(f"    reason: {record.cause}", style=theme.WARN))
                self.console.print(Text(f"    suggestion: {record.suggestion}", style=theme.WARN))
            else:
                raw = (record.result.stderr.strip() if record.result else "").splitlines()
                snippet = raw[-1] if raw else "no stderr captured"
                self.console.print(Text(f"    reason: unrecognized error", style=theme.WARN))
                self.console.print(Text(f"    stderr: {snippet}", style=theme.DIM))
                self.console.print(Text("    see the JSON log for full output", style=theme.DIM))

    def _render_summary(self, records, elapsed):
        counts = {}
        for record in records:
            counts[record.status] = counts.get(record.status, 0) + 1
        summary = Text("Summary: ", style=theme.HEADING)
        parts = [f"{status}={count}" for status, count in counts.items()]
        summary.append(", ".join(parts) if parts else "nothing to do")
        self.console.print(summary)
        self.console.print(Text(f"Elapsed: {elapsed:.1f}s", style=theme.DIM))

    def save(self, records, elapsed, notes=None):
        """Write JSON and plain-text logs. Returns the .log path for display."""
        _ensure_log_dir()
        stamp = _timestamp()
        json_path = os.path.join(_LOG_DIR, f"{stamp}_{self.kind}.json")
        log_path = os.path.join(_LOG_DIR, f"{stamp}_{self.kind}.log")

        payload = {
            "kind": self.kind,
            "platform": self.platform_name,
            "backend": self.backend_key,
            "timestamp": stamp,
            "elapsed_seconds": round(elapsed, 3),
            "packages": [r.as_dict() for r in records],
            "notes": notes or [],
        }
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(self._plain_text(records, elapsed, notes))

        return log_path, json_path

    def _plain_text(self, records, elapsed, notes):
        lines = [f"{self.kind.upper()} REPORT",
                 f"Platform: {self.platform_name} (backend: {self.backend_key})",
                 ""]
        for category, items in _group_by_category(records).items():
            lines.append(category)
            for record in items:
                marker = f" {theme.MARKER_LOCKED}" if record.locked else ""
                lines.append(f"  {record.name}{marker}  {record.status}  {record.description}")
                if record.status == FAILED:
                    if record.cause:
                        lines.append(f"    reason: {record.cause}")
                        lines.append(f"    suggestion: {record.suggestion}")
                    elif record.result and record.result.stderr:
                        tail = record.result.stderr.strip().splitlines()
                        lines.append(f"    stderr: {tail[-1] if tail else ''}")
            lines.append("")
        if notes:
            lines.extend(notes)
            lines.append("")
        counts = {}
        for record in records:
            counts[record.status] = counts.get(record.status, 0) + 1
        lines.append("Summary: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
        lines.append(f"Elapsed: {elapsed:.1f}s")
        return "\n".join(lines) + "\n"


def latest_log():
    """Return the path to the most recent .log file, or None."""
    if not os.path.isdir(_LOG_DIR):
        return None
    logs = [os.path.join(_LOG_DIR, f) for f in os.listdir(_LOG_DIR) if f.endswith(".log")]
    if not logs:
        return None
    return max(logs, key=os.path.getmtime)

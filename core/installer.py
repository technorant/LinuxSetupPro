"""Drives install sequences using the selected backend. Holds no platform commands."""

import os

import yaml

from core.packageManager import (
    OperationResult,
    SKIPPED,
    FAILED,
)
from core.progress import ProgressRenderer
from core.report import PackageRecord

_CATALOG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "packages.yaml")


def load_catalog(path=_CATALOG):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def resolve_package(entry, backend_key):
    """Return the backend-specific package name, or None if unavailable there."""
    return entry.get(backend_key)


class Installer:
    def __init__(self, backend, classifier, console, verbose=False):
        self.backend = backend
        self.classifier = classifier
        self.console = console
        self.verbose = verbose
        self.progress = ProgressRenderer(console)

    def install_sequence(self, entries, start_index=1, total=None):
        """Install each entry in order. Returns a list of PackageRecord."""
        total = total if total is not None else len(entries)
        records = []
        for offset, entry in enumerate(entries):
            index = start_index + offset
            records.append(self._install_one(entry, index, total))
        return records

    def _install_one(self, entry, index, total):
        name = entry["name"]
        description = entry.get("description", "")
        locked = bool(entry.get("locked", False))
        pkg = resolve_package(entry, self.backend.key)

        if pkg is None:
            reason = f"not packaged for the {self.backend.key} backend"
            result = OperationResult(name, SKIPPED, stdout=reason)
            self._echo_unavailable(index, total, name)
            return PackageRecord(entry.get("_category", ""), name, description,
                                 SKIPPED, locked, result,
                                 cause=reason,
                                 suggestion="Install it from a Linux chroot (proot-distro) or a language package manager.",
                                 available=False)

        result = self._run_install(index, total, name, pkg)
        record = PackageRecord(entry.get("_category", ""), name, description,
                               result.status, locked, result)
        if result.status == FAILED:
            classified = self.classifier.classify(result.stderr)
            if classified:
                record.cause, record.suggestion = classified
        return record

    def _run_install(self, index, total, name, pkg):
        operation = lambda: self.backend.install(pkg)
        if self.verbose:
            self.console.print(f"[{index}/{total}] installing {name} ({pkg})")
            result = operation()
            if result.stdout:
                self.console.print(result.stdout)
            if result.stderr:
                self.console.print(result.stderr)
            self.console.print(f"  -> {result.status}")
            return result
        return self.progress.run(index, total, "install", name, operation)

    def _echo_unavailable(self, index, total, name):
        self.console.print(f"[{index}/{total}] {name} skipped (not available on this platform)")


def flatten_primary(catalog):
    """Yield (category, entry) for primary categories in defined order."""
    for block in catalog.get("primary", []):
        category = block.get("category", "")
        for entry in block.get("packages", []):
            entry = dict(entry)
            entry["_category"] = category
            yield category, entry


def flatten_secondary(catalog):
    for block in catalog.get("secondary", []):
        category = block.get("category", "")
        for entry in block.get("packages", []):
            entry = dict(entry)
            entry["_category"] = category
            yield category, entry

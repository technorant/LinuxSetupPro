"""Health check: audits tracked tool-installed packages against what is on the system."""

from collections import namedtuple

from core import state

# One audited package: its label, backend name, category, description, and whether it is still present.
PackageStatus = namedtuple("PackageStatus", "name package category description present")

# Result of a health check: every package audited, plus the subset found missing.
HealthReport = namedtuple("HealthReport", "checked discrepancies")


def run_health_check(backend, backend_key):
    """Re-check every tracked tool-installed package against the backend. Returns a HealthReport.

    Only packages this tool installed are recorded in the manifest, so pre-existing
    ('already installed') packages are never audited or flagged as drift.
    """
    checked = []
    for entry in state.list_installed(backend_key):
        package = entry.get("package") or entry.get("name", "")
        checked.append(PackageStatus(
            entry.get("name", package), package, entry.get("category", ""),
            entry.get("description", ""), _is_present(backend, package)))
    discrepancies = [status for status in checked if not status.present]
    return HealthReport(checked, discrepancies)


def _is_present(backend, package):
    """True if the backend still reports package installed. A check that errors is not treated as drift."""
    try:
        return bool(backend.is_installed(package))
    except Exception:
        # An unexpected backend error must not turn an unverifiable package into a false discrepancy.
        return True

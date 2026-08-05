"""Matches captured stderr against known error patterns."""

import os
import re

import yaml

_CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "errorPatterns.yaml")


class ErrorClassifier:
    def __init__(self, backend_key, patterns_path=_CONFIG):
        self.backend_key = backend_key
        self._patterns = self._load(patterns_path)

    def _load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except (OSError, yaml.YAMLError):
            return []
        compiled = []
        for entry in data.get("patterns", []):
            try:
                regex = re.compile(entry["match"], re.IGNORECASE)
            except (re.error, KeyError, TypeError):
                continue
            compiled.append((regex, entry.get("cause", ""), entry.get("suggestion", {})))
        return compiled

    def classify(self, stderr):
        """Return (cause, suggestion) for the first matching pattern, else None."""
        if not stderr:
            return None
        for regex, cause, suggestion in self._patterns:
            if regex.search(stderr):
                return cause, self._pick_suggestion(suggestion)
        return None

    def _pick_suggestion(self, suggestion):
        if not isinstance(suggestion, dict):
            return str(suggestion)
        return suggestion.get(self.backend_key) or suggestion.get("all") or ""

"""Detects the shell rc file and manages marked, idempotent config blocks."""

import os

BEGIN_MARKER = "# BEGIN linux-setup-pro banner"
END_MARKER = "# END linux-setup-pro banner"

EDITOR_BEGIN = "# BEGIN linux-setup-pro editor"
EDITOR_END = "# END linux-setup-pro editor"

# The instant-prompt block always sources a p10k-instant-prompt cache file.
_P10K_SOURCE = "p10k-instant-prompt"


def detect_shell():
    """Return the shell base name from $SHELL, defaulting to bash."""
    shell = os.environ.get("SHELL", "")
    base = os.path.basename(shell)
    return base if base else "bash"


def rc_path_for_shell(shell=None):
    shell = shell or detect_shell()
    home = os.path.expanduser("~")
    if shell == "zsh":
        return os.path.join(home, ".zshrc")
    return os.path.join(home, ".bashrc")


def _read_lines(path):
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def _write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip("\n") + "\n")


def _strip_block(lines, begin, end):
    """Remove an existing begin/end block, keeping everything else."""
    out, skipping = [], False
    for line in lines:
        if line.strip() == begin:
            skipping = True
            continue
        if line.strip() == end:
            skipping = False
            continue
        if not skipping:
            out.append(line)
    return out


def _p10k_end_index(lines):
    """Return the index just after a p10k instant-prompt block, or None if absent."""
    source_idx = None
    for i, line in enumerate(lines):
        if _P10K_SOURCE in line:
            source_idx = i
    if source_idx is None:
        return None
    # The source line lives inside an `if ... fi` guard; insert after its `fi`.
    for j in range(source_idx, min(source_idx + 6, len(lines))):
        if lines[j].strip() == "fi":
            return j + 1
    return source_idx + 1


def insert_banner_block(body_lines, shell=None):
    """Insert or replace the banner block. Returns the rc path written."""
    path = rc_path_for_shell(shell)
    lines = _read_lines(path)
    lines = _strip_block(lines, BEGIN_MARKER, END_MARKER)

    block = [BEGIN_MARKER] + body_lines + [END_MARKER]
    insert_at = _p10k_end_index(lines)
    if insert_at is None:
        new_lines = block + lines
    else:
        new_lines = lines[:insert_at] + block + lines[insert_at:]

    _write_lines(path, new_lines)
    return path


def remove_banner_block(shell=None):
    """Remove the banner block from the rc file. Returns (path, removed)."""
    path = rc_path_for_shell(shell)
    lines = _read_lines(path)
    if not any(line.strip() == BEGIN_MARKER for line in lines):
        return path, False
    _write_lines(path, _strip_block(lines, BEGIN_MARKER, END_MARKER))
    return path, True


def set_editor(editor, shell=None):
    """Persist an EDITOR export inside a marked block. Returns the rc path."""
    path = rc_path_for_shell(shell)
    lines = _strip_block(_read_lines(path), EDITOR_BEGIN, EDITOR_END)
    block = [EDITOR_BEGIN, f'export EDITOR="{editor}"', f'export VISUAL="{editor}"', EDITOR_END]
    _write_lines(path, lines + block)
    return path


def get_editor(shell=None):
    """Return the EDITOR value from our editor block, or None if it was never set."""
    inside = False
    for line in _read_lines(rc_path_for_shell(shell)):
        stripped = line.strip()
        if stripped == EDITOR_BEGIN:
            inside = True
        elif stripped == EDITOR_END:
            inside = False
        elif inside and stripped.startswith("export EDITOR="):
            return stripped[len("export EDITOR="):].strip().strip('"').strip("'") or None
    return None


def has_p10k(shell=None):
    return _p10k_end_index(_read_lines(rc_path_for_shell(shell))) is not None

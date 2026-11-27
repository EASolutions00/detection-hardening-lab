"""The code version of this repository, for the run records and the analyser version.

A run record used to name no code at all (outside review, point 12; docs/FREEZE-DATES.md section 5). A commit hash
alone is not enough: the working tree may hold changes that were never committed, so the code that ran may not equal
the commit. `code_version` therefore returns two things, the commit and whether a file under `src/` or `lab/` differs
from it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

UNKNOWN = "unknown"


def code_version(repo: str | Path) -> tuple[str, bool | None]:
    """(short commit hash, changed) of the code in `repo`.

    `changed` is True when a file under `src/` or `lab/` differs from that commit or is new and not yet committed
    (the code that ran may not equal the commit), False when none does, and None when git could not be asked.
    Returns ("unknown", None) when git is missing or `repo` is not a repository. Read only."""
    base = ["git", "-C", str(repo)]
    try:
        head = subprocess.run([*base, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=30)
        commit = head.stdout.strip()
        if head.returncode != 0 or not commit:
            return UNKNOWN, None
        status = subprocess.run([*base, "status", "--porcelain", "--", "src", "lab"],
                                capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return UNKNOWN, None
    return commit, (bool(status.stdout.strip()) if status.returncode == 0 else None)


def describe(commit: str | None, changed: bool | None) -> str:
    """For a report line: "abc1234", "abc1234 (files changed since)", or "not recorded"."""
    if not commit:
        return "not recorded"
    return commit + (" (files changed since)" if changed else "")

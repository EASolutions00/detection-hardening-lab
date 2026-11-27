"""The hash of the Wazuh rule export, computed from the files.

DECISIONS (pinned table, 2026-11-13) pins the rule export by one value: SHA256 over the lines
"file SHA256, two spaces, relative path", one per file, each ending in a line feed. The details the pinned table
does not state, found 2026-11-28 by reproducing the pinned value from the real export:
- the path is relative to the unpacked export folder (`wazuh-4.14.7`) and uses forward slashes, for example
  `ruleset/rules/0010-rules_config.xml` and `etc/rules/local_rules.xml`;
- the file hash is lower-case hexadecimal;
- the lines are sorted by path (not by file hash).

Until 2026-11-28 the value was typed into `catalog.parameters()` and never computed again (outside review, point 12).
`pipeline.compare` now computes it from the folder it reads the rules from, and refuses to run when it differs from
the value the runs were captured with. The method reproduces the pinned value `a3f9749e...2939` from the real
export (169 files), so the typed value was right (WORKLOG 2026-11-28).
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def file_lines(folder: str | Path) -> list[str]:
    """One "SHA256, two spaces, relative path" line per file under `folder`, sorted by path."""
    root = Path(folder)
    if not root.is_dir():
        raise ValueError(f"not a folder: {root}")
    files = sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix())
    return [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}" for p in files]


def rule_folder_sha256(folder: str | Path) -> str:
    """The hash of the rule export in `folder`: SHA256 over its `file_lines`, each ending in a line feed."""
    text = "".join(line + "\n" for line in file_lines(folder))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

"""When each run was captured, from its own run_manifest.json. Read only.

    .venv/Scripts/python.exe tools/run_times.py --summary data/summaries/eval-2026-11-26/run-times.txt

docs/FREEZE-DATES.md says which decision came before which data. This prints the data side of that order:
for every spike, trial and evaluation run, the start and finish of the run, its capture window, whether its
record holds the void rule's check (record.run_checks; the rule was built 2026-11-26 19:29 UTC), the first
8 characters of its parameters hash, and the code version it recorded (record.code_commit, recorded since
2026-11-28, fix 6 of the outside review; earlier runs recorded none). All times are the host's clock, in
UTC. It writes nothing except the --summary file, if one is given.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parent.parent / "data" / "runs"
GROUPS = (
    ("spike (2026-11-16; the feasibility study, a different stimulus)", ("spike-", "test-")),
    ("trial (2026-11-26, Phase D; not evaluation data)", ("trial-",)),
    ("evaluation (2026-11-26; the study's 26 runs)", ("eval-",)),
)


def clock(stamp: str | None) -> str:
    """'2026-11-26T17:55:17.123456' to '2026-11-26 17:55:17'."""
    return stamp[:19].replace("T", " ") if stamp else "-"


def describe(folder: Path) -> dict | None:
    manifest = folder / "run_manifest.json"
    if not manifest.exists():
        return None
    data = json.loads(manifest.read_text(encoding="utf-8"))
    rec = data.get("record", {})
    window = rec.get("window", {})
    code = rec.get("code_commit")
    return {
        "run": folder.name,
        "start": rec.get("run_started_host_utc"),
        "finish": rec.get("run_finished_host_utc"),
        "window": f"{(window.get('start') or '-')[11:19]}..{(window.get('end') or '-')[11:19]}" if window else "-",
        "checks": "yes" if rec.get("run_checks") else "no",
        "hash": (data.get("parameters_sha256") or "-")[:8],
        "code": (code + ("+changed files" if rec.get("code_dirty") else "")) if code else "not recorded",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="When each run was captured, from its run_manifest.json.")
    ap.add_argument("--summary", help="also write the output to this file")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lines: list[str] = ["RUN TIMES, from each run's run_manifest.json (host clock, UTC; tools/run_times.py)", ""]
    for title, prefixes in GROUPS:
        rows = [r for d in sorted(RUNS.iterdir()) if d.is_dir() and d.name.startswith(prefixes)
                for r in [describe(d)] if r]
        rows.sort(key=lambda r: r["start"] or "")
        lines.append(f"{title}: {len(rows)} runs")
        lines.append(f"  {'run':<18} {'started':<19} {'finished':<19} {'window':<19} {'checks':<6} {'hash':<8} code version")
        for r in rows:
            lines.append(f"  {r['run']:<18} {clock(r['start']):<19} {clock(r['finish']):<19} {r['window']:<19} "
                         f"{r['checks']:<6} {r['hash']:<8} {r['code']}")
        lines.append("")
    lines.append("checks: yes = the record holds the void rule's check (record.run_checks).")
    lines.append("code version: the git commit recorded by the run itself; 'not recorded' for every run before 2026-11-28.")
    text = "\n".join(lines) + "\n"
    print(text, end="")
    if a.summary:
        out = Path(a.summary)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

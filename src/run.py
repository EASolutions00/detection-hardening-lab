"""Run one comparison from run folders.

    .venv/Scripts/python.exe src/run.py --control data/runs/ctl-* --pre data/runs/pre-* \
        --post data/runs/post-* --rules data/rules/wazuh-4.14.7 --out data/summaries/C3

Writes report.txt, findings.json and comparison.csv into --out.
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telos.pipeline import PipelineError, compare  # noqa: E402


def _git_commit() -> str:
    """The repository's current commit, recorded as the analyser version (read-only)."""
    import subprocess
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                           cwd=Path(__file__).parent.parent)
        return p.stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def _expand(patterns: list[str]) -> list[str]:
    out: list[str] = []
    for p in patterns:
        out.extend(sorted(glob.glob(p)) or [p])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare control, before and after runs of one change.")
    ap.add_argument("--control", nargs="+", required=True)
    ap.add_argument("--pre", nargs="+", required=True)
    ap.add_argument("--post", nargs="+", required=True)
    ap.add_argument("--rules", required=True, help="the unpacked Wazuh rule export")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-runs", type=int, default=3)
    default_kb = Path(__file__).parent.parent / "lab" / "knowledge" / "compensating-controls.json"
    ap.add_argument("--controls", default=str(default_kb) if default_kb.exists() else None,
                    help="curated compensating controls for remediation level 2")
    a = ap.parse_args()
    try:
        out = compare(_expand(a.control), _expand(a.pre), _expand(a.post), a.rules, a.out, a.min_runs,
                      analyser_version=_git_commit(), controls_path=a.controls)
    except PipelineError as exc:
        print(f"cannot compare: {exc}", file=sys.stderr)
        return 2
    for name, path in out.files.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

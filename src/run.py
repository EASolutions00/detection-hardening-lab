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
    a = ap.parse_args()
    try:
        out = compare(_expand(a.control), _expand(a.pre), _expand(a.post), a.rules, a.out, a.min_runs)
    except PipelineError as exc:
        print(f"cannot compare: {exc}", file=sys.stderr)
        return 2
    for name, path in out.files.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

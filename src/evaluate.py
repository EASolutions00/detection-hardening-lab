"""Run the evaluation's remaining runs on the real lab, one after another, unattended.
**The student runs this**: it passes the guest password to vmrun (DECISIONS 2026-11-27).

    .venv/Scripts/python.exe src/evaluate.py
    .venv/Scripts/python.exe src/evaluate.py --cases C3 C5      (only these cases' after runs)

The plan is all 26 runs in src/telos/evaluation.py. Runs already in data/runs/ are skipped, so
the same command resumes after any stop. Each run is captured exactly as src/capture.py captures
it: the same LabConfig (capture.lab_config), the pinned stimulus, Config S and item 22's void
rule. A voided run does not stop the batch; a run that stops before producing data does (a lab
problem that the next run would hit too). Keep the host signed in, unlocked and awake: the
Remote Desktop sign-in opens a window on its desktop for 30 s in every run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent))

from capture import REPO, lab_config as _lab_config  # noqa: E402
from telos.catalog import CHANGES, RUN_CHECKS, parameters, pinned_stimulus  # noqa: E402
from telos.evaluation import CASES, evaluation_plan  # noqa: E402
from telos.harness import Lab, LabConfig, capture  # noqa: E402
from telos.spike import PlannedRun, run_batch  # noqa: E402


def lab_config(window_s: int, backup_dir: str | None) -> LabConfig:
    return _lab_config(window_s, backup_dir, "S")


def make_capture_one(window_s: int, backup_dir: str | None,
                     capture_fn: Callable[..., dict] = capture) -> Callable[[PlannedRun], dict]:
    def capture_one(run: PlannedRun) -> dict:
        change = CHANGES[run.change] if run.change else None
        return capture_fn(Lab(lab_config(window_s, backup_dir)), run.run_id, run.phase, pinned_stimulus(),
                          parameters(run.config), change=change, checks=RUN_CHECKS)
    return capture_one


def main() -> int:
    ap = argparse.ArgumentParser(description="The TeLoS evaluation runs, unattended (Phase E).")
    ap.add_argument("--cases", nargs="+", choices=CASES, help="only these cases' after runs")
    ap.add_argument("--window-s", type=int, default=180)
    ap.add_argument("--backup-dir", default=None)
    a = ap.parse_args()
    plan = [r for r in evaluation_plan() if not a.cases or r.change in a.cases]
    runs_dir = REPO / "data" / "runs"
    todo = [r for r in plan if not (runs_dir / r.run_id / "run_manifest.json").exists()]
    print(f"evaluation: {len(plan)} runs in the plan, {len(todo)} to run, window {a.window_s} s; "
          f"about {len(todo) * 9} minutes. Keep the host signed in, unlocked and awake.")
    summary = run_batch(plan, runs_dir, make_capture_one(a.window_s, a.backup_dir))
    void = [s for s in summary if s["status"] == "VOID"]
    stopped = bool(summary) and summary[-1]["status"].startswith("STOPPED")
    print(f"\ndone: {sum(1 for s in summary if s['status'] == 'valid')} valid, {len(void)} void, "
          f"{sum(1 for s in summary if s['status'].startswith('skipped'))} skipped, "
          f"{'STOPPED early: start the same command again to resume' if stopped else 'not stopped'}")
    for s in void:
        print(f"  VOID {s['run_id']}: {s['void_reasons']} (capture a replacement under a new id, for example "
              f"{s['run_id']}b)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

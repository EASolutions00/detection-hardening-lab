"""The feasibility spike: its run plan and the batch runner (runbook Phase 7).

The plan is the smallest set of runs that answers the six spike questions, plus
one real C3 comparison so the whole method runs once on real data:

    S-ctl    5 control runs, Config S      Q1, Q2, Q3, Q4, Q5
    N-ctl    5 control runs, Config N      Q1 under Config N
    reboot   3 control runs, Config S,     Q6: does a post-change run's extra reboot
             with one extra reboot             leave a trace?
    C3-pre   3 runs before C3, Config S    the first real comparison (src/run.py)
    C3-post  3 runs after C3, Config S

The batch runner runs them in order. A run whose folder already holds a manifest is
skipped, so an interrupted batch can be started again. A voided run does not stop the
batch (it is recorded). A failed check before a run stops the batch, because it is a
lab problem (for example the host's lab address is missing) that every later run
would hit too.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .harness import HarnessError


@dataclass(frozen=True)
class PlannedRun:
    run_id: str
    group: str
    phase: str
    config: str                 # "S" Defender off after every boot, "N" as is
    change: str | None = None
    extra_reboot: bool = False


def spike_plan() -> list[PlannedRun]:
    plan = [PlannedRun(f"spike-S-ctl-{i}", "S-ctl", "control", "S") for i in range(1, 6)]
    plan += [PlannedRun(f"spike-N-ctl-{i}", "N-ctl", "control", "N") for i in range(1, 6)]
    plan += [PlannedRun(f"spike-S-reboot-{i}", "reboot", "control", "S", extra_reboot=True) for i in range(1, 4)]
    plan += [PlannedRun(f"spike-S-C3-pre-{i}", "C3-pre", "pre", "S") for i in range(1, 4)]
    plan += [PlannedRun(f"spike-S-C3-post-{i}", "C3-post", "post", "S", change="C3") for i in range(1, 4)]
    return plan


def run_batch(plan: list[PlannedRun], runs_dir: str | Path, capture_one: Callable[[PlannedRun], dict],
              log: Callable[..., None] = print) -> list[dict]:
    """Run each planned run in order; returns one summary line per run reached."""
    runs_dir = Path(runs_dir)
    summary: list[dict] = []
    for i, run in enumerate(plan, 1):
        if (runs_dir / run.run_id / "run_manifest.json").exists():
            summary.append({"run_id": run.run_id, "status": "skipped (exists)"})
            log(f"[{i}/{len(plan)}] {run.run_id}: skipped, already exists")
            continue
        log(f"[{i}/{len(plan)}] {run.run_id}: {run.group}, phase {run.phase}, config {run.config}"
            + (f", change {run.change}" if run.change else "") + (", extra reboot" if run.extra_reboot else ""))
        try:
            m = capture_one(run)
        except HarnessError as exc:
            summary.append({"run_id": run.run_id, "status": f"STOPPED: {exc}"})
            log(f"    STOPPED, before producing data: {exc}")
            break
        r = m["record"]
        status = "valid" if r["valid"] else "VOID"
        summary.append({"run_id": run.run_id, "status": status, "void_reasons": r.get("void_reasons", []),
                        "run_seconds": r.get("run_seconds")})
        log(f"    {status}" + (f": {r['void_reasons']}" if not r["valid"] else "")
            + (f"   ({r.get('run_seconds', 0) / 60:.1f} min)" if r.get("run_seconds") else ""))
    return summary

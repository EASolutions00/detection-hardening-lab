"""The evaluation's run plan (Phase E; EXPECTED-RESULTS section 5; DECISIONS 2026-11-27).

All 26 runs, in the order they are made:

    ctl        5 control runs, no change          the noise floor; item 22's fingerprint range
    pre        3 before runs, no change           shared by all six cases
    post-<id>  3 after runs per case, in CASES    C1, C3, C5 (hardening) and K1, K2, K3 (test cases)

Every run: Config S, the pinned stimulus, `golden-base-v2`, item 22's void rule. The batch
runner (`spike.run_batch`) skips a run whose folder already holds a manifest, so the same
plan resumes after any stop. A voided run stays on disk with its reason; its replacement is
captured afterwards under a new run id (for example `eval-post-C3-2b`), never over it.
"""

from __future__ import annotations

from .spike import PlannedRun

CASES = ("C1", "C3", "C5", "K1", "K2", "K3")


def evaluation_plan() -> list[PlannedRun]:
    plan = [PlannedRun(f"eval-ctl-{i}", "ctl", "control", "S") for i in range(1, 6)]
    plan += [PlannedRun(f"eval-pre-{i}", "pre", "pre", "S") for i in range(1, 4)]
    plan += [PlannedRun(f"eval-post-{c}-{i}", f"post-{c}", "post", "S", change=c) for c in CASES for i in range(1, 4)]
    return plan

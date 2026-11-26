"""Tests for the evaluation batch (DECISIONS 2026-11-27): the plan of all 26 runs, and that
`src/evaluate.py` captures each run exactly as `src/capture.py` would. Nothing here touches a VM.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import evaluate  # noqa: E402
from telos.catalog import CHANGES, CONFIG_S, GOLDEN_SNAPSHOT, RUN_CHECKS, pinned_stimulus  # noqa: E402
from telos.evaluation import CASES, evaluation_plan  # noqa: E402
from telos.spike import run_batch  # noqa: E402

DONE_ON_2026_11_26 = ["eval-ctl-1", "eval-ctl-2", "eval-ctl-3", "eval-ctl-4", "eval-ctl-5",
                      "eval-pre-1", "eval-pre-2", "eval-pre-3", "eval-post-C1-1"]


def test_the_plan_has_26_runs_in_the_decided_order_with_the_ids_in_use():
    """5 control, 3 before, then 3 after runs per case (EXPECTED-RESULTS section 5; DECISIONS 2026-11-27)."""
    plan = evaluation_plan()
    ids = [r.run_id for r in plan]
    assert len(plan) == 26 and len(set(ids)) == 26
    assert ids[:9] == DONE_ON_2026_11_26
    assert [r.phase for r in plan] == ["control"] * 5 + ["pre"] * 3 + ["post"] * 18
    assert [r.change for r in plan[8:]] == [c for c in CASES for _ in range(3)]
    assert all(r.change is None for r in plan[:8]) and all(r.config == "S" for r in plan)


def test_the_after_runs_cover_exactly_the_six_cases_of_the_catalog():
    assert CASES == ("C1", "C3", "C5", "K1", "K2", "K3")
    assert set(CASES) <= set(CHANGES)


def test_each_run_is_captured_like_capture_py_with_the_void_rule(tmp_path):
    calls = []

    def fake_capture(lab, run_id, phase, stimulus, parameters, change=None, checks=None):
        calls.append((lab.cfg, run_id, phase, [s.name for s in stimulus], parameters, change, checks))
        return {"record": {"valid": True, "void_reasons": [], "run_seconds": 1.0}}

    capture_one = evaluate.make_capture_one(window_s=180, backup_dir=None, capture_fn=fake_capture)
    run = next(r for r in evaluation_plan() if r.run_id == "eval-post-C3-1")
    capture_one(run)
    cfg, run_id, phase, stimulus, parameters, change, checks = calls[0]
    assert (run_id, phase) == ("eval-post-C3-1", "post")
    assert cfg.snapshot == GOLDEN_SNAPSHOT and cfg.window_s == 180 and cfg.after_boot == CONFIG_S
    assert stimulus == [s.name for s in pinned_stimulus()]
    assert change is CHANGES["C3"] and checks is RUN_CHECKS


def test_a_restart_skips_the_runs_on_disk_and_runs_the_rest_in_order(tmp_path):
    for run_id in DONE_ON_2026_11_26:
        (tmp_path / run_id).mkdir()
        (tmp_path / run_id / "run_manifest.json").write_text("{}")
    ran = []

    def capture_one(run):
        ran.append(run.run_id)
        return {"record": {"valid": True, "void_reasons": [], "run_seconds": 1.0}}

    summary = run_batch(evaluation_plan(), tmp_path, capture_one, log=lambda *a: None)
    assert ran == [r.run_id for r in evaluation_plan()][9:]
    assert len(ran) == 17
    assert sum(1 for s in summary if s["status"].startswith("skipped")) == 9


def test_the_batch_and_capture_py_give_the_same_parameters_hash(tmp_path):
    """The batch must stay comparable with the 9 runs made with capture.py: one LabConfig for both."""
    import capture
    from telos.harness import parameters_hash
    a = evaluate.lab_config(window_s=180, backup_dir=None)
    b = capture.lab_config(window_s=180, backup_dir=None, config="S")
    assert a == b

    def params(cfg):
        from telos.catalog import parameters
        return {**parameters("S"), "window_s": cfg.window_s, "settle_s": cfg.settle_s, "drain_s": cfg.drain_s,
                "snapshot": cfg.snapshot, "agent": cfg.agent, "stimulus": [s.name for s in pinned_stimulus()],
                "after_boot": [s.name for s in cfg.after_boot]}
    assert parameters_hash(params(a)) == "9895d0cf7c5854231710f0af733e248cd62bfa7a8ca154a3c29bab11c53b14cd"

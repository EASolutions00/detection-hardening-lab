"""Tests for the spike plan and its batch runner (runbook Phase 7).

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.harness import HarnessError
from telos.spike import run_batch, spike_plan


def test_the_plan_has_the_19_runs_in_order():
    plan = spike_plan()
    groups = [r.group for r in plan]
    assert groups == ["S-ctl"] * 5 + ["N-ctl"] * 5 + ["reboot"] * 3 + ["C3-pre"] * 3 + ["C3-post"] * 3
    assert [r.config for r in plan].count("N") == 5
    assert all(r.extra_reboot for r in plan if r.group == "reboot")
    assert all(r.change == "C3" and r.phase == "post" for r in plan if r.group == "C3-post")
    assert all(r.change is None for r in plan if r.group != "C3-post")
    assert len({r.run_id for r in plan}) == 19


def fake_manifest(valid=True):
    return {"record": {"valid": valid, "void_reasons": [] if valid else ["x"], "run_seconds": 600.0}}


def test_existing_runs_are_skipped_and_voided_runs_do_not_stop_the_batch(tmp_path):
    plan = spike_plan()[:3]
    (tmp_path / plan[0].run_id).mkdir()
    (tmp_path / plan[0].run_id / "run_manifest.json").write_text(json.dumps(fake_manifest()))
    done = []

    def capture_one(run):
        done.append(run.run_id)
        return fake_manifest(valid=(run is not plan[1]))

    summary = run_batch(plan, tmp_path, capture_one, log=lambda *_: None)
    assert done == [plan[1].run_id, plan[2].run_id]
    assert [s["status"] for s in summary] == ["skipped (exists)", "VOID", "valid"]


def test_a_failed_check_before_a_run_stops_the_batch(tmp_path):
    plan = spike_plan()[:3]

    def capture_one(run):
        if run is plan[1]:
            raise HarnessError("the host's lab address 10.20.10.1 is missing")
        return fake_manifest()

    summary = run_batch(plan, tmp_path, capture_one, log=lambda *_: None)
    assert [s["status"] for s in summary] == ["valid", "STOPPED: the host's lab address 10.20.10.1 is missing"]

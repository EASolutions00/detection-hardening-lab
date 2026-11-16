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


PARAMS = {"config": "S", "window_s": 180}
STEADY = "Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]"
NOISY = "Sysmon-13[Details,EventType,TargetObject]"
RARE = "Security-4624[AuthenticationPackageName=other,LogonType=2,TargetUserName]"


def write_run(root, run_id, counts, seconds=600.0, valid=True, params=PARAMS):
    from telos.harness import parameters_hash
    d = root / run_id
    d.mkdir(parents=True)
    (d / "counts.json").write_text(json.dumps({"run_id": run_id, "counts": counts, "fired": {}}))
    (d / "run_manifest.json").write_text(json.dumps({
        "parameters": params, "parameters_sha256": parameters_hash(params),
        "record": {"run_id": run_id, "valid": valid, "void_reasons": [], "run_seconds": seconds,
                   "change_id": "C3" if "post" in run_id else None}}))


def spike_runs(root, *, groups=("S-ctl", "N-ctl", "reboot")):
    for r in spike_plan():
        if r.group not in groups:
            continue
        i = int(r.run_id.rsplit("-", 1)[1])
        params = dict(PARAMS, config=r.config)
        write_run(root, r.run_id, {STEADY: 100 + i, NOISY: [40, 80, 20, 70, 30][i - 1], RARE: 2},
                  seconds=550.0 + 10 * i, params=params)


def test_spike_answers_are_written_from_the_runs(tmp_path):
    from telos.spike import analyse_spike
    runs, out = tmp_path / "runs", tmp_path / "summaries"
    spike_runs(runs)
    answers = analyse_spike(runs, out, rules_dir=None)
    cov = (out / "cov_control_runs.csv").read_text(encoding="utf-8")
    assert cov.startswith("config,key,") and "S," in cov and "N," in cov
    assert "run_id" in (out / "run_timings.csv").read_text(encoding="utf-8")
    assert answers["Q2"]["runs"] == 13 and 9.0 < answers["Q2"]["mean_minutes"] < 10.5
    assert answers["Q3"]["pairs"] == 10
    assert answers["Q4"]["testable"] == 2 and answers["Q4"]["keys"] == 3      # RARE: 2 per run, under 30 in 3
    assert answers["Q5"]["min"] == 101 and answers["Q5"]["max"] == 105
    assert answers["Q6"]["runs"] == 3
    assert "Q1" in (out / "spike_answers.txt").read_text(encoding="utf-8")


def test_the_c3_comparison_records_the_analyser_version(tmp_path, monkeypatch):
    # Found on the first real spike (2026-11-16): the C3 report said "analyser version unknown".
    import telos.pipeline
    from telos.spike import analyse_spike
    runs, out = tmp_path / "runs", tmp_path / "summaries"
    spike_runs(runs, groups=("S-ctl", "C3-pre", "C3-post"))
    seen = {}

    def fake_compare(*args, **kwargs):
        seen.update(kwargs)
        raise telos.pipeline.PipelineError("stop here")

    monkeypatch.setattr(telos.pipeline, "compare", fake_compare)
    analyse_spike(runs, out, rules_dir=tmp_path, analyser_version="abc1234")
    assert seen.get("analyser_version") == "abc1234"


def test_a_partial_spike_says_what_is_missing(tmp_path):
    from telos.spike import analyse_spike
    runs, out = tmp_path / "runs", tmp_path / "summaries"
    spike_runs(runs, groups=("S-ctl",))
    answers = analyse_spike(runs, out, rules_dir=None)
    assert answers["Q1"]["N"] == "not enough valid runs (0 of 5)"
    assert answers["Q6"] == "not enough valid runs (0 of 3)"
    assert answers["C3"] == "not enough valid runs (C3-pre 0 of 3, C3-post 0 of 3)"


def test_a_failed_check_before_a_run_stops_the_batch(tmp_path):
    plan = spike_plan()[:3]

    def capture_one(run):
        if run is plan[1]:
            raise HarnessError("the host's lab address 10.20.10.1 is missing")
        return fake_manifest()

    summary = run_batch(plan, tmp_path, capture_one, log=lambda *_: None)
    assert [s["status"] for s in summary] == ["valid", "STOPPED: the host's lab address 10.20.10.1 is missing"]

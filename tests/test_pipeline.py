"""Tests for the pipeline: run folders in, report and exports out.

Run folders are what the harness writes (counts.json, run_manifest.json). The
pipeline checks they belong together, runs the whole method, and writes the
report, the JSON findings and the CSV comparison.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.harness import parameters_hash
from telos.pipeline import PipelineError, compare, load_phase
from telos.rulehash import rule_folder_sha256

from test_impact import RULES

INJECTION = "Sysmon-8[]"
PROCESS = "Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]"
PARAMS = {"window_s": 600, "snapshot": "cfg-suppressed", "stimulus": ["T1003.001-13"]}


def write_run(root: Path, run_id: str, counts: dict, fired: dict, *, phase="pre", change=None,
              valid=True, params=PARAMS, code=None) -> Path:
    d = root / run_id
    d.mkdir(parents=True)
    (d / "counts.json").write_text(json.dumps({"run_id": run_id, "counts": counts, "fired": fired}))
    record = {"run_id": run_id, "phase": phase, "change_id": change, "valid": valid,
              "void_reasons": [] if valid else ["change not confirmed"]}
    if code is not None:                       # (commit, changed): the code version a run records since 2026-11-28
        record["code_commit"], record["code_dirty"] = code
    (d / "run_manifest.json").write_text(json.dumps({
        "parameters": params, "parameters_sha256": parameters_hash(params), "record": record}))
    return d


@pytest.fixture
def rules_dir(tmp_path):
    d = tmp_path / "rules"
    d.mkdir()
    (d / "rules.xml").write_text(RULES, encoding="utf-8")
    return d


def phases(tmp_path, params=PARAMS, pre_code=None):
    control = [write_run(tmp_path, f"ctl-{i}", {INJECTION: 40 + i, PROCESS: 200 + i}, {"92403": 40},
                         phase="control", params=params) for i in range(5)]
    pre = [write_run(tmp_path, f"pre-{i}", {INJECTION: 41 - i, PROCESS: 201 - i}, {"92403": 40}, params=params,
                     code=pre_code if i == 0 else None) for i in range(3)]
    post = [write_run(tmp_path, f"post-{i}", {PROCESS: 200 + i}, {"99001": 3}, phase="post", change="C3",
                      params=params) for i in range(3)]
    return control, pre, post


def test_a_run_missing_a_key_counts_zero_for_it(tmp_path):
    a = write_run(tmp_path, "a", {INJECTION: 4}, {})
    b = write_run(tmp_path, "b", {PROCESS: 7}, {})
    phase, fired, _ = load_phase("pre", [a, b], keys=[INJECTION, PROCESS])
    assert phase.counts == {INJECTION: [4, 0], PROCESS: [0, 7]}


def test_the_whole_method_runs_and_writes_three_files(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)
    out = compare(control, pre, post, rules_dir, tmp_path / "out")
    report = (tmp_path / "out" / "report.txt").read_text(encoding="utf-8")
    assert "BLIND SPOTS FOUND: 1" in report
    assert "T1055" in report
    findings = json.loads((tmp_path / "out" / "findings.json").read_text(encoding="utf-8"))
    assert findings["ranked"][0]["key"] == INJECTION
    assert findings["ranked"][0]["classification"] == "LOST"
    assert (tmp_path / "out" / "comparison.csv").read_text(encoding="utf-8").startswith("key,")
    layer = json.loads((tmp_path / "out" / "navigator_layer.json").read_text(encoding="utf-8"))
    assert layer["versions"]["layer"] == "4.5" and "T1055" in {t["techniqueID"] for t in layer["techniques"]}
    assert out.ranked[0].key == INJECTION


def test_myers_runs_in_the_pipeline_on_the_joined_phases(tmp_path, rules_dir):
    """Step 3: the 3 runs before (120 injection events) against the 3 after (none)."""
    control, pre, post = phases(tmp_path)
    out = compare(control, pre, post, rules_dir, tmp_path / "out")
    assert out.myers.phases.deleted == {INJECTION: 120}
    assert out.myers.phases.inserted == {PROCESS: 3}
    assert out.myers.phases.d == 123 and out.myers.phases.matches_count_subtraction
    assert len(out.myers.control_pair_d) == 10 and len(out.myers.before_after_pair_d) == 9
    report = (tmp_path / "out" / "report.txt").read_text(encoding="utf-8")
    assert "MYERS COMPARISON" in report and "Edit distance D = 123" in report
    assert report.index("MYERS COMPARISON") < report.index("NOISE FLOOR")
    data = json.loads((tmp_path / "out" / "findings.json").read_text(encoding="utf-8"))
    assert data["myers"]["phases"]["deleted"] == {INJECTION: 120}


def test_the_report_carries_a_reproducibility_record(tmp_path, rules_dir):
    """FINAL, Outputs: the manifest and its hash, snapshot, tests, rule set, analyser version, raw counts."""
    control, pre, post = phases(tmp_path)
    compare(control, pre, post, rules_dir, tmp_path / "out", analyser_version="abc1234")
    report = (tmp_path / "out" / "report.txt").read_text(encoding="utf-8")
    section = report[report.index("REPRODUCIBILITY"):]
    assert parameters_hash(PARAMS) in section
    assert "cfg-suppressed" in section and "T1003.001-13" in section
    assert "abc1234" in section
    for run_id in ["ctl-0", "pre-2", "post-1"]:
        assert run_id in section
    assert "counts.json" in section
    data = json.loads((tmp_path / "out" / "findings.json").read_text(encoding="utf-8"))
    assert data["reproducibility"]["parameters_sha256"] == parameters_hash(PARAMS)
    assert data["reproducibility"]["analyser_version"] == "abc1234"


def test_the_curated_list_gives_remediation_level_2_for_the_change(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)
    kb = Path(__file__).parent.parent / "lab" / "knowledge" / "compensating-controls.json"
    compare(control, pre, post, rules_dir, tmp_path / "out", controls_path=kb)
    report = (tmp_path / "out" / "report.txt").read_text(encoding="utf-8")
    assert "REMEDIATION CANDIDATES, LEVEL 2" in report and "92032" in report
    data = json.loads((tmp_path / "out" / "findings.json").read_text(encoding="utf-8"))
    assert data["remediation_level_2"][0]["change_id"] == "C3"


def test_runs_with_different_parameters_are_not_compared(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)
    other = dict(PARAMS, window_s=300)
    post[0] = write_run(tmp_path, "post-x", {PROCESS: 200}, {}, phase="post", change="C3", params=other)
    with pytest.raises(PipelineError, match="not comparable") as err:
        compare(control, pre, post, rules_dir, tmp_path / "out")
    assert "window_s" in str(err.value) and "stimulus" not in str(err.value)    # the field that differs is named


def test_a_manifest_changed_after_the_run_is_refused(tmp_path, rules_dir):
    """Outside review, point 12: the stored hash is recomputed from the run's own parameters."""
    control, pre, post = phases(tmp_path)
    manifest = pre[1] / "run_manifest.json"
    data = json.loads(manifest.read_text())
    data["parameters"]["window_s"] = 1                  # edited by hand; the stored hash is left as it was
    manifest.write_text(json.dumps(data))
    with pytest.raises(PipelineError, match=r"pre-1: its parameters do not match its stored hash"):
        compare(control, pre, post, rules_dir, tmp_path / "out")


def test_the_rule_export_must_be_the_one_the_runs_were_captured_with(tmp_path, rules_dir):
    right = rule_folder_sha256(rules_dir)
    ok = dict(PARAMS, rule_folder_sha256=right)
    control, pre, post = phases(tmp_path / "ok", params=ok)
    compare(control, pre, post, rules_dir, tmp_path / "out")
    report = (tmp_path / "out" / "report.txt").read_text(encoding="utf-8")
    assert f"SHA256 {right}" in report and "MATCHES the value pinned in the runs" in report
    data = json.loads((tmp_path / "out" / "findings.json").read_text(encoding="utf-8"))
    assert data["reproducibility"]["rule_export"]["matches_runs"] is True
    wrong = dict(PARAMS, rule_folder_sha256="0" * 64)
    control, pre, post = phases(tmp_path / "wrong", params=wrong)
    with pytest.raises(PipelineError, match="not the one the runs were captured with"):
        compare(control, pre, post, rules_dir, tmp_path / "out2")


def test_a_missing_rule_export_folder_is_a_clear_error(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)
    with pytest.raises(PipelineError, match="cannot read the rule export: not a folder"):
        compare(control, pre, post, tmp_path / "no-such-folder", tmp_path / "out")


def test_a_rule_export_the_runs_do_not_pin_is_computed_and_reported_as_not_compared(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)               # PARAMS holds no rule_folder_sha256
    compare(control, pre, post, rules_dir, tmp_path / "out")
    report = (tmp_path / "out" / "report.txt").read_text(encoding="utf-8")
    assert "not pinned in the runs, so not compared" in report
    data = json.loads((tmp_path / "out" / "findings.json").read_text(encoding="utf-8"))
    assert data["reproducibility"]["rule_export"]["sha256"] == rule_folder_sha256(rules_dir)
    assert data["reproducibility"]["rule_export"]["matches_runs"] is None


def test_the_record_lists_what_the_hash_covers_the_analysis_settings_and_each_runs_code_version(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path, pre_code=("abc1234", True))
    compare(control, pre, post, rules_dir, tmp_path / "out")
    report = (tmp_path / "out" / "report.txt").read_text(encoding="utf-8")
    section = report[report.index("REPRODUCIBILITY"):]
    assert "What it covers: exactly the parameters listed below, and nothing else" in section
    assert "alpha 0.05" in section and "at least 30 events before" in section
    assert "code abc1234 (files changed since)" in section and "code not recorded" in section
    data = json.loads((tmp_path / "out" / "findings.json").read_text(encoding="utf-8"))
    repro = data["reproducibility"]
    assert repro["analysis_settings"] == {"alpha": 0.05, "max_ratio": 0.5, "min_pre_count": 30,
                                          "noise_sigmas": 3.0, "min_control_runs": 3}
    by_id = {r["run_id"]: r for r in repro["runs"]}
    assert by_id["pre-0"]["code_commit"] == "abc1234" and by_id["pre-0"]["code_dirty"] is True
    assert by_id["pre-1"]["code_commit"] is None


def test_a_voided_run_is_left_out_and_too_few_runs_is_an_error(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)
    post[1] = write_run(tmp_path, "post-void", {PROCESS: 200}, {}, phase="post", change="C3", valid=False)
    with pytest.raises(PipelineError, match="post.*2 valid runs.*post-void"):
        compare(control, pre, post, rules_dir, tmp_path / "out")


def test_post_runs_of_different_changes_are_refused(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)
    post[2] = write_run(tmp_path, "post-c5", {PROCESS: 200}, {}, phase="post", change="C5")
    with pytest.raises(PipelineError, match="more than one change"):
        compare(control, pre, post, rules_dir, tmp_path / "out")

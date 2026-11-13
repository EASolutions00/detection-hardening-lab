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

from test_impact import RULES

INJECTION = "Sysmon-8[]"
PROCESS = "Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]"
PARAMS = {"window_s": 600, "snapshot": "cfg-suppressed", "stimulus": ["T1003.001-13"]}


def write_run(root: Path, run_id: str, counts: dict, fired: dict, *, phase="pre", change=None,
              valid=True, params=PARAMS) -> Path:
    d = root / run_id
    d.mkdir(parents=True)
    (d / "counts.json").write_text(json.dumps({"run_id": run_id, "counts": counts, "fired": fired}))
    (d / "run_manifest.json").write_text(json.dumps({
        "parameters": params, "parameters_sha256": parameters_hash(params),
        "record": {"run_id": run_id, "phase": phase, "change_id": change, "valid": valid,
                   "void_reasons": [] if valid else ["change not confirmed"]}}))
    return d


@pytest.fixture
def rules_dir(tmp_path):
    d = tmp_path / "rules"
    d.mkdir()
    (d / "rules.xml").write_text(RULES, encoding="utf-8")
    return d


def phases(tmp_path):
    control = [write_run(tmp_path, f"ctl-{i}", {INJECTION: 40 + i, PROCESS: 200 + i}, {"92403": 40},
                         phase="control") for i in range(5)]
    pre = [write_run(tmp_path, f"pre-{i}", {INJECTION: 41 - i, PROCESS: 201 - i}, {"92403": 40})
           for i in range(3)]
    post = [write_run(tmp_path, f"post-{i}", {PROCESS: 200 + i}, {"99001": 3}, phase="post", change="C3")
            for i in range(3)]
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
    assert out.ranked[0].key == INJECTION


def test_runs_with_different_parameters_are_not_compared(tmp_path, rules_dir):
    control, pre, post = phases(tmp_path)
    other = dict(PARAMS, window_s=300)
    post[0] = write_run(tmp_path, "post-x", {PROCESS: 200}, {}, phase="post", change="C3", params=other)
    with pytest.raises(PipelineError, match="not comparable"):
        compare(control, pre, post, rules_dir, tmp_path / "out")


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

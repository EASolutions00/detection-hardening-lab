"""Tests for the report sections added 2026-11-13: verdict, ranked blind spots,
coverage change, remediation level 1, and the JSON and CSV exports (FINAL,
Outputs; DECISIONS 2026-11-13 on the ranking and on "did fire").

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos import Classification, Phase
from telos.impact import rank_impact
from telos.index import build_index, load_rules
from telos.model import AnalysisResult, Finding, ProfileOutcome
from telos.report import (comparison_csv, coverage_change, findings_json, render_coverage,
                          render_impact, render_verdict)

from test_impact import INJECTION, LSASS_READ, NO_RULE, PROCESS, RULES


@pytest.fixture
def index(tmp_path):
    (tmp_path / "rules.xml").write_text(RULES, encoding="utf-8")
    return build_index(load_rules(tmp_path))


def result(*findings, outcome=ProfileOutcome.CHANGED):
    return AnalysisResult(outcome=outcome, outcome_reason="test", findings=list(findings))


def post(counts):
    return Phase(name="post", counts={k: [v, v, v] for k, v in counts.items()})


# --- verdict -----------------------------------------------------------------

def test_verdict_for_a_run_that_could_not_be_tested(index):
    text = render_verdict(result(outcome=ProfileOutcome.NOT_TESTABLE), [])
    assert "NOT TESTABLE" in text


def test_verdict_when_no_lost_key_leaves_a_technique_blind(index):
    r = result(Finding(LSASS_READ, Classification.LOST))
    ranked = rank_impact(r, post({PROCESS: 5}), index, fired_after={"99001": 2})
    assert "NO BLIND SPOT FOUND" in render_verdict(r, ranked)


def test_verdict_counts_keys_with_a_blind_technique_and_names_the_top_one(index):
    r = result(Finding(LSASS_READ, Classification.LOST), Finding(INJECTION, Classification.REDUCED),
               Finding(NO_RULE, Classification.LOST))
    ranked = rank_impact(r, post({INJECTION: 2, PROCESS: 5}), index, fired_after={})
    text = render_verdict(r, ranked)
    assert "BLIND SPOTS FOUND: 2" in text
    assert LSASS_READ in text.splitlines()[-1] or LSASS_READ in text


# --- ranked blind spots and remediation level 1 ------------------------------

def test_ranked_section_shows_the_three_numbers_and_the_could_fire_rules(index):
    r = result(Finding(LSASS_READ, Classification.LOST))
    ranked = rank_impact(r, post({PROCESS: 5}), index, fired_after={})
    text = render_impact(ranked)
    assert LSASS_READ in text
    assert "blind techniques 1" in text and "highest level 12" in text and "rules 1" in text
    assert "T1003.001" in text
    assert "99001" in text            # the could-fire rule, offered as remediation level 1


# --- coverage change ---------------------------------------------------------

def test_coverage_change_lists_techniques_that_fired_before_and_not_after(index):
    before, after, lost = coverage_change({"92403": 1, "99001": 2}, {"99001": 2}, index)
    assert before == {"T1055", "T1003.001"}
    assert after == {"T1003.001"}
    assert lost == ["T1055"]
    assert "T1055" in render_coverage(before, after, lost)


# --- exports -----------------------------------------------------------------

def test_json_export_keeps_the_ranking_and_parses(index):
    r = result(Finding(LSASS_READ, Classification.LOST), Finding(INJECTION, Classification.REDUCED))
    ranked = rank_impact(r, post({INJECTION: 2, PROCESS: 5}), index, fired_after={"99001": 2})
    data = json.loads(findings_json(r, ranked, lost_techniques=["T1055"]))
    assert data["outcome"] == "CHANGED"
    assert [f["key"] for f in data["ranked"]] == [INJECTION, LSASS_READ]
    assert data["ranked"][0]["blind_techniques"] == ["T1055"]
    assert data["coverage_lost"] == ["T1055"]


def test_navigator_layer_uses_the_required_fields_of_format_4_5(index):
    """MITRE ATT&CK Navigator layer format 4.5 (layers/spec/v4.5/layerformat.md, read 2026-11-13):
    name and domain required; versions.layer "4.5", versions.navigator at least "4.9.0";
    techniqueID required per technique."""
    from telos.report import navigator_layer
    r = result(Finding(INJECTION, Classification.LOST))
    ranked = rank_impact(r, post({PROCESS: 5}), index, fired_after={"99001": 1})
    layer = json.loads(navigator_layer("C3 test", {"T1055", "T1003.001"}, {"T1003.001"}, ranked))
    assert layer["name"] == "C3 test" and layer["domain"] == "enterprise-attack"
    assert layer["versions"]["layer"] == "4.5" and layer["versions"]["navigator"] == "4.9.0"
    by_id = {t["techniqueID"]: t for t in layer["techniques"]}
    assert by_id["T1055"]["color"] == "#e60d0d" and "no alert" in by_id["T1055"]["comment"]
    assert by_id["T1003.001"]["color"] == "#31a354"


KB = {"version": 1, "controls": [
    {"change_id": "C3", "technique": "T1055", "control": "Raise the level of 92032", "source": "COMMANDS 2.13",
     "status": "suggested, not tested"},
    {"change_id": "C3", "technique": None, "control": "Any C3 entry", "source": "x", "status": "suggested"},
    {"change_id": "C5", "technique": "T1021.001", "control": "C5 only", "source": "y", "status": "suggested"},
]}


def test_remediation_level_2_matches_the_change_and_the_blind_techniques(tmp_path):
    from telos.report import load_controls, remediation_level2
    path = tmp_path / "kb.json"
    path.write_text(json.dumps(KB), encoding="utf-8")
    kb = load_controls(path)
    hits = remediation_level2(kb, "C3", {"T1055"})
    assert [h["control"] for h in hits] == ["Raise the level of 92032", "Any C3 entry"]
    assert remediation_level2(kb, "C3", {"T1003.001"}) == [KB["controls"][1]]
    assert remediation_level2(kb, "C1", {"T1055"}) == []


def test_remediation_level_2_section_shows_source_and_status():
    from telos.report import render_remediation2
    text = render_remediation2("C3", KB["controls"][:1])
    assert "Raise the level of 92032" in text and "COMMANDS 2.13" in text and "not tested" in text
    assert "no entry" in render_remediation2("C1", [])


def test_csv_export_has_one_row_per_key_and_blank_for_untested_values():
    r = result(Finding(LSASS_READ, Classification.LOST, pre_total=30, post_total=0, pre_rate=10.0,
                       post_rate=0.0, rate_ratio=0.0, q_value=0.001, cov=0.05, dispersion=1.2),
               Finding(NO_RULE, Classification.INCONCLUSIVE, pre_total=3, pre_rate=1.0))
    rows = list(csv.DictReader(io.StringIO(comparison_csv(r))))
    assert [row["key"] for row in rows] == [LSASS_READ, NO_RULE]
    assert rows[0]["classification"] == "LOST" and rows[0]["rate_ratio"] == "0.0"
    assert rows[1]["rate_ratio"] == "" and rows[1]["q_value"] == ""

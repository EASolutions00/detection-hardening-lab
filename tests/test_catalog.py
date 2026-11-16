"""Tests for the lab catalogue: the changes, Config S, the first test stimulus and the
hashed parameters that src/capture.py hands to the harness.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.catalog import CHANGES, CONFIG_S, POWERSHELL, parameters, trial_stimulus


def test_each_change_runs_its_script_and_confirms_with_verify():
    for cid, script in [("C1", "change-C1-disable-wdigest.ps1"), ("C3", "change-C3-lsa-protection.ps1"),
                        ("C5", "change-C5-rdp-nla.ps1")]:
        ch = CHANGES[cid]
        assert ch.apply[0].program == POWERSHELL
        assert ch.apply[0].args[-1] == rf"C:\telos\{script}"
        assert ch.verify.args[-2:] == (rf"C:\telos\{script}", "-Verify")
        assert re.fullmatch(r"[0-9a-f]{64}", ch.script_sha256)


def test_only_c3_needs_a_reboot():
    assert CHANGES["C3"].reboot and not CHANGES["C1"].reboot and not CHANGES["C5"].reboot


def test_config_s_runs_the_defender_script_after_boot():
    assert CONFIG_S[0].args[-1] == r"C:\telos\config-S-defender-off.ps1"


def test_trial_stimulus_runs_test_13_last_then_cleans_up():
    """Test 13 leaves a second lsass.exe running, which breaks a later test that names
    lsass.exe (OPEN-QUESTIONS 35), so it runs last."""
    names = [s.name for s in trial_stimulus()]
    assert names == ["T1003.001-1", "T1003.001-2", "T1003.001-13", "T1003.001-cleanup"]
    assert "-TestNumbers 13 " in trial_stimulus()[2].args[-1]


def test_parameters_carry_the_pinned_versions_and_the_config():
    p = parameters(config="S")
    assert p["art_commit"] == "cb486d9a888e921fac5902a06c7b46e420bb14a7"
    assert p["rule_folder_sha256"] == "a3f9749e7bb35978f663c7d7dd0c6d67a92a03d0df552e341c52a4eb55ae2939"
    assert p["sysmon_config_sha256"] == "02C43AC8EA7B27A9D290C2FE4587A5C184B09FC0AEDA263C2C4E24A4EE43B3AD"
    assert p["config"] == "S"
    assert parameters(config="N")["config"] == "N"

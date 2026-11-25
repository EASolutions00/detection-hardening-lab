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


def test_known_answer_cases_run_their_scripts_and_confirm_with_verify():
    """K1 to K3 (DECISIONS 2026-11-26): test cases, each a script in lab/scripts with -Verify,
    applied like a change. None restarts the guest; K2's -Verify checks the effect itself."""
    for cid, script in [("K1", "change-K1-audit-logon-off.ps1"), ("K2", "change-K2-cmdline-off.ps1"),
                        ("K3", "change-K3-audit-process-creation-off.ps1")]:
        ch = CHANGES[cid]
        assert ch.apply[0].program == POWERSHELL
        assert ch.apply[0].args[-1] == rf"C:\telos\{script}"
        assert ch.verify.args[-2:] == (rf"C:\telos\{script}", "-Verify")
        assert not ch.reboot
        assert re.fullmatch(r"[0-9a-f]{64}", ch.script_sha256)


def test_config_s_runs_the_defender_script_after_boot():
    assert CONFIG_S[0].args[-1] == r"C:\telos\config-S-defender-off.ps1"


def test_trial_stimulus_runs_test_13_last_then_cleans_up():
    """Test 13 leaves a second lsass.exe running, which breaks a later test that names
    lsass.exe (OPEN-QUESTIONS 35), so it runs last."""
    names = [s.name for s in trial_stimulus()]
    assert names == ["T1003.001-1", "T1003.001-2", "T1003.001-13", "T1003.001-cleanup"]
    assert "-TestNumbers 13 " in trial_stimulus()[2].args[-1]


def test_pinned_stimulus_signs_in_over_rdp_first_then_runs_the_lsass_tests():
    """The pinned list (DECISIONS 2026-11-18, OPEN-QUESTIONS 40): the Remote Desktop
    sign-in from the host first, then the trial's LSASS tests with 13 last."""
    from telos.catalog import pinned_stimulus
    from telos.harness import GuestStep, HostStep
    steps = pinned_stimulus()
    assert [s.name for s in steps] == ["rdp-signin-30s", "T1003.001-1", "T1003.001-2", "T1003.001-13",
                                       "T1003.001-cleanup"]
    assert isinstance(steps[0], HostStep) and all(isinstance(s, GuestStep) for s in steps[1:])


def test_rdp_signin_uses_the_stored_credential_and_fails_if_mstsc_closed_early():
    from telos.catalog import rdp_signin
    step = rdp_signin()
    script = step.args[-1]
    assert step.args[0] == POWERSHELL
    assert "/v:10.20.10.20" in script and "Start-Sleep -Seconds 30" in script and "Stop-Process" in script
    assert "HasExited" in script and "exit 1" in script
    # No password anywhere in the step: mstsc reads the cmdkey credential (COMMANDS 2.12).
    assert not any(re.search(r"(?i)password|-gp\b|cmdkey|/pass|\.pw\b", a) for a in step.args)


def test_parameters_carry_the_pinned_versions_and_the_config():
    p = parameters(config="S")
    assert p["art_commit"] == "cb486d9a888e921fac5902a06c7b46e420bb14a7"
    assert p["rule_folder_sha256"] == "a3f9749e7bb35978f663c7d7dd0c6d67a92a03d0df552e341c52a4eb55ae2939"
    assert p["sysmon_config_sha256"] == "02C43AC8EA7B27A9D290C2FE4587A5C184B09FC0AEDA263C2C4E24A4EE43B3AD"
    assert p["config"] == "S"
    assert parameters(config="N")["config"] == "N"

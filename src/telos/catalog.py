"""The lab's fixed pieces for the harness: the changes, Config S, the first test
stimulus, and the parameters that are hashed into every run manifest.

Everything here points at files already in the golden image (`golden-base`,
DECISIONS 2026-11-16): the scripts in `C:\\telos\\` (copied 2026-11-16) and Atomic
Red Team at its pinned commit in `C:\\AtomicRedTeam\\`.

The final attack-test list is the student's decision (STATUS). `trial_stimulus()`
is the LSASS trial's tests, enough to prove the harness on the real lab.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .harness import Change, GuestStep

POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
SCRIPTS = Path(__file__).resolve().parents[2] / "lab" / "scripts"
ART_MODULE = r"C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1"
ART_ATOMICS = r"C:\AtomicRedTeam\atomics"


def script_step(name: str, script: str, *extra: str) -> GuestStep:
    """A guest step that runs one of the repo's scripts from C:\\telos."""
    return GuestStep(name, POWERSHELL, ("-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                        rf"C:\telos\{script}", *extra))


def _sha256(script: str) -> str:
    return hashlib.sha256((SCRIPTS / script).read_bytes()).hexdigest()


def _change(cid: str, script: str, reboot: bool = False) -> Change:
    return Change(cid, apply=(script_step(f"{cid}-apply", script),),
                  verify=script_step(f"{cid}-verify", script, "-Verify"),
                  reboot=reboot, script_sha256=_sha256(script))


CHANGES: dict[str, Change] = {
    "C1": _change("C1", "change-C1-disable-wdigest.ps1"),
    "C3": _change("C3", "change-C3-lsa-protection.ps1", reboot=True),
    "C5": _change("C5", "change-C5-rdp-nla.ps1"),
}

CONFIG_S: tuple[GuestStep, ...] = (script_step("config-S", "config-S-defender-off.ps1"),)


def atomic(technique: str, number: int) -> GuestStep:
    """One Atomic Red Team test, run on its own so it gets its own exit code and duration."""
    cmd = (f"Import-Module {ART_MODULE} -Force; "
           f"Invoke-AtomicTest {technique} -TestNumbers {number} -PathToAtomicsFolder {ART_ATOMICS}")
    return GuestStep(f"{technique}-{number}", POWERSHELL, ("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd))


def atomic_cleanup(technique: str, numbers: list[int]) -> GuestStep:
    nums = ",".join(str(n) for n in numbers)
    cmd = (f"Import-Module {ART_MODULE} -Force; "
           f"Invoke-AtomicTest {technique} -TestNumbers {nums} -PathToAtomicsFolder {ART_ATOMICS} -Cleanup")
    return GuestStep(f"{technique}-cleanup", POWERSHELL, ("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd))


def trial_stimulus() -> list[GuestStep]:
    """The LSASS trial's tests 1, 2 and 13. Test 13 runs last: it leaves a second
    lsass.exe running, which breaks a later test that names lsass.exe (OPEN-QUESTIONS 35)."""
    return [atomic("T1003.001", 1), atomic("T1003.001", 2), atomic("T1003.001", 13),
            atomic_cleanup("T1003.001", [1, 2, 13])]


def parameters(config: str) -> dict:
    """The pinned values hashed into every run manifest (DECISIONS, pinned table)."""
    return {
        "config": config,                                                  # S = Defender off, N = as is
        "golden_base": "2026-11-16T06:59:45Z",
        "art_commit": "cb486d9a888e921fac5902a06c7b46e420bb14a7",
        "invoke_atomicredteam_commit": "8af478bb9e4637df568ac1e596553b025b16cd1b",
        "sysmon_config_sha256": "02C43AC8EA7B27A9D290C2FE4587A5C184B09FC0AEDA263C2C4E24A4EE43B3AD",
        "fence_sha256": "D35C939B71ECAC94868947932292531C02A171DECFD3046DEE47DB8E3BD0D814",
        "rule_folder_sha256": "a3f9749e7bb35978f663c7d7dd0c6d67a92a03d0df552e341c52a4eb55ae2939",
        "wazuh_version": "4.14.7",
    }

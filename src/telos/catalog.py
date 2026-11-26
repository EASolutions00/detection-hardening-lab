"""The lab's fixed pieces for the harness: the changes, Config S, the first test
stimulus, and the parameters that are hashed into every run manifest.

Everything here points at files already in the golden image (`golden-base`,
DECISIONS 2026-11-16): the scripts in `C:\\telos\\` (copied 2026-11-16) and Atomic
Red Team at its pinned commit in `C:\\AtomicRedTeam\\`. The one exception: the scripts
of the test cases K1 to K3 (added 2026-11-26) are not in `golden-base` yet
(OPEN-QUESTIONS 42), so their verify step fails and the harness voids the run until
they are. They go into `golden-base-v2` (docs/GOLDEN-BASE-V2.md); then GOLDEN_SNAPSHOT
and GOLDEN_BASE_TAKEN below change together.

`pinned_stimulus()` is the study's one attack list (DECISIONS 2026-11-18): the Remote
Desktop sign-in from the host, then the LSASS trial's tests. `trial_stimulus()` alone
is what the spike of 2026-11-16 used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .harness import Change, GuestStep, HostStep, Step

POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

# The golden snapshot every run reverts to, and when it was taken (DECISIONS 2026-11-16). Change BOTH together, right
# after a new snapshot is taken: the name goes to the harness (src/capture.py), the time into every run's hashed
# parameters. golden-base-v2 replaces both once it exists (DECISIONS 2026-11-26; docs/GOLDEN-BASE-V2.md, step C4).
GOLDEN_SNAPSHOT = "golden-base"
GOLDEN_BASE_TAKEN = "2026-11-16T06:59:45Z"
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
    # Test cases with a known answer (DECISIONS 2026-11-26; OPEN-QUESTIONS 42): configuration
    # mistakes made on purpose, each the opposite of a CIS or DISA item, never hardening.
    # Their expected results are in docs/EXPECTED-RESULTS.md, written before any run.
    "K1": _change("K1", "change-K1-audit-logon-off.ps1"),
    "K2": _change("K2", "change-K2-cmdline-off.ps1"),
    "K3": _change("K3", "change-K3-audit-process-creation-off.ps1"),
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


RDP_TARGET = "10.20.10.20"
RDP_SECONDS = 30


def rdp_signin(seconds: int = RDP_SECONDS) -> HostStep:
    """The Remote Desktop sign-in from the host, for C5 (and C1, DECISIONS 2026-11-18).

    mstsc signs in with `eli`'s credential stored on the host by `cmdkey` (COMMANDS 2.12):
    no password passes through this step. The client is closed after a fixed time; the
    revert before the next run ends the session (DECISIONS 2026-11-13). Exit code 1 if
    mstsc closed by itself before the time, which would mean the sign-in did not hold.
    The time is in the step's name, so it is part of the hashed parameters."""
    script = (f"$p = Start-Process mstsc -ArgumentList '/v:{RDP_TARGET}' -PassThru; "
              f"Start-Sleep -Seconds {seconds}; "
              "if ($p.HasExited) { exit 1 }; Stop-Process -Id $p.Id; exit 0")
    return HostStep(f"rdp-signin-{seconds}s", (POWERSHELL, "-NoProfile", "-Command", script))


def pinned_stimulus() -> list[Step]:
    """The one attack list for every run of the study (DECISIONS 2026-11-18; OPEN-QUESTIONS 40).
    The sign-in runs first, because test 13 leaves a second lsass.exe running."""
    return [rdp_signin(), *trial_stimulus()]


def parameters(config: str) -> dict:
    """The pinned values hashed into every run manifest (DECISIONS, pinned table)."""
    return {
        "config": config,                                                  # S = Defender off, N = as is
        "golden_base": GOLDEN_BASE_TAKEN,
        "art_commit": "cb486d9a888e921fac5902a06c7b46e420bb14a7",
        "invoke_atomicredteam_commit": "8af478bb9e4637df568ac1e596553b025b16cd1b",
        "sysmon_config_sha256": "02C43AC8EA7B27A9D290C2FE4587A5C184B09FC0AEDA263C2C4E24A4EE43B3AD",
        "fence_sha256": "D35C939B71ECAC94868947932292531C02A171DECFD3046DEE47DB8E3BD0D814",
        "rule_folder_sha256": "a3f9749e7bb35978f663c7d7dd0c6d67a92a03d0df552e341c52a4eb55ae2939",
        "wazuh_version": "4.14.7",
    }

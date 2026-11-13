"""Tests for the capture harness (runbook Phase 6), with a fake vmrun, ssh, scp
and clock. Nothing here touches a VM and no real time passes.

Each test checks one rule from the runbook or DECISIONS:
- the checks before a run stop everything before any VM command (requirement 9);
- the change comes before the START fence (D2, DECISIONS 2026-09-14);
- the window has a fixed length (DECISIONS 2026-11-13);
- guest calls are counted (requirement 10) and the password never reaches a file;
- the export is checked against its hash (step 10);
- a missing END fence or an unconfirmed change voids the run (requirements 2, 11);
- a window across midnight exports both dates (step 10).

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.harness import (Change, GuestStep, HarnessError, Lab, LabConfig, Result, capture,
                           parameters_hash)

from test_archive import fence, logon_type2

PASSWORD = "not-a-real-password-123"


class Clock:
    def __init__(self, start: datetime):
        self.t = start

    def now(self) -> datetime:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += timedelta(seconds=seconds)


class FakeRunner:
    """Answers vmrun, ipconfig, ssh and scp like the real lab, and records every call."""

    def __init__(self, clock: Clock, archive_by_date: dict[str, list[str]], *, lab_ip="10.20.10.1",
                 program_results: dict[str, tuple[int, float]] | None = None, bad_hash=False):
        self.clock, self.archive, self.lab_ip, self.bad_hash = clock, archive_by_date, lab_ip, bad_hash
        self.program_results = program_results or {}
        self.calls: list[tuple[datetime, list[str]]] = []
        self._gz: dict[str, bytes] = {}

    def __call__(self, args: list[str]) -> Result:
        self.calls.append((self.clock.now(), list(args)))
        tool = Path(args[0]).name.lower()
        if tool == "ipconfig":
            return Result(0, f"IPv4 Address. . . . . . . . . . . : {self.lab_ip}\n")
        if tool == "vmrun":
            if "checkToolsState" in args:
                return Result(0, "running\n")
            if "runProgramInGuest" in args:
                program = args[args.index("runProgramInGuest") + 2]
                code, seconds = self.program_results.get(Path(program).name, (0, 1.0))
                self.clock.sleep(seconds)
                return Result(code, "")
            return Result(0, "")
        if tool == "ssh":
            cmd = args[-1]
            if "export" in cmd:
                date = cmd.split()[-1]
                data = gzip.compress(("\n".join(self.archive.get(date, [])) + "\n").encode())
                path = f"/tmp/telos-archive-{date}.json.gz"
                self._gz[path] = data
                sha = "0" * 64 if self.bad_hash else hashlib.sha256(data).hexdigest()
                return Result(0, f"{path}\nbytes_gz   {len(data)}\nsha256_gz  {sha}\nlines      1\n")
            return Result(0, "ok\n")
        if tool == "scp":
            src, dest = args[-2], Path(args[-1])
            dest.write_bytes(self._gz[src.split(":", 1)[1]])
            return Result(0, "")
        return Result(0, "")

    def vmrun_ops(self) -> list[str]:
        ops = []
        for _, a in self.calls:
            if Path(a[0]).name.lower() == "vmrun":
                if "runProgramInGuest" in a:
                    i = a.index("runProgramInGuest")
                    ops.append("guest:" + " ".join([Path(a[i + 2]).name] + a[i + 3:]))
                else:
                    ops.append(a[3])
        return ops

    def time_of(self, op: str) -> datetime:
        for t, a in self.calls:
            if "runProgramInGuest" in a and op in " ".join(a):
                return t
        raise AssertionError(f"no call {op!r}")


def archive_for(run_id: str, start: str, end: str, inside: str = "2026-11-20T10:05:00.0000000Z") -> list[str]:
    return [fence("START", run_id, start), logon_type2(inside), fence("END", run_id, end)]


def make(tmp_path, *, start=datetime(2026, 11, 20, 10, 0, 0), window_s=600, archive=None, **runner_kw):
    pw = tmp_path / "guest.pw"
    pw.write_text(PASSWORD)
    clock = Clock(start)
    archive = archive or {start.strftime("%Y-%m-%d"): archive_for("run-1", "2026-11-20T10:03:05.0000000Z",
                                                                    "2026-11-20T10:13:05.0000000Z")}
    runner = FakeRunner(clock, archive, **runner_kw)
    cfg = LabConfig(vmrun="vmrun", vmx="F:/lab/WIN-EP-01.vmx", snapshot="cfg-suppressed", guest_user="eli",
                    password_file=pw, ssh_key=tmp_path / "key", runs_dir=tmp_path / "runs", window_s=window_s)
    lab = Lab(cfg, runner, now=clock.now, sleep=clock.sleep)
    return lab, runner, clock


ATTACK = [GuestStep("T1003.001-1", "powershell.exe", ("-c", "Invoke-AtomicTest T1003.001 -TestNumbers 1"))]
PARAMS = {"atomic_tests": ["T1003.001-1"], "rule_folder_sha256": "a3f9749e"}


def test_parameters_hash_does_not_depend_on_key_order():
    assert parameters_hash({"a": 1, "b": [2, 3]}) == parameters_hash({"b": [2, 3], "a": 1})


def test_a_failed_check_stops_the_run_before_any_vm_command(tmp_path):
    lab, runner, _ = make(tmp_path, lab_ip="192.168.1.5")
    with pytest.raises(HarnessError, match="10.20.10.1"):
        capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert runner.vmrun_ops() == []


def test_the_change_is_applied_and_confirmed_before_the_start_fence(tmp_path):
    lab, runner, _ = make(tmp_path)
    change = Change("C3", apply=(GuestStep("set", "reg.exe", ("add", "x")),),
                    verify=GuestStep("check", "check.exe"), reboot=True)
    capture(lab, "run-1", "post", ATTACK, PARAMS, change=change)
    ops = runner.vmrun_ops()
    assert ops[:2] == ["revertToSnapshot", "start"]
    start_fence = ops.index("guest:telos-fence.exe START run-1")
    assert ops.index("guest:reg.exe add x") < ops.index("reset") < ops.index("guest:check.exe") < start_fence
    assert ops[-1] == "stop"


def test_the_window_has_a_fixed_length(tmp_path):
    lab, runner, _ = make(tmp_path, window_s=600, program_results={"powershell.exe": (0, 95.0)})
    capture(lab, "run-1", "pre", ATTACK, PARAMS)
    gap = runner.time_of("END run-1") - runner.time_of("START run-1")
    assert gap == timedelta(seconds=600)


def test_tests_longer_than_the_window_void_the_run(tmp_path):
    lab, _, _ = make(tmp_path, window_s=600, program_results={"powershell.exe": (0, 700.0)})
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert m["record"]["valid"] is False
    assert any("longer than the window" in r for r in m["record"]["void_reasons"])


def test_guest_calls_are_counted_and_the_password_is_never_written(tmp_path):
    lab, runner, _ = make(tmp_path)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    guest_calls = sum(1 for _, a in runner.calls if "runProgramInGuest" in a)
    assert m["record"]["guest_calls"] == guest_calls == 3       # START fence, one test, END fence
    run_dir = tmp_path / "runs" / "run-1"
    for f in run_dir.iterdir():
        if f.suffix == ".json":
            assert PASSWORD not in f.read_text()


def test_the_manifest_hashes_only_the_parameters(tmp_path):
    lab, _, _ = make(tmp_path)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert m["parameters_sha256"] == parameters_hash(m["parameters"])
    assert m["parameters"]["window_s"] == 600 and "run_id" not in m["parameters"]
    saved = json.loads((tmp_path / "runs" / "run-1" / "run_manifest.json").read_text())
    assert saved["parameters_sha256"] == m["parameters_sha256"]


def test_a_wrong_export_hash_stops_the_run(tmp_path):
    lab, _, _ = make(tmp_path, bad_hash=True)
    with pytest.raises(HarnessError, match="SHA256"):
        capture(lab, "run-1", "pre", ATTACK, PARAMS)


def test_counts_and_fired_rules_are_written_for_the_analyser(tmp_path):
    lab, _, _ = make(tmp_path)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    counts = json.loads((tmp_path / "runs" / "run-1" / "counts.json").read_text())
    assert counts["counts"]["Security-4624[AuthenticationPackageName=other,LogonType=2,TargetUserName]"] == 1
    assert m["record"]["valid"] is True


def test_a_missing_end_fence_voids_the_run(tmp_path):
    archive = {"2026-11-20": archive_for("run-1", "2026-11-20T10:03:05.0000000Z", "x")[:2]}
    lab, _, _ = make(tmp_path, archive=archive)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert m["record"]["valid"] is False
    assert any("END fence" in r for r in m["record"]["void_reasons"])


def test_a_change_not_confirmed_in_the_guest_voids_the_run(tmp_path):
    lab, _, _ = make(tmp_path, program_results={"check.exe": (1, 1.0)})
    change = Change("C3", apply=(GuestStep("set", "reg.exe"),), verify=GuestStep("check", "check.exe"))
    m = capture(lab, "run-1", "post", ATTACK, PARAMS, change=change)
    assert m["record"]["change_confirmed"] is False
    assert any("not confirmed" in r for r in m["record"]["void_reasons"])


CONFIG_S = (GuestStep("config-S", "config-S-defender-off.ps1"),)


def test_after_boot_steps_run_after_the_reset_and_again_after_a_change_reboot(tmp_path):
    """Config S must hold after every boot: Defender ignored its stored setting right after a
    restart on 2026-11-13 (COMMANDS 2.13)."""
    lab, runner, _ = make(tmp_path)
    lab.cfg.after_boot = CONFIG_S
    change = Change("C3", apply=(GuestStep("set", "reg.exe"),), verify=GuestStep("check", "check.exe"),
                    reboot=True)
    m = capture(lab, "run-1", "post", ATTACK, PARAMS, change=change)
    ops = runner.vmrun_ops()
    config_runs = [i for i, op in enumerate(ops) if op == "guest:config-S-defender-off.ps1"]
    assert len(config_runs) == 2
    assert config_runs[0] < ops.index("guest:reg.exe") < ops.index("reset") < config_runs[1] < ops.index("guest:check.exe")
    assert [s["exit_code"] for s in m["record"]["after_boot"]] == [0, 0]
    assert m["record"]["valid"] is True


def test_a_failed_after_boot_step_voids_the_run(tmp_path):
    lab, _, _ = make(tmp_path, program_results={"config-S-defender-off.ps1": (1, 60.0)})
    lab.cfg.after_boot = CONFIG_S
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert m["record"]["valid"] is False
    assert any("config-S" in r for r in m["record"]["void_reasons"])


def test_a_window_across_midnight_exports_both_dates(tmp_path):
    start = datetime(2026, 11, 20, 23, 50, 0)
    archive = {"2026-11-20": [fence("START", "run-1", "2026-11-20T23:53:05.0000000Z")],
               "2026-11-21": [logon_type2("2026-11-21T00:00:05.0000000Z"),
                              fence("END", "run-1", "2026-11-21T00:03:05.0000000Z")]}
    lab, runner, _ = make(tmp_path, start=start, archive=archive)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert [e["date"] for e in m["record"]["exports"]] == ["2026-11-20", "2026-11-21"]
    assert m["record"]["valid"] is True

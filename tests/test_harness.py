"""Tests for the capture harness (runbook Phase 6), with a fake vmrun, ssh, scp
and clock. Nothing here touches a VM and no real time passes.

Each test checks one rule from the runbook or DECISIONS:
- the checks before a run stop everything before any VM command (requirement 9);
- the change comes before the START fence (D2, DECISIONS 2026-09-14);
- the window has a fixed length (DECISIONS 2026-11-13);
- guest calls are counted (requirement 10) and the password never reaches a file;
- the export is checked against its hash (step 10);
- a missing END fence or an unconfirmed change voids the run (requirements 2, 11);
- a window across midnight exports both dates (step 10);
- the wait for VMware Tools wakes a status stuck at "installed", and still ends when Tools
  never answers (COMMANDS 2.19; DECISIONS 2026-11-27);
- item 22's void rule: a fingerprint outside its range, or a required step that did not exit 0,
  voids the run, and the rule never changes the parameters hash (DECISIONS 2026-11-27).

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

from telos.harness import (Change, GuestStep, HarnessError, HostStep, Lab, LabConfig, Result, capture,
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
        self.timeouts: list[float] = []          # the time limit of every call that had one
        self._gz: dict[str, bytes] = {}

    def __call__(self, args: list[str], timeout: float | None = None) -> Result:
        self.calls.append((self.clock.now(), list(args)))
        if timeout is not None:
            self.timeouts.append(timeout)
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
        code, seconds = self.program_results.get(tool, (0, 0.0))       # a host step, for example
        self.clock.sleep(seconds)
        return Result(code, "")

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


def make(tmp_path, *, start=datetime(2026, 11, 20, 10, 0, 0), window_s=600, archive=None,
         runner_cls=None, **runner_kw):
    pw = tmp_path / "guest.pw"
    pw.write_text(PASSWORD)
    clock = Clock(start)
    archive = archive or {start.strftime("%Y-%m-%d"): archive_for("run-1", "2026-11-20T10:03:05.0000000Z",
                                                                    "2026-11-20T10:13:05.0000000Z")}
    runner = (runner_cls or FakeRunner)(clock, archive, **runner_kw)
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


def test_recount_rereads_a_run_whose_window_was_unreadable(tmp_path):
    """test-pre-1 (2026-11-16) was voided only because the reader missed vmrun's quoted fences.
    A recount reads the saved archive again; it adds a note and leaves the parameters alone."""
    from telos.harness import recount
    lab, _, _ = make(tmp_path)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    run_dir = tmp_path / "runs" / "run-1"
    (run_dir / "counts.json").unlink()
    m["record"]["void_reasons"] = ["window not readable: no START fence for run 'run-1'"]
    m["record"]["valid"] = False
    (run_dir / "run_manifest.json").write_text(json.dumps(m))
    after = recount(run_dir)
    assert after["record"]["valid"] is True and after["record"]["void_reasons"] == []
    assert after["record"]["recounts"][0]["reasons_before"] == ["window not readable: no START fence for run 'run-1'"]
    assert after["parameters_sha256"] == m["parameters_sha256"]
    assert (run_dir / "counts.json").exists()


def test_recount_keeps_other_void_reasons(tmp_path):
    from telos.harness import recount
    lab, _, _ = make(tmp_path, program_results={"check.exe": (1, 1.0)})
    change = Change("C3", apply=(GuestStep("set", "reg.exe"),), verify=GuestStep("check", "check.exe"))
    capture(lab, "run-1", "post", ATTACK, PARAMS, change=change)
    after = recount(tmp_path / "runs" / "run-1")
    assert after["record"]["valid"] is False
    assert any("not confirmed" in r for r in after["record"]["void_reasons"])


def test_an_extra_reboot_comes_before_the_start_fence_and_is_recorded(tmp_path):
    """Spike Q6: a control run with one extra reboot and settle, as a post-change run has (D2)."""
    lab, runner, _ = make(tmp_path)
    lab.cfg.after_boot = CONFIG_S
    m = capture(lab, "run-1", "control", ATTACK, PARAMS, extra_reboot=True)
    ops = runner.vmrun_ops()
    assert ops.index("reset") < ops.index("guest:telos-fence.exe START run-1")
    assert len([op for op in ops if op == "guest:config-S-defender-off.ps1"]) == 2
    assert m["record"]["extra_reboot"] is True


def test_the_record_has_the_runs_own_start_and_end_time(tmp_path):
    """Spike Q2: the real time per run, from before the checks to after the export."""
    lab, _, clock = make(tmp_path)
    start = clock.now()
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    began = datetime.fromisoformat(m["record"]["run_started_host_utc"])
    ended = datetime.fromisoformat(m["record"]["run_finished_host_utc"])
    assert began == start and ended > began
    assert m["record"]["run_seconds"] == (ended - began).total_seconds()


def test_a_window_across_midnight_exports_both_dates(tmp_path):
    start = datetime(2026, 11, 20, 23, 50, 0)
    archive = {"2026-11-20": [fence("START", "run-1", "2026-11-20T23:53:05.0000000Z")],
               "2026-11-21": [logon_type2("2026-11-21T00:00:05.0000000Z"),
                              fence("END", "run-1", "2026-11-21T00:03:05.0000000Z")]}
    lab, runner, _ = make(tmp_path, start=start, archive=archive)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert [e["date"] for e in m["record"]["exports"]] == ["2026-11-20", "2026-11-21"]
    assert m["record"]["valid"] is True


class StuckToolsRunner(FakeRunner):
    """The lab after the host start of 2026-11-26 15:51 UTC (COMMANDS 2.19): Tools runs in the guest,
    but `checkToolsState` says "installed" until something has waited on Tools with
    `getGuestIPAddress -wait`. With `tools_answer=False`, the wait runs out its time limit instead."""

    def __init__(self, *args, tools_answer: bool = True, **kw):
        super().__init__(*args, **kw)
        self.tools_answer, self.woken = tools_answer, False

    def __call__(self, args: list[str], timeout: float | None = None) -> Result:
        if Path(args[0]).name.lower() == "vmrun" and "checkToolsState" in args:
            self.calls.append((self.clock.now(), list(args)))
            return Result(0, "running\n" if self.woken else "installed\n")
        if Path(args[0]).name.lower() == "vmrun" and "getGuestIPAddress" in args and "-wait" in args:
            self.calls.append((self.clock.now(), list(args)))
            if timeout is not None:
                self.timeouts.append(timeout)
            if self.tools_answer:
                self.clock.sleep(15)                    # Tools comes up about 15 s after the start
                self.woken = True
                return Result(0, "10.20.10.20\n")
            self.clock.sleep(timeout or 0)              # the real runner stops vmrun at its limit
            return Result(124, "")
        return super().__call__(args, timeout)


def test_a_tools_status_stuck_at_installed_is_woken_and_the_run_goes_on(tmp_path):
    """2026-11-26: eval-ctl-1 stopped twice with 'VMware Tools not running after 300 s' while Tools
    ran; one `getGuestIPAddress -wait` woke the status in 0.4 s (COMMANDS 2.19)."""
    lab, runner, _ = make(tmp_path, runner_cls=StuckToolsRunner)
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS)
    ops = runner.vmrun_ops()
    assert ops.index("start") < ops.index("getGuestIPAddress") < ops.index("guest:telos-fence.exe START run-1")
    assert runner.timeouts == [lab.cfg.tools_timeout_s]          # the wait always has a time limit
    assert m["record"]["valid"] is True


def test_tools_that_never_answer_stop_the_run_before_any_guest_call(tmp_path):
    lab, runner, clock = make(tmp_path, runner_cls=StuckToolsRunner, tools_answer=False)
    began = clock.now()
    with pytest.raises(HarnessError, match="VMware Tools not running"):
        capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert runner.timeouts == [lab.cfg.tools_timeout_s]          # the wait was tried, with its limit
    assert not any("runProgramInGuest" in a for _, a in runner.calls)
    assert not (tmp_path / "runs" / "run-1").exists()            # no data
    assert clock.now() - began <= timedelta(seconds=2 * lab.cfg.tools_timeout_s + 10)   # it always ends


def test_a_working_tools_status_needs_no_extra_wait(tmp_path):
    """When the first check already says "running", the harness goes on at once, with no extra wait."""
    lab, runner, _ = make(tmp_path)
    capture(lab, "run-1", "pre", ATTACK, PARAMS)
    assert "getGuestIPAddress" not in runner.vmrun_ops()


def test_the_real_runner_stops_a_program_that_passes_its_time_limit():
    from telos.harness import TIMED_OUT, run_command
    r = run_command([sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.5)
    assert r.returncode == TIMED_OUT


# --- item 22's void rule (DECISIONS 2026-11-27) ---------------------------------

def process_start(time: str) -> str:
    """One Sysmon 1 event, a process start inside the window."""
    from test_archive import SYSMON, line
    return line(SYSMON, "1", time, {"image": "C:\\\\x\\\\a.exe", "commandLine": "a.exe"})


def archive_with_processes(n: int) -> dict[str, list[str]]:
    starts = [process_start(f"2026-11-20T10:05:{i:02d}.0000000Z") for i in range(n)]
    return {"2026-11-20": [fence("START", "run-1", "2026-11-20T10:03:05.0000000Z"), *starts,
                           fence("END", "run-1", "2026-11-20T10:13:05.0000000Z")]}


SIGNIN = HostStep("rdp-signin-30s", ("rdp.exe",))


def test_a_fingerprint_outside_its_range_voids_the_run(tmp_path):
    from telos.harness import RunChecks
    lab, _, _ = make(tmp_path, archive=archive_with_processes(3))
    m = capture(lab, "run-1", "pre", ATTACK, PARAMS, checks=RunChecks(fingerprint_min=10, fingerprint_max=20))
    assert m["record"]["valid"] is False
    assert any("fingerprint" in r for r in m["record"]["void_reasons"])


def test_a_required_step_that_did_not_exit_0_voids_the_run(tmp_path):
    """The sign-in step exits 1 when mstsc closed before its 30 s, so the sign-in did not hold."""
    from telos.harness import RunChecks
    lab, _, _ = make(tmp_path, archive=archive_with_processes(3), program_results={"rdp.exe": (1, 30.0)})
    m = capture(lab, "run-1", "pre", [SIGNIN, *ATTACK], PARAMS,
                checks=RunChecks(fingerprint_min=0, fingerprint_max=1000, must_succeed=("rdp-signin-30s",)))
    assert m["record"]["valid"] is False
    assert any("rdp-signin-30s" in r and "exit code 1" in r for r in m["record"]["void_reasons"])


def test_a_run_that_passes_the_rule_stays_valid_and_records_the_rule(tmp_path):
    from telos.harness import RunChecks
    lab, _, _ = make(tmp_path, archive=archive_with_processes(3))
    rule = RunChecks(fingerprint_min=0, fingerprint_max=1000, must_succeed=("rdp-signin-30s",))
    m = capture(lab, "run-1", "pre", [SIGNIN, *ATTACK], PARAMS, checks=rule)
    assert m["record"]["valid"] is True
    rc = m["record"]["run_checks"]
    assert rc["fingerprint"] >= 3 and rc["fingerprint_min"] == 0 and rc["must_succeed"] == ["rdp-signin-30s"]


def test_the_void_rule_never_changes_the_parameters_hash(tmp_path):
    """The 5 control runs were made before the rule existed; the runs after must keep their hash."""
    from telos.harness import RunChecks
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    a_lab, _, _ = make(tmp_path / "a", archive=archive_with_processes(3))
    b_lab, _, _ = make(tmp_path / "b", archive=archive_with_processes(3))
    without = capture(a_lab, "run-1", "pre", ATTACK, PARAMS)
    with_rule = capture(b_lab, "run-1", "pre", ATTACK, PARAMS, checks=RunChecks(fingerprint_min=0, fingerprint_max=9))
    assert with_rule["parameters_sha256"] == without["parameters_sha256"]
    assert "run_checks" not in with_rule["parameters"]


def test_the_catalogs_range_is_the_control_mean_plus_or_minus_3_sd():
    """From eval-ctl-1 to eval-ctl-5 (COMMANDS 2.19): 100, 118, 119, 99, 118."""
    import statistics
    from telos.catalog import CONTROL_FINGERPRINTS, RUN_CHECKS, rdp_signin
    assert CONTROL_FINGERPRINTS == (100, 118, 119, 99, 118)
    m, sd = statistics.mean(CONTROL_FINGERPRINTS), statistics.stdev(CONTROL_FINGERPRINTS)
    assert RUN_CHECKS.fingerprint_min == pytest.approx(m - 3 * sd)
    assert RUN_CHECKS.fingerprint_max == pytest.approx(m + 3 * sd)
    assert RUN_CHECKS.passes(80) and not RUN_CHECKS.passes(79)
    assert RUN_CHECKS.passes(141) and not RUN_CHECKS.passes(142)
    assert RUN_CHECKS.must_succeed == (rdp_signin().name,)

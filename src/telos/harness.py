"""The capture harness: one capture window, run from the host (runbook Phase 6).

It drives WIN-EP-01 with `vmrun`, collects the run's archive from SIEM-01 with
`telos-archive export` over SSH, counts the window with archive.py, and writes a
two-part run manifest. Every step follows runbook Phase 6 and the requirements
listed there; each is named where it is done.

One window, in order (runbook Phase 6):

    checks before the run   VMnet2 holds the host's lab address, SSH to SIEM-01 answers,
                            telos-archive disk answers, free space on the host (requirement 9)
    1-3  reset              revert to the snapshot, start, wait for VMware Tools, settle
    4    change             post-change runs only: apply, reboot if needed and settle,
                            then confirm in the guest (requirement 11). Before the fence (D2).
    5    START fence
    6    attack tests       each step's exit code and duration recorded (requirement 3)
         fixed window       wait until the window has its set length (DECISIONS 2026-11-13)
    7    END fence
    8    drain              let the agent and the manager write the tail
    9    stop
    10   export             every date the window touched; checked against size and SHA256
    11   manifest           `parameters` (hashed, sorted keys) and `record` (not hashed)

**Who runs it.** Guest steps pass the guest password to `vmrun` (`-gp`), read from the
password file at the moment of the call. The password is never stored in an
object, a log or a file. A person runs the harness; it is not run by an assistant.

**What it does not decide.** Whether a run is voided for a moved stimulus fingerprint
(OPEN-QUESTIONS 22) is decided later from the spike data; the harness records what
that needs (exit codes, durations, guest calls, event counts) and voids only on the
reasons it can know: tests longer than the window, a change not confirmed, a window
that cannot be read (for example no END fence).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Union

from .archive import count_window


class HarnessError(RuntimeError):
    """A condition that must stop the run before it produces data."""


@dataclass(frozen=True)
class Result:
    returncode: int
    stdout: str = ""


def run_command(args: list[str]) -> Result:
    """The real runner: run a host program and capture its output."""
    p = subprocess.run(args, capture_output=True, text=True)
    return Result(p.returncode, p.stdout)


@dataclass(frozen=True)
class GuestStep:
    """A program run inside WIN-EP-01 with `vmrun runProgramInGuest`."""

    name: str
    program: str
    args: tuple[str, ...] = ()


@dataclass(frozen=True)
class HostStep:
    """A program run on the host, for example the C5 Remote Desktop sign-in."""

    name: str
    args: tuple[str, ...]


Step = Union[GuestStep, HostStep]


@dataclass(frozen=True)
class Change:
    """A hardening change: how to apply it and how to confirm it took effect."""

    change_id: str
    apply: tuple[GuestStep, ...]
    verify: GuestStep                 # exit code 0 means the change took effect
    reboot: bool = False
    script_sha256: str = ""


@dataclass
class LabConfig:
    vmrun: str
    vmx: str
    snapshot: str
    guest_user: str
    password_file: Path
    ssh_key: Path
    siem: str = "eli@10.20.10.10"
    agent: str = "WIN-EP-01"
    fence_exe: str = r"C:\telos\telos-fence.exe"
    runs_dir: Path = Path("data/runs")
    backup_dir: Path | None = None     # requirement 8: a second physical drive
    host_lab_ip: str = "10.20.10.1"
    settle_s: int = 180
    drain_s: int = 120
    window_s: int = 600                # fixed window length; set after the spike
    tools_timeout_s: int = 300
    min_free_bytes: int = 1_000_000_000
    # Guest steps run after every boot (after the reset and after a change's reboot), for
    # example Config S's Defender-off script; exit code 0 = in force, otherwise the run is voided.
    after_boot: tuple[GuestStep, ...] = ()


def parameters_hash(parameters: dict) -> str:
    """SHA256 of the parameters, serialised with sorted keys (runbook step 11)."""
    text = json.dumps(parameters, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Lab:
    """The host's view of the lab: vmrun for WIN-EP-01, ssh and scp for SIEM-01."""

    def __init__(self, cfg: LabConfig, runner: Callable[[list[str]], Result] = run_command,
                 now: Callable[[], datetime] = _utcnow, sleep: Callable[[float], None] = time.sleep):
        self.cfg, self.run, self.now, self.sleep = cfg, runner, now, sleep
        self.guest_calls = 0

    # --- WIN-EP-01 ----------------------------------------------------------
    def vmrun(self, *args: str) -> Result:
        return self.run([self.cfg.vmrun, "-T", "ws", *args])

    def guest(self, step: GuestStep) -> Result:
        """Run a program in the guest. Counted, because each call writes logons (requirement 10)."""
        self.guest_calls += 1
        password = self.cfg.password_file.read_text(encoding="utf-8").strip()
        return self.run([self.cfg.vmrun, "-T", "ws", "-gu", self.cfg.guest_user, "-gp", password,
                         "runProgramInGuest", self.cfg.vmx, step.program, *step.args])

    def host(self, step: HostStep) -> Result:
        return self.run(list(step.args))

    def wait_tools(self) -> None:
        waited = 0
        while waited <= self.cfg.tools_timeout_s:
            if "running" in self.vmrun("checkToolsState", self.cfg.vmx).stdout:
                return
            self.sleep(5)
            waited += 5
        raise HarnessError(f"VMware Tools not running after {self.cfg.tools_timeout_s} s")

    def reset_to_known_state(self) -> None:
        """Requirement 5: the one function that returns the endpoint to a known state."""
        if self.vmrun("revertToSnapshot", self.cfg.vmx, self.cfg.snapshot).returncode != 0:
            raise HarnessError(f"revert to snapshot {self.cfg.snapshot!r} failed")
        if self.vmrun("start", self.cfg.vmx, "nogui").returncode != 0:
            raise HarnessError("vmrun start failed")
        self.wait_tools()
        self.sleep(self.cfg.settle_s)

    def reboot_and_settle(self) -> None:
        self.vmrun("reset", self.cfg.vmx, "soft")
        self.sleep(30)
        self.wait_tools()
        self.sleep(self.cfg.settle_s)

    def fence(self, word: str, run_id: str) -> Result:
        return self.guest(GuestStep(f"fence-{word}", self.cfg.fence_exe, (word, run_id)))

    def stop(self) -> None:
        self.vmrun("stop", self.cfg.vmx, "soft")

    # --- SIEM-01 ------------------------------------------------------------
    def ssh(self, command: str) -> Result:
        return self.run(["ssh", "-i", str(self.cfg.ssh_key), "-o", "BatchMode=yes", self.cfg.siem, command])

    def preflight(self) -> dict:
        """Requirement 9 and the disk guard: abort before touching the VM."""
        if self.cfg.host_lab_ip not in self.run(["ipconfig"]).stdout:
            raise HarnessError(f"the host's lab address {self.cfg.host_lab_ip} is missing (OPEN-QUESTIONS 27)")
        if self.ssh("date -u +%Y-%m-%dT%H:%M:%S").returncode != 0:
            raise HarnessError("SSH to SIEM-01 does not answer")
        disk = self.ssh("sudo -n /usr/local/sbin/telos-archive disk")
        if disk.returncode != 0:
            raise HarnessError("telos-archive disk failed on SIEM-01")
        self.cfg.runs_dir.mkdir(parents=True, exist_ok=True)
        free = shutil.disk_usage(self.cfg.runs_dir).free
        if free < self.cfg.min_free_bytes:
            raise HarnessError(f"only {free} bytes free on the host for runs")
        return {"siem_disk": disk.stdout.strip(), "host_free_bytes": free}

    def export(self, date: str, dest_dir: Path) -> dict:
        """Step 10: export one date, copy it, and check it against size and SHA256."""
        out = self.ssh(f"sudo -n /usr/local/sbin/telos-archive export {date}")
        path = re.search(r"(/tmp/\S+\.gz)", out.stdout)
        size = re.search(r"bytes_gz\s+(\d+)", out.stdout)
        sha = re.search(r"sha256_gz\s+([0-9a-f]{64})", out.stdout)
        lines = re.search(r"lines\s+(\d+)", out.stdout)
        if out.returncode != 0 or not (path and size and sha):
            raise HarnessError(f"telos-archive export {date} gave no path, size or SHA256")
        dest = dest_dir / f"archive-{date}.json.gz"
        self.run(["scp", "-i", str(self.cfg.ssh_key), "-o", "BatchMode=yes",
                  f"{self.cfg.siem}:{path.group(1)}", str(dest)])
        data = dest.read_bytes() if dest.exists() else b""
        if len(data) != int(size.group(1)) or hashlib.sha256(data).hexdigest() != sha.group(1):
            raise HarnessError(f"export {date}: the copy does not match its size or SHA256")
        return {"date": date, "file": dest.name, "bytes_gz": len(data), "sha256_gz": sha.group(1),
                "lines": int(lines.group(1)) if lines else None}


def capture(lab: Lab, run_id: str, phase: str, stimulus: list[Step], parameters: dict,
            change: Change | None = None) -> dict:
    """Run one capture window and write its folder. Returns the manifest."""
    cfg = lab.cfg
    checks = lab.preflight()
    lab.guest_calls = 0
    reasons: list[str] = []

    after_boot: list[dict] = []

    def run_after_boot() -> None:
        for step in cfg.after_boot:
            code = lab.guest(step).returncode
            after_boot.append({"name": step.name, "exit_code": code})
            if code != 0:
                reasons.append(f"after-boot step {step.name} failed (exit code {code})")

    lab.reset_to_known_state()
    run_after_boot()

    confirmed = None
    if change is not None:                                   # step 4, before the fence (D2)
        for step in change.apply:
            lab.guest(step)
        if change.reboot:
            lab.reboot_and_settle()
            run_after_boot()
        confirmed = lab.guest(change.verify).returncode == 0
        if not confirmed:
            reasons.append(f"change {change.change_id} not confirmed in the guest")

    t_start = lab.now()
    lab.fence("START", run_id)                               # step 5
    steps = []
    for step in stimulus:                                    # step 6
        t0 = lab.now()
        res = lab.guest(step) if isinstance(step, GuestStep) else lab.host(step)
        steps.append({"name": step.name, "exit_code": res.returncode,
                      "seconds": round((lab.now() - t0).total_seconds(), 3)})
    elapsed = (lab.now() - t_start).total_seconds()
    if elapsed > cfg.window_s:
        reasons.append(f"tests took {elapsed:.0f} s, longer than the window of {cfg.window_s} s")
    else:
        lab.sleep(cfg.window_s - elapsed)                    # fixed window (DECISIONS 2026-11-13)
    t_end = lab.now()
    lab.fence("END", run_id)                                 # step 7
    lab.sleep(cfg.drain_s)                                   # step 8
    lab.stop()                                               # step 9

    run_dir = cfg.runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    dates = sorted({t_start.strftime("%Y-%m-%d"), t_end.strftime("%Y-%m-%d")})
    exports = [lab.export(d, run_dir) for d in dates]        # step 10

    lines: list[str] = []
    for e in exports:
        with gzip.open(run_dir / e["file"], "rt", encoding="utf-8") as fh:
            lines.extend(fh.readlines())
    window = None
    try:                                                     # requirement 2: the END fence arrived
        w = count_window(lines, cfg.agent, run_id)
        window = {"start": w.start, "end": w.end, "n_events": w.n_events, "broken_lines": w.broken_lines}
        (run_dir / "counts.json").write_text(json.dumps(
            {"run_id": run_id, "counts": w.counts, "fired": w.fired, **window}, indent=2, sort_keys=True))
    except ValueError as exc:
        reasons.append(f"window not readable: {exc}")

    params = {**parameters, "window_s": cfg.window_s, "settle_s": cfg.settle_s, "drain_s": cfg.drain_s,
              "snapshot": cfg.snapshot, "agent": cfg.agent,
              "stimulus": [s.name for s in stimulus], "after_boot": [s.name for s in cfg.after_boot]}
    manifest = {
        "parameters": params,
        "parameters_sha256": parameters_hash(params),
        "record": {
            "run_id": run_id, "phase": phase,
            "change_id": change.change_id if change else None,
            "change_script_sha256": change.script_sha256 if change else None,
            "change_confirmed": confirmed,
            "start_fence_host_utc": t_start.isoformat(), "end_fence_host_utc": t_end.isoformat(),
            "after_boot": after_boot, "stimulus": steps, "guest_calls": lab.guest_calls,
            "exports": exports, "window": window, "checks": checks,
            "void_reasons": reasons, "valid": not reasons,
        },
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    if cfg.backup_dir is not None:                           # requirement 8
        shutil.copytree(run_dir, cfg.backup_dir / run_id, dirs_exist_ok=True)
    return manifest

"""Run one capture window on the real lab. **The student runs this**: it passes the
guest password to vmrun.

    .venv/Scripts/python.exe src/capture.py --run-id test-pre-1 --phase pre
    .venv/Scripts/python.exe src/capture.py --run-id test-post-1 --phase post --change C3

It reverts WIN-EP-01 to the golden snapshot (catalog.GOLDEN_SNAPSHOT), applies the change for an "after" run,
fires the fences, runs the pinned attack list (or the spike's with --stimulus trial; the
pinned list opens a Remote Desktop window on the host for 30 s), waits out the fixed window, exports
the archive from SIEM-01, and writes data/runs/<run-id>/ (runbook Phase 6).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telos.catalog import (CHANGES, CONFIG_S, GOLDEN_SNAPSHOT, RUN_CHECKS, parameters,  # noqa: E402
                           pinned_stimulus, trial_stimulus)
from telos.harness import HarnessError, Lab, LabConfig, capture, recount  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
HOME = Path(os.environ["USERPROFILE"])


def main() -> int:
    ap = argparse.ArgumentParser(description="One capture window on the TeLoS lab.")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--phase", choices=["control", "pre", "post"], help="required unless --recount")
    ap.add_argument("--recount", action="store_true",
                    help="read a finished run's saved archive again (no VM, no password)")
    ap.add_argument("--change", choices=sorted(CHANGES), help="required for --phase post, refused otherwise")
    ap.add_argument("--config", default="S", choices=["S", "N"], help="S: Defender off after every boot")
    ap.add_argument("--window-s", type=int, default=180, help="fixed window; the spike sets the final value")
    ap.add_argument("--backup-dir", default=None, help="a folder on a second drive (runbook requirement 8)")
    ap.add_argument("--stimulus", default="pinned", choices=["pinned", "trial"],
                    help="pinned: the study's list (RDP sign-in, then the LSASS tests); trial: the spike's")
    a = ap.parse_args()
    if a.recount:
        m = recount(REPO / "data" / "runs" / a.run_id)
        r = m["record"]
        print(f"recounted {a.run_id}: valid {r['valid']}   void reasons: {r['void_reasons'] or '-'}")
        print(f"window: {r['window']}")
        return 0 if r["valid"] else 1
    if a.phase is None:
        ap.error("--phase is required unless --recount")
    if (a.phase == "post") != (a.change is not None):
        ap.error("--change is required for --phase post and refused for the other phases")

    cfg = LabConfig(
        vmrun=r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
        vmx=r"F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx",
        snapshot=GOLDEN_SNAPSHOT,          # catalog: one place for the name and its time
        guest_user="eli",
        password_file=HOME / ".telos" / "WIN-EP-01.pw",
        ssh_key=HOME / ".telos" / "siem01_ed25519",
        runs_dir=REPO / "data" / "runs",
        backup_dir=Path(a.backup_dir) if a.backup_dir else None,
        window_s=a.window_s,
        after_boot=CONFIG_S if a.config == "S" else (),
    )
    lab = Lab(cfg)
    change = CHANGES[a.change] if a.change else None
    stimulus = pinned_stimulus() if a.stimulus == "pinned" else trial_stimulus()
    # Item 22's void rule was measured with the pinned stimulus only (DECISIONS 2026-11-27).
    checks = RUN_CHECKS if a.stimulus == "pinned" else None
    print(f"run {a.run_id}: phase {a.phase}, change {a.change or '-'}, config {a.config}, window {a.window_s} s, "
          f"stimulus {a.stimulus}")
    try:
        m = capture(lab, a.run_id, a.phase, stimulus, parameters(a.config), change=change, checks=checks)
    except HarnessError as exc:
        print(f"STOPPED before producing data: {exc}", file=sys.stderr)
        return 2
    r = m["record"]
    print(f"valid: {r['valid']}   void reasons: {r['void_reasons'] or '-'}")
    print(f"after-boot: {r['after_boot']}")
    print(f"stimulus: {[(s['name'], s['exit_code'], s['seconds']) for s in r['stimulus']]}")
    print(f"guest calls: {r['guest_calls']}   window: {r['window']}")
    if r.get("run_checks"):
        rc = r["run_checks"]
        print(f"fingerprint: {rc['fingerprint']} (range {rc['fingerprint_min']:.1f} to {rc['fingerprint_max']:.1f})")
    print(f"exports: {[(e['date'], e['lines']) for e in r['exports']]}")
    print(f"folder: {cfg.runs_dir / a.run_id}")
    return 0 if r["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

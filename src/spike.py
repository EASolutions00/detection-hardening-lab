"""Run the feasibility spike's batch on the real lab. **The student runs this**: it passes
the guest password to vmrun. About 19 runs of about 10 minutes, unattended.

    .venv/Scripts/python.exe src/spike.py
    .venv/Scripts/python.exe src/spike.py --groups S-ctl N-ctl      (only some groups)
    .venv/Scripts/python.exe src/spike.py --analyse                 (answers Q1 to Q6; no VM, no password)

Runs already in data/runs/ are skipped, so it can be started again after an
interruption. See src/telos/spike.py for the plan.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telos.catalog import CHANGES, CONFIG_S, parameters, trial_stimulus  # noqa: E402
from telos.harness import Lab, LabConfig, capture  # noqa: E402
from telos.spike import PlannedRun, analyse_spike, run_batch, spike_plan  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
HOME = Path(os.environ["USERPROFILE"])


def main() -> int:
    ap = argparse.ArgumentParser(description="The TeLoS feasibility spike (runbook Phase 7).")
    ap.add_argument("--groups", nargs="+", choices=["S-ctl", "N-ctl", "reboot", "C3-pre", "C3-post"])
    ap.add_argument("--window-s", type=int, default=180)
    ap.add_argument("--backup-dir", default=None)
    ap.add_argument("--analyse", action="store_true",
                    help="answer Q1 to Q6 from the runs already captured (no VM, no password)")
    ap.add_argument("--out", default=str(REPO / "data" / "summaries"), help="where --analyse writes")
    a = ap.parse_args()
    if a.analyse:
        from run import _git_commit
        answers = analyse_spike(REPO / "data" / "runs", a.out, REPO / "data" / "rules" / "wazuh-4.14.7",
                                analyser_version=_git_commit())
        for q, v in answers.items():
            if q == "Q3" and isinstance(v, dict):
                v = {k: x for k, x in v.items() if k != "per_pair"}
            print(f"{q}: {v}")
        print(f"written to {a.out}")
        return 0
    plan = [r for r in spike_plan() if not a.groups or r.group in a.groups]

    def capture_one(run: PlannedRun) -> dict:
        cfg = LabConfig(
            vmrun=r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
            vmx=r"F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx",
            snapshot="golden-base", guest_user="eli",
            password_file=HOME / ".telos" / "WIN-EP-01.pw",
            ssh_key=HOME / ".telos" / "siem01_ed25519",
            runs_dir=REPO / "data" / "runs",
            backup_dir=Path(a.backup_dir) if a.backup_dir else None,
            window_s=a.window_s,
            after_boot=CONFIG_S if run.config == "S" else (),
        )
        change = CHANGES[run.change] if run.change else None
        return capture(Lab(cfg), run.run_id, run.phase, trial_stimulus(), parameters(run.config),
                       change=change, extra_reboot=run.extra_reboot)

    print(f"spike: {len(plan)} runs, window {a.window_s} s; runs already in data/runs are skipped")
    summary = run_batch(plan, REPO / "data" / "runs", capture_one)
    valid = sum(1 for s in summary if s["status"] == "valid")
    print(f"\ndone: {valid} valid, {sum(1 for s in summary if s['status'] == 'VOID')} void, "
          f"{sum(1 for s in summary if s['status'].startswith('skipped'))} skipped, "
          f"{'STOPPED early' if summary and summary[-1]['status'].startswith('STOPPED') else 'not stopped'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

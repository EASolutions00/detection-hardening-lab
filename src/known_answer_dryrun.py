"""Dry run of the known-answer cases K1 to K3 through the real pipeline, before any lab run.

    .venv/Scripts/python.exe src/known_answer_dryrun.py --summary data/summaries/known-answer-dryrun-2026-11-26.txt

Why. docs/EXPECTED-RESULTS.md states what each test case should do. This script checks
what the system will report for those expected events, so a gap in the method shows up
before hours of lab time, not in front of the panel (DECISIONS 2026-11-26).

What is real and what is made up:
- Real (read only): the spike's Config S run folders in data/runs. They give the real
  run-to-run noise: 5 control runs, 3 runs as "before", and 3 runs with no change
  (the reboot runs) as the base of "after".
- Synthetic: (1) the pinned Remote Desktop sign-in's events, added to every run, as
  measured by hand (OPEN-QUESTIONS 37, the default client: two type 3 NTLM logons with
  rule 92657, one 4648, two type 10 logons with rule 92653); (2) each case's effect,
  applied to the "after" runs: K1 removes the Logon subcategory's events (4624, 4625,
  4648, 4675) and the rules that read 4624; K2 empties CommandLine in 4688; K3 removes
  4688 and rule 67027. N applies nothing.

So this is not evidence that the system works on real data. It is a check that the
expected results and the code agree. The evidence comes from the lab runs.

Writes the synthetic run folders and the four reports into --work (a new temporary
folder by default). Nothing in data/runs is changed.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telos.harness import parameters_hash  # noqa: E402
from telos.model import Classification  # noqa: E402
from telos.pipeline import compare  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "data" / "runs"
RULES = REPO / "data" / "rules" / "wazuh-4.14.7"

CONTROL = [f"spike-S-ctl-{i}" for i in range(1, 6)]
PRE = [f"spike-S-C3-pre-{i}" for i in range(1, 4)]
AFTER_BASE = [f"spike-S-reboot-{i}" for i in range(1, 4)]

RDP_COUNTS = {
    "Security-4624[AuthenticationPackageName=NTLM,LogonType=other,TargetUserName]": 2,
    "Security-4624[AuthenticationPackageName=other,LogonType=10,TargetUserName]": 2,
    "Security-4648[]": 1,
}
RDP_FIRED = {"92657": 2, "92653": 2}

# Events of the "Logon" audit subcategory (Microsoft's audit documentation: 4624, 4625, 4648, 4675).
LOGON_EVENTS = ("Security-4624[", "Security-4625[", "Security-4648[", "Security-4675[")
# Rules whose chain starts at 60106 (event 4624), as read in the rule files.
LOGON_RULES = {"60106", "60118", "60119", "67022", "67024", "92651", "92652", "92653", "92656", "92657"}


def _real(run_id: str) -> tuple[dict, dict]:
    d = json.loads((RUNS / run_id / "counts.json").read_text(encoding="utf-8"))
    return d["counts"], d.get("fired", {})


def _add_rdp(counts: dict, fired: dict) -> tuple[dict, dict]:
    c, f = dict(counts), dict(fired)
    for k, n in RDP_COUNTS.items():
        c[k] = c.get(k, 0) + n
    for r, n in RDP_FIRED.items():
        f[r] = f.get(r, 0) + n
    return c, f


def no_change(c: dict, f: dict) -> tuple[dict, dict]:
    return dict(c), dict(f)


def k1(c: dict, f: dict) -> tuple[dict, dict]:
    """Audit Logon off: the subcategory's events and every rule that reads 4624 are gone."""
    return ({k: n for k, n in c.items() if not k.startswith(LOGON_EVENTS)},
            {r: n for r, n in f.items() if r not in LOGON_RULES})


def k2(c: dict, f: dict) -> tuple[dict, dict]:
    """Command line off: 4688 still written with CommandLine empty; rule 67027 still fires."""
    out: dict = {}
    for k, n in c.items():
        if k.startswith("Security-4688[") and "CommandLine" in k:
            head, _, tail = k.partition("[")
            k = f"{head}[{','.join(x for x in tail[:-1].split(',') if x and x != 'CommandLine')}]"
        out[k] = out.get(k, 0) + n
    return out, dict(f)


def k3(c: dict, f: dict) -> tuple[dict, dict]:
    """Audit Process Creation off: no 4688, so rule 67027 stops."""
    return ({k: n for k, n in c.items() if not k.startswith("Security-4688[")},
            {r: n for r, n in f.items() if r != "67027"})


CASES = {"N": no_change, "K1": k1, "K2": k2, "K3": k3}


def expected_lost(case: str, keys: set[str]) -> set[str]:
    """The keys each case must make LOST, by event ID and field only (docs/EXPECTED-RESULTS.md)."""
    if case == "K1":
        return {k for k in keys if k.startswith(LOGON_EVENTS)}
    if case == "K2":
        return {k for k in keys if k.startswith("Security-4688[") and "CommandLine" in k}
    if case == "K3":
        return {k for k in keys if k.startswith("Security-4688[")}
    return set()


def _write_run(folder: Path, run_id: str, phase: str, change_id: str | None, counts: dict, fired: dict) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "counts.json").write_text(json.dumps({"run_id": run_id, "counts": counts, "fired": fired}, indent=1),
                                        encoding="utf-8")
    params = {"window_s": 180, "dry_run": True}
    manifest = {"parameters": params, "parameters_sha256": parameters_hash(params),    # the pipeline recomputes it
                "record": {"run_id": run_id, "phase": phase, "change_id": change_id, "valid": True}}
    (folder / "run_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return folder


def _ratio(a: int, b: int) -> str:
    return f"{a / b:.2f}" if b else "n/a"


def run(work: Path) -> list[str]:
    lines: list[str] = []
    say = lines.append
    say("KNOWN-ANSWER DRY RUN (synthetic effects on real spike noise; see the script's docstring)")
    say(f"Real runs: control {', '.join(CONTROL)}; before {', '.join(PRE)}; base of after {', '.join(AFTER_BASE)}")
    say("")
    rows = []
    for case, effect in CASES.items():
        base = work / "runs" / case
        dirs: dict[str, list[Path]] = {"control": [], "pre": [], "post": []}
        for i, rid in enumerate(CONTROL, 1):
            dirs["control"].append(_write_run(base / f"ctl-{i}", f"dry-{case}-ctl-{i}", "control", None,
                                              *_add_rdp(*_real(rid))))
        for i, rid in enumerate(PRE, 1):
            dirs["pre"].append(_write_run(base / f"pre-{i}", f"dry-{case}-pre-{i}", "pre", None,
                                          *_add_rdp(*_real(rid))))
        for i, rid in enumerate(AFTER_BASE, 1):
            dirs["post"].append(_write_run(base / f"post-{i}", f"dry-{case}-post-{i}", "post", case,
                                           *effect(*_add_rdp(*_real(rid)))))
        out = compare(dirs["control"], dirs["pre"], dirs["post"], RULES, work / "out" / case)
        res = out.result

        before: Counter = Counter()
        after: Counter = Counter()
        for d in dirs["pre"]:
            before.update(json.loads((d / "counts.json").read_text(encoding="utf-8"))["counts"])
        for d in dirs["post"]:
            after.update(json.loads((d / "counts.json").read_text(encoding="utf-8"))["counts"])
        truth = expected_lost(case, set(before))
        found = {f.key for f in res.findings if f.classification in (Classification.LOST, Classification.REDUCED)}
        naive = {k for k in before if before[k] > after.get(k, 0)}

        say("=" * 100)
        say(f"CASE {case}   verdict: {res.outcome.value}")
        for f in res.findings:
            if f.classification in (Classification.LOST, Classification.REDUCED, Classification.NEW):
                q = f"   q = {f.q_value:.2g}" if f.q_value is not None else ""
                say(f"  {f.classification.value:13} {f.key}   {f.pre_total} -> {f.post_total}{q}")
            elif f.classification is Classification.INCONCLUSIVE and f.key in truth:
                say(f"  {f.classification.value:13} {f.key}   {f.pre_total} -> {f.post_total}   ({f.reason})")
        for lost, new, dropped in res.field_losses:
            say(f"  FIELD LOSS    {lost} -> {new}   dropped: {', '.join(dropped)}")
        for h in out.ranked:
            say(f"  RANKED        {h.key}: blind techniques {', '.join(h.blind_techniques) or '-'};"
                f" highest level {h.max_level}; rules {len(h.rules)}")
        say(f"  COVERAGE      no longer detected (alerts fired before, none after): {', '.join(out.coverage_lost) or '-'}")
        m = out.myers
        say(f"  MYERS         joined D = {m.phases.d}; control pairs D {min(m.control_pair_d)} to "
            f"{max(m.control_pair_d)}; before-after pairs D {min(m.before_after_pair_d)} to "
            f"{max(m.before_after_pair_d)}")
        tp, fp, fn = len(found & truth), len(found - truth), len(truth - found)
        ntp, nfp, nfn = len(naive & truth), len(naive - truth), len(truth - naive)
        say(f"  SCORE         expected LOST keys {len(truth)}; system TP {tp} FP {fp} FN {fn} "
            f"(precision {_ratio(tp, tp + fp)}, recall {_ratio(tp, tp + fn)}); naive subtraction TP {ntp} FP {nfp} "
            f"FN {nfn} (precision {_ratio(ntp, ntp + nfp)}, recall {_ratio(ntp, ntp + nfn)})")
        if truth - found:
            say(f"  MISSED        {', '.join(sorted(truth - found))}")
        if naive - truth:
            say(f"  NAIVE FALSE   {', '.join(sorted(naive - truth))}")
        say("")
        rows.append((case, len(truth), tp, fp, fn, ntp, nfp, nfn))

    say("=" * 100)
    say(f"{'case':5} {'expected':>8} | {'system TP':>9} {'FP':>3} {'FN':>3} | {'naive TP':>8} {'FP':>3} {'FN':>3}")
    for case, nt, tp, fp, fn, ntp, nfp, nfn in rows:
        say(f"{case:5} {nt:8} | {tp:9} {fp:3} {fn:3} | {ntp:8} {nfp:3} {nfn:3}")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--work", help="folder for the synthetic runs and reports (default: a new temporary folder)")
    ap.add_argument("--summary", help="also write the printed summary to this file")
    a = ap.parse_args()
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix="telos-dryrun-"))
    text = "\n".join(run(work)) + "\n"
    print(text, end="")
    print(f"(synthetic runs and reports in {work})")
    if a.summary:
        Path(a.summary).parent.mkdir(parents=True, exist_ok=True)
        Path(a.summary).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""How the evaluation's score depends on the test for a key that falls to zero.

    .venv/Scripts/python.exe src/zero_loss_sensitivity.py --summary data/summaries/eval-2026-11-26/zero-loss-sensitivity.txt

Why. An outside review (WORKLOG 2026-11-27, point 2) found that the declared test for a key
that falls to zero treats the before rate as known. This script asks whether the score would
change under tests that do not. The declared test stays the main result, because it was fixed
before the runs (DECISIONS 2026-11-26; OPEN-QUESTIONS 43). The other four were chosen after the
runs, so they are a check on the result, not a replacement for it.

What it does. It reads data/runs and the official output in data/summaries/eval-2026-11-26, and
writes nothing except the --summary file, if one is given.
1. For each case it loads the 5 control, 3 before and 3 after runs the way
   telos.pipeline.compare does, and runs the code's own per-key steps (_test_key, then classify,
   as analyse() does). It stops unless every key gets the same class, totals and q value as the
   official comparison.csv.
2. It then replaces only the p value of each tested key that fell to zero, and runs classify
   again. So the correction, the rule for REDUCED and the rule for a rare key stay the code's.
3. It scores each test as section 3 of docs/EXPECTED-RESULTS.md says.

The five tests, for a key with `a` events in the n1 before runs and none in the n2 after runs:
- declared: the chance of no event after if the rate stayed at the before rate,
  exp(-(a / n1) * n2 / phi), with phi from the control runs. It treats the before rate as known.
- split of events, 3 v 3: if nothing changed, each event is as likely to fall in any run, so
  the chance that all `a` events fall in the before runs is (n1 / (n1 + n2)) ** a. It does not
  assume the rate.
- split of events, 8 v 3: the same, with the 5 control runs counted as before runs.
- runs with the key, 3 v 3: counts runs, not events, so the events of one run may belong
  together. If `x` of the n1 before runs have the key and none of the n2 after runs do, the
  chance that all `x` runs with the key are before runs is C(n1, x) / C(n1 + n2, x). This is
  Fisher's exact test, one-sided.
- runs with the key, 8 v 3: the same, with the control runs counted as before runs.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))

from telos.differential import (ALPHA, MAX_RATIO, MIN_PRE_COUNT, NOISE_SIGMAS,  # noqa: E402
                                _test_key, align, classify)
from telos.model import Classification  # noqa: E402
from telos.pipeline import load_phase, load_run  # noqa: E402
from telos.variance import VarianceModel  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "data" / "runs"
OFFICIAL = REPO / "data" / "summaries" / "eval-2026-11-26"
CASES = ("C1", "C3", "C5", "K1", "K2", "K3")
SCORED = ("C1", "C5", "K1", "K2", "K3")      # C3 is not scored for recall (EXPECTED-RESULTS section 3)
CONTROL = [f"eval-ctl-{i}" for i in range(1, 6)]
PRE = [f"eval-pre-{i}" for i in range(1, 4)]
TESTS = [
    ("declared", "declared (before rate known)"),
    ("split3", "split of events, 3 v 3"),
    ("split8", "split of events, 8 v 3"),
    ("runs3", "runs with the key, 3 v 3"),
    ("runs8", "runs with the key, 8 v 3"),
]
FOUND = (Classification.LOST, Classification.REDUCED)


def p_split(events: int, base_runs: int, after_runs: int) -> float:
    """The chance that all the events fall in the base runs, if every run is equally likely."""
    return (base_runs / (base_runs + after_runs)) ** events


def p_runs(runs_with_key: int, base_runs: int, after_runs: int) -> float:
    """Fisher's exact test, one-sided, when no after run has the key. Of all C(base + after, x)
    ways to choose which x runs have the key, C(base, x) put all of them in the base runs."""
    return math.comb(base_runs, runs_with_key) / math.comb(base_runs + after_runs, runs_with_key)


def field_names(key: str) -> list[str]:
    """'Security-4688[CommandLine,NewProcessName]' gives ['CommandLine', 'NewProcessName']."""
    if "[" not in key:
        return []
    inside = key[key.index("[") + 1:key.rindex("]")]
    return [part.split("=")[0] for part in inside.split(",") if part]


def expected_lost(case: str, key: str) -> bool:
    """EXPECTED-RESULTS section 3, by event ID and field only (applied to keys seen before)."""
    event = key.split("[")[0]
    if case == "K1":
        return event in ("Security-4624", "Security-4625", "Security-4648", "Security-4675")
    if case == "K2":
        return event == "Security-4688" and "CommandLine" in field_names(key)
    if case == "K3":
        return event == "Security-4688"
    return False    # C1 and C5: none expected


def self_checks(say) -> None:
    """The formulas against values worked out by hand, and against scipy's Fisher test."""
    checks = [
        ("split, 6 events, 3 v 3: (1/2)^6", p_split(6, 3, 3), 0.015625),
        ("runs, 3 of 3 before, 0 of 3 after: 1/C(6,3) = 1/20", p_runs(3, 3, 3), 0.05),
        ("runs, 2 of 3 before, 0 of 3 after: C(3,2)/C(6,2) = 3/15", p_runs(2, 3, 3), 0.2),
        ("runs, 8 of 8 before, 0 of 3 after: 1/C(11,3) = 1/165", p_runs(8, 8, 3), 1 / 165),
    ]
    for x, base, after in ((3, 3, 3), (2, 3, 3), (8, 8, 3), (5, 8, 3)):
        fisher = float(stats.fisher_exact([[x, base - x], [0, after]], alternative="greater")[1])
        checks.append((f"runs, {x} of {base} before, 0 of {after} after: scipy's Fisher test",
                       p_runs(x, base, after), fisher))
    for name, got, want in checks:
        ok = math.isclose(got, want, rel_tol=1e-12)
        say(f"  {name}: {got:.6g}  {'ok' if ok else 'FAILED, expected ' + format(want, '.6g')}")
        if not ok:
            raise SystemExit("a self-check failed; nothing else was computed")


def load_case(case: str):
    """The case's control, before and after phases and noise model, as telos.pipeline.compare
    builds them: one key list for all three phases, the window from the first before run."""
    dirs = {"control": [RUNS / r for r in CONTROL], "pre": [RUNS / r for r in PRE],
            "post": [RUNS / f"eval-post-{case}-{i}" for i in range(1, 4)]}
    runs = {name: [load_run(d) for d in ds] for name, ds in dirs.items()}
    every = [r for rs in runs.values() for r in rs]
    if not all(r.valid for r in every):
        raise SystemExit(f"{case}: a run is not valid: {[r.run_id for r in every if not r.valid]}")
    if len({r.params_hash for r in every}) != 1:
        raise SystemExit(f"{case}: the runs do not share one parameters hash")
    if len({r.change_id for r in runs["post"]}) != 1:
        raise SystemExit(f"{case}: the after runs belong to more than one change")
    window_minutes = float(runs["pre"][0].manifest.get("parameters", {}).get("window_s", 900)) / 60.0
    keys = sorted({k for r in every for k in r.counts})
    ctl, pre, post = (load_phase(name, dirs[name], keys, window_minutes)[0] for name in ("control", "pre", "post"))
    if (ctl.n_runs, pre.n_runs, post.n_runs) != (5, 3, 3):
        raise SystemExit(f"{case}: expected 5, 3 and 3 runs")
    return ctl, pre, post, VarianceModel.from_control(ctl, min_runs=3)


def findings_under(test: str, ctl, pre, post, vm):
    """The code's per-key steps (as analyse() runs them), with the p value of each tested key that
    fell to zero replaced by the chosen test's. classify() then applies the correction and rules."""
    findings = [_test_key(k, pre, post, vm, MIN_PRE_COUNT) for k in align(pre, post)]
    n1, n2, nc = pre.n_runs, post.n_runs, ctl.n_runs
    for f in findings:
        if test == "declared" or f.p_value is None or not (f.pre_total > 0 and f.post_total == 0):
            continue
        a, c = f.pre_total, ctl.total(f.key)
        x_pre = sum(1 for v in pre.counts[f.key] if v > 0)
        x_ctl = sum(1 for v in ctl.counts[f.key] if v > 0)
        f.p_value = {"split3": p_split(a, n1, n2), "split8": p_split(a + c, n1 + nc, n2),
                     "runs3": p_runs(x_pre, n1, n2), "runs8": p_runs(x_pre + x_ctl, n1 + nc, n2)}[test]
    classify(findings, ALPHA, MAX_RATIO, NOISE_SIGMAS)
    return findings


def reproduces_official(case: str, findings) -> list[str]:
    """Keys whose class, totals or q value differ from the official comparison.csv (empty if none)."""
    with open(OFFICIAL / case / "comparison.csv", encoding="utf-8", newline="") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}
    mine = {f.key: f for f in findings}
    problems = [f"only in one of the two: {k}" for k in sorted(set(rows) ^ set(mine))]
    for k in sorted(set(rows) & set(mine)):
        r, f = rows[k], mine[k]
        q = float(r["q_value"]) if r["q_value"] else None
        same_q = (q is None) == (f.q_value is None) and (q is None or math.isclose(q, f.q_value, rel_tol=1e-9))
        if (r["classification"] != f.classification.value or int(r["pre_total"]) != f.pre_total
                or int(r["post_total"]) != f.post_total or not same_q):
            problems.append(k)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="How the score depends on the test for a key that falls to zero.")
    ap.add_argument("--summary", help="also write the output to this file")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lines: list[str] = []

    def say(text: str = "") -> None:
        print(text)
        lines.append(text)

    say("ZERO-LOSS SENSITIVITY, evaluation runs of 2026-11-26 (src/zero_loss_sensitivity.py)")
    say("Runs: eval-ctl-1 to -5 (control), eval-pre-1 to -3 (before), eval-post-<case>-1 to -3 (after).")
    say("The declared test is the main result. The other four were chosen after the runs.")
    say()
    say("SELF-CHECKS (the formulas against values worked out by hand)")
    self_checks(say)
    say()

    say("REPRODUCTION (the declared test against the official comparison.csv of each case)")
    results: dict[str, dict[str, list]] = {}
    phases = {}
    for case in CASES:
        ctl, pre, post, vm = load_case(case)
        phases[case] = (ctl, pre, post)
        results[case] = {t: findings_under(t, ctl, pre, post, vm) for t, _ in TESTS}
        problems = reproduces_official(case, results[case]["declared"])
        say(f"  {case}: {len(results[case]['declared'])} keys; class, totals and q the same for every key: "
            f"{'yes' if not problems else 'NO'}")
        if problems:
            for p in problems[:10]:
                say(f"      differs: {p}")
            raise SystemExit("the declared test does not reproduce the official output; nothing else was computed")
    say()

    say("SCORE PER TEST (keys found LOST or REDUCED per case; TP, FP, FN over C1, C5, K1, K2 and K3)")
    say(f"  {'test':<30} {'C1':>3} {'C5':>3} {'K1':>3} {'K2':>3} {'K3':>3}   {'TP':>3} {'FP':>3} {'FN':>3}   C3 (not scored)")
    for t, label in TESTS:
        tp = fp = fn = 0
        per_case = {}
        for case in CASES:
            fs = results[case][t]
            found = {f.key for f in fs if f.classification in FOUND}
            per_case[case] = len(found)
            if case in SCORED:
                expected = {f.key for f in fs if f.pre_total > 0 and expected_lost(case, f.key)}
                tp += len(found & expected)
                fp += len(found - expected)
                fn += len(expected - found)
        say(f"  {label:<30} " + " ".join(f"{per_case[c]:>3}" for c in SCORED)
            + f"   {tp:>3} {fp:>3} {fn:>3}   {per_case['C3']}")
    say()

    say("EACH TESTED KEY THAT FELL TO ZERO (p before the correction, q after it, and the class)")
    for case in CASES:
        ctl, pre, post = phases[case]
        zero = [f.key for f in results[case]["declared"]
                if f.p_value is not None and f.pre_total > 0 and f.post_total == 0]
        if not zero:
            say(f"  {case}: none")
            continue
        for key in zero:
            x_pre = sum(1 for v in pre.counts[key] if v > 0)
            x_ctl = sum(1 for v in ctl.counts[key] if v > 0)
            say(f"  {case}  {key}   expected LOST: {'yes' if expected_lost(case, key) else 'no'}")
            say(f"      before {pre.total(key)} (in {x_pre} of 3 runs), after 0, "
                f"control {ctl.total(key)} (in {x_ctl} of 5 runs)")
            for t, label in TESTS:
                f = next(f for f in results[case][t] if f.key == key)
                say(f"      {label:<30} p {f.p_value:<10.3g} q {f.q_value:<10.4g} {f.classification.value}")
    say()
    say("Everything else is the code's: the same keys, the same noise model, the same correction")
    say(f"(Benjamini-Hochberg at {ALPHA}), the same rules for REDUCED and for a rare key.")

    if a.summary:
        out = Path(a.summary)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nwritten: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

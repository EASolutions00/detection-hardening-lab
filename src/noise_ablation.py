"""What the noise part of the method adds: the same analysis with and without it (an ablation).

    .venv/Scripts/python.exe src/noise_ablation.py --summary data/summaries/eval-2026-11-26/noise-ablation.txt

Why. EXPECTED-RESULTS section 7 says the evaluation does not show what measuring the noise adds: every true loss fell
to zero, and the one false loss of plain subtraction is also removed by the rule that a loss must at least halve
(outside review, point 5). This script compares five ways of deciding that a key was lost, on three kinds of data.
It was chosen after the runs (docs/FREEZE-DATES.md section 6), so it is a check, not a result fixed in advance.

The five ways (the first three use the code's own analyse(), unchanged):
- full:            the system as it is: the noise model from the control runs (dispersion and CoV), 3 x CoV.
- no noise band:   the same, but a drop no longer has to exceed 3 x CoV (noise_sigmas = 0).
- no noise model:  plain Poisson: dispersion 1 and CoV 0 for every key, and every key is tested, also one the
                   control runs never saw. The statistics stay; the measured noise goes.
- halving rule:    no statistics: a key is lost when its total after is at most half its total before.
- subtraction:     no statistics: a key is lost when its total fell at all.

The three kinds of data:
- the 6 real cases, scored as EXPECTED-RESULTS section 3 says;
- 70 comparisons of control runs against control runs, the method of DECISIONS 2026-11-27: every pair of single runs
  (20) and every 2-against-2 split (30), with the noise model from all 5 control runs, and 20 out of sample, with the
  model from 3 runs and the other 2 compared. Nothing changed between those runs, so every finding is false;
- made-up partial losses: in the real C1 and C5 comparisons (3 before against 3 after, no key fell), one key's after
  counts are cut to 20, 40, 50 or 60 percent (rounded half up), for each key with 30 or more events before and after.
  Real noise, a made-up effect, as in src/known_answer_dryrun.py: not lab evidence. No real loss was partial, so this
  is the only place where the noise band can show what it does.

A threshold sweep follows: each of alpha, the halving ratio, the minimum count and the noise sigmas changed alone, on
the real cases and the 70 control comparisons.

It reads data/runs and the official output, and writes nothing except the --summary file. It stops unless the full
system gives the official class and q of every key in all 6 cases, and the recorded 0 false findings in the 70
control comparisons.
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telos.differential import ALPHA, MAX_RATIO, MIN_PRE_COUNT, NOISE_SIGMAS, analyse  # noqa: E402
from telos.model import Classification, Phase  # noqa: E402
from telos.pipeline import load_phase  # noqa: E402
from telos.variance import VarianceModel  # noqa: E402
from zero_loss_sensitivity import CASES, CONTROL, RUNS, SCORED, expected_lost, load_case, reproduces_official  # noqa: E402

FOUND = (Classification.LOST, Classification.REDUCED)
WAYS = ("full", "no noise band", "no noise model", "halving rule", "subtraction")
RATIOS = (0.2, 0.4, 0.5, 0.6)


class NoNoiseModel:
    """No measured noise: the Poisson dispersion 1 and a CoV of 0 for every key, and every key counts as measured."""

    def dispersion(self, key: str) -> float:
        return 1.0

    def cov(self, key: str) -> float:
        return 0.0

    def measured(self, key: str) -> bool:
        return True


def found_keys(way: str, pre: Phase, post: Phase, vm, **settings) -> set[str]:
    """The keys one way calls lost or reduced."""
    if way == "halving rule":
        return {k for k in pre.keys() | post.keys() if pre.total(k) > 0 and post.total(k) <= 0.5 * pre.total(k)}
    if way == "subtraction":
        return {k for k in pre.keys() | post.keys() if post.total(k) < pre.total(k)}
    if way == "no noise band":
        settings = {**settings, "noise_sigmas": 0.0}
    model = NoNoiseModel() if way == "no noise model" else vm
    return {f.key for f in analyse(pre, post, model, **settings).findings if f.classification in FOUND}


def null_comparisons() -> list[tuple[str, Phase, Phase, VarianceModel]]:
    """The 70 comparisons of control runs against control runs (DECISIONS 2026-11-27; COMMANDS 2.19)."""
    dirs = [RUNS / r for r in CONTROL]
    keys = sorted(load_phase("all", dirs)[0].counts)
    one = {d.name: load_phase(d.name, [d], keys)[0] for d in dirs}
    vm_all = VarianceModel.from_control(load_phase("control", dirs, keys)[0])
    out = []
    for a, b in itertools.permutations(dirs, 2):                                   # 20 pairs, both directions
        out.append((f"pair {a.name[-1]}>{b.name[-1]}", one[a.name], one[b.name], vm_all))
    for pre in itertools.combinations(dirs, 2):                                    # 30 splits, 2 against 2
        rest = [d for d in dirs if d not in pre]
        for post in itertools.combinations(rest, 2):
            out.append((f"split {''.join(d.name[-1] for d in pre)}>{''.join(d.name[-1] for d in post)}",
                        load_phase("p", list(pre), keys)[0], load_phase("q", list(post), keys)[0], vm_all))
    for model in itertools.combinations(dirs, 3):                                  # 20 out of sample
        vm = VarianceModel.from_control(load_phase("m", list(model), keys)[0])
        a, b = [d for d in dirs if d not in model]
        for pre, post in ((a, b), (b, a)):
            out.append((f"out of sample {''.join(d.name[-1] for d in model)}: {pre.name[-1]}>{post.name[-1]}",
                        one[pre.name], one[post.name], vm))
    return out


def score(found: dict[str, set[str]], cases: dict) -> tuple[int, int, int]:
    tp = fp = fn = 0
    for case in SCORED:
        _ctl, pre, _post, _vm = cases[case]
        expected = {k for k in pre.keys() if pre.total(k) > 0 and expected_lost(case, k)}
        tp += len(found[case] & expected)
        fp += len(found[case] - expected)
        fn += len(expected - found[case])
    return tp, fp, fn


def cut(post: Phase, key: str, ratio: float) -> Phase:
    """The after phase with one key's counts cut to `ratio`, rounded half up: the made-up partial loss."""
    counts = {k: list(v) for k, v in post.counts.items()}
    counts[key] = [int(c * ratio + 0.5) for c in counts[key]]
    return Phase(name=post.name, counts=counts, window_minutes=post.window_minutes)


def main() -> int:
    ap = argparse.ArgumentParser(description="What the noise part of the method adds (an ablation).")
    ap.add_argument("--summary", help="also write the output to this file")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lines: list[str] = []

    def say(text: str = "") -> None:
        print(text)
        lines.append(text)

    say("NOISE ABLATION, evaluation runs of 2026-11-26 (src/noise_ablation.py)")
    say("Chosen after the runs: a check, not a result fixed in advance. The made-up partial losses are not lab evidence.")
    say()

    cases = {case: load_case(case) for case in CASES}
    nulls = null_comparisons()

    say("SELF-CHECKS")
    for case in CASES:
        ctl, pre, post, vm = cases[case]
        problems = reproduces_official(case, analyse(pre, post, vm).findings)
        say(f"  {case}: the full system gives the official class, totals and q of every key: {'yes' if not problems else 'NO'}")
        if problems:
            raise SystemExit("the full system does not reproduce the official output; nothing else was computed")
    full_null = sum(len(found_keys("full", pre, post, vm)) for _n, pre, post, vm in nulls)
    say(f"  the 70 control comparisons: {len(nulls)} built; false findings of the full system: {full_null} "
        f"(recorded 2026-11-27: 0): {'yes' if full_null == 0 and len(nulls) == 70 else 'NO'}")
    if full_null != 0 or len(nulls) != 70:
        raise SystemExit("the control comparisons do not reproduce the recorded result; nothing else was computed")
    say()

    say("A. THE FIVE WAYS, ON THE REAL CASES AND ON THE 70 CONTROL COMPARISONS")
    say(f"  {'way':<16} {'TP':>3} {'FP':>3} {'FN':>3}  {'C3 found':>8}   {'control comparisons: false findings':>36}  {'with any':>8}")
    for way in WAYS:
        found = {case: found_keys(way, pre, post, vm) for case, (_c, pre, post, vm) in cases.items()}
        tp, fp, fn = score(found, cases)
        per = [len(found_keys(way, pre, post, vm)) for _n, pre, post, vm in nulls]
        say(f"  {way:<16} {tp:>3} {fp:>3} {fn:>3}  {len(found['C3']):>8}   {sum(per):>36}  {sum(1 for n in per if n):>5} of 70")
    say()
    say("  The control comparisons by design (false findings: pairs of single runs / 2 against 2 / out of sample):")
    groups = (("pair", 20), ("split", 30), ("out of sample", 20))
    for way in WAYS:
        parts = []
        for prefix, n in groups:
            parts.append(str(sum(len(found_keys(way, pre, post, vm)) for name, pre, post, vm in nulls
                                 if name.startswith(prefix))))
        say(f"  {way:<16} {' / '.join(parts)}")
    say("  The false findings of the no-noise-model way (comparison, key, class, totals before and after; the full")
    say("  system's dispersion for the key, from the control runs):")
    for name, pre, post, vm in nulls:
        for f in analyse(pre, post, NoNoiseModel()).findings:
            if f.classification in FOUND:
                say(f"    {name:<14} {f.key[:58]:<58} {f.classification.value:<8} {f.pre_total} -> {f.post_total}  "
                    f"dispersion {vm.dispersion(f.key):.2f}")
    say()

    say("B. MADE-UP PARTIAL LOSSES (real noise, a made-up cut; not lab evidence)")
    say("  In the real C1 and C5 comparisons, one key's after counts cut to the ratio shown, for each key with 30 or")
    say("  more events before and after. found = the cut key is LOST or REDUCED; others = other keys found, in total.")
    targets = []
    for case in ("C1", "C5"):
        _ctl, pre, post, vm = cases[case]
        for k in sorted(pre.keys()):
            if pre.total(k) >= 30 and post.total(k) >= 30:
                targets.append((case, k))
    say(f"  keys cut: {len(targets)} ({sum(1 for c, _ in targets if c == 'C1')} in C1, "
        f"{sum(1 for c, _ in targets if c == 'C5')} in C5)")
    say(f"  {'way':<16} " + "  ".join(f"{'ratio ' + str(r):>18}" for r in RATIOS))
    for way in WAYS:
        cells = []
        for r in RATIOS:
            hit = others = 0
            for case, k in targets:
                _ctl, pre, post, vm = cases[case]
                f = found_keys(way, pre, cut(post, k, r), vm)
                hit += k in f
                others += len(f - {k})
            cells.append(f"{hit:>2} of {len(targets)}, others {others:<3}")
        say(f"  {way:<16} " + "  ".join(f"{c:>18}" for c in cells))
    say("  The cut keys the full system misses at ratio 0.4 and 0.2, and why (its own reason):")
    for case, k in targets:
        _ctl, pre, post, vm = cases[case]
        for r in (0.4, 0.2):
            f = next(x for x in analyse(pre, cut(post, k, r), vm).findings if x.key == k)
            if f.classification not in FOUND:
                say(f"    {case} ratio {r}: {k[:60]:<60} {f.reason}")
    say()

    say("C. THRESHOLD SWEEP (the full system, one setting changed at a time)")
    say(f"  defaults: alpha {ALPHA}, halving ratio {MAX_RATIO}, minimum count {MIN_PRE_COUNT}, noise sigmas {NOISE_SIGMAS}")
    say(f"  {'setting':<24} {'TP':>3} {'FP':>3} {'FN':>3}  {'C3 found':>8}  {'control comparisons: false findings':>36}")
    sweep = [({}, "defaults"), ({"alpha": 0.01}, "alpha 0.01"), ({"alpha": 0.10}, "alpha 0.10"),
             ({"max_ratio": 0.3}, "halving ratio 0.3"), ({"max_ratio": 0.7}, "halving ratio 0.7"),
             ({"min_pre_count": 10}, "minimum count 10"), ({"min_pre_count": 60}, "minimum count 60"),
             ({"noise_sigmas": 2.0}, "noise sigmas 2"), ({"noise_sigmas": 4.0}, "noise sigmas 4")]
    for settings, label in sweep:
        found = {case: found_keys("full", pre, post, vm, **settings) for case, (_c, pre, post, vm) in cases.items()}
        tp, fp, fn = score(found, cases)
        nf = sum(len(found_keys("full", pre, post, vm, **settings)) for _n, pre, post, vm in nulls)
        say(f"  {label:<24} {tp:>3} {fp:>3} {fn:>3}  {len(found['C3']):>8}  {nf:>36}")
    say()
    say("Everything in A and C uses the code's own analyse() and the same runs as the official comparisons.")

    if a.summary:
        out = Path(a.summary)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nwritten: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

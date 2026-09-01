"""Render results as text.

Plain text on purpose. The web interface comes later; the analysis has to be
readable and checkable before anything is put in a browser.
"""

from __future__ import annotations

from .baseline import BaselineFinding
from .model import AnalysisResult, Classification
from .variance import VarianceModel

LINE = "=" * 78
THIN = "-" * 78


def render_variance(vm: VarianceModel, show: int = 6) -> str:
    s = vm.summary()
    out = [LINE, "NOISE FLOOR  (measured from the control runs)", LINE, ""]
    out.append(
        f"  event types measured        {int(s['n_keys'])}\n"
        f"  median CoV                  {s['median_cov']:.2%}\n"
        f"  highest CoV                 {s['max_cov']:.2%}\n"
        f"  median dispersion           {s['median_dispersion']:.2f}\n"
        f"  share of types over 5% CoV  {s['share_cov_over_5pct']:.0%}"
    )
    out.append("")
    out.append("  This is the answer to the feasibility spike's question Q1.")
    out.append("  A median CoV near zero would mean the statistical layer buys")
    out.append("  nothing inside the laboratory, and the study must say so.")
    out.append("")
    out.append(f"  {'event type':<34} {'mean':>9} {'CoV':>8} {'dispersion':>11}")
    out.append(f"  {'-'*34} {'-'*9} {'-'*8} {'-'*11}")
    stats = sorted(vm._stats.values(), key=lambda k: -k.cov)[:show]
    for k in stats:
        out.append(f"  {k.key:<34} {k.mean:>9.1f} {k.cov:>7.2%} {k.dispersion:>11.2f}")
    out.append("")
    return "\n".join(out)


def render_analysis(result: AnalysisResult) -> str:
    out = [LINE, "DIFFERENTIAL ANALYSIS", LINE, ""]

    out.append("STAGE B  global gate (one chi-square over the whole profile)")
    verdict = "PASSED" if result.gate_passed else "NOT PASSED"
    out.append(f"  chi-square = {result.gate_statistic:,.1f}   p = {result.gate_p_value:.3g}   {verdict}")
    if not result.gate_passed:
        out.append("")
        out.append("  The emitted profile did not change detectably.")
        out.append("  Recorded as 'coverage survived this change', not discarded.")
        return "\n".join(out)
    out.append(f"  event types carried into per-type testing: {result.n_tested}")
    out.append("")

    out.append("STAGE C  classification")
    counts = {c: len(result.by_class(c)) for c in Classification}
    for c in (Classification.LOST, Classification.REDUCED, Classification.NEW,
              Classification.INCONCLUSIVE, Classification.UNCHANGED):
        out.append(f"  {c.value:<14} {counts[c]:>4}")
    out.append("")

    hits = result.reported()
    out.append(f"REPORTED FINDINGS  ({len(hits)})")
    out.append("")
    if not hits:
        out.append("  none")
    for i, f in enumerate(hits, 1):
        rr = "0.000" if f.rate_ratio == 0 else f"{f.rate_ratio:.3f}"
        out.append(f"  FINDING {i}   {f.classification.value}   {f.key}")
        out.append(f"    rate before   {f.pre_rate:,.1f} per window")
        out.append(f"    rate after    {f.post_rate:,.1f} per window")
        out.append(f"    rate ratio    {rr}"
                   + (f"   95% CI [{f.ci_low:.3f}, {f.ci_high:.3f}]"
                      if f.ci_low is not None and f.ci_high is not None else ""))
        out.append(f"    q value       {f.q_value:.3g}   (BH corrected)")
        out.append(f"    noise floor   {f.cov:.2%} CoV, dispersion {f.dispersion:.2f}")
        out.append(f"    why           {f.reason}")
        out.append("")

    incon = result.by_class(Classification.INCONCLUSIVE)
    if incon:
        out.append(f"NOT TESTED, REPORTED AS INCONCLUSIVE  ({len(incon)})")
        out.append("  These are not cleared. There was not enough data to test them.")
        for f in incon:
            out.append(f"    {f.key:<34} {f.pre_total} occurrences before the change")
        out.append("")
    return "\n".join(out)


def render_comparison(result: AnalysisResult, naive: list[BaselineFinding],
                      truth: set[str]) -> str:
    """The head-to-head against the naive baseline. This is the study's result."""
    proposed = {f.key for f in result.reported()}
    naive_keys = {f.key for f in naive}

    def score(reported: set[str]) -> tuple[int, int, int, float, float, float]:
        tp = len(reported & truth)
        fp = len(reported - truth)
        fn = len(truth - reported)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        return tp, fp, fn, prec, rec, f1

    out = [LINE, "STAGE D  proposed method versus naive differencing", LINE, ""]
    out.append(f"  ground truth (keys the change really removed or reduced): {len(truth)}")
    out.append("")
    out.append(f"  {'method':<26} {'TP':>4} {'FP':>4} {'FN':>4} {'precision':>10} {'recall':>8} {'F1':>7}")
    out.append(f"  {'-'*26} {'-'*4} {'-'*4} {'-'*4} {'-'*10} {'-'*8} {'-'*7}")
    for name, keys in (("naive differencing", naive_keys), ("proposed system", proposed)):
        tp, fp, fn, p, r, f1 = score(keys)
        out.append(f"  {name:<26} {tp:>4} {fp:>4} {fn:>4} {p:>9.1%} {r:>7.1%} {f1:>7.3f}")
    out.append("")

    false_alarms = naive_keys - truth
    if false_alarms:
        out.append(f"  false alarms raised by the naive method only ({len(false_alarms)}):")
        for k in sorted(false_alarms):
            nf = next(f for f in naive if f.key == k)
            out.append(f"    {k:<34} fell {nf.drop:.2%}, which is inside its own noise")
        out.append("")
        out.append("  Each of these is an event type that moved on its own. An engineer")
        out.append("  using subtraction would investigate every one of them.")
    else:
        out.append("  The naive method raised no false alarms on this data.")
        out.append("  If that holds across all changes, the study reports it plainly:")
        out.append("  the statistical layer is justified for production, not for the lab.")
    out.append("")
    return "\n".join(out)

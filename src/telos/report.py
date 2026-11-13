"""Render results as text.

Plain text on purpose. The analysis has to be readable and checkable on its
own before any other presentation layer is considered.
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping

from .baseline import BaselineFinding
from .impact import ImpactFinding
from .index import RuleIndex
from .model import AnalysisResult, Classification, ProfileOutcome
from .variance import VarianceModel

LINE = "=" * 78
THIN = "-" * 78


def render_variance(vm: VarianceModel, show: int = 6) -> str:
    s = vm.summary()
    out = [LINE, "NOISE FLOOR  (measured from the control runs)", LINE, ""]
    out.append(
        f"  event keys measured         {int(s['n_keys'])}\n"
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
    out.append(f"  {'event key':<34} {'mean':>9} {'CoV':>8} {'dispersion':>11}")
    out.append(f"  {'-'*34} {'-'*9} {'-'*8} {'-'*11}")
    stats = sorted(vm._stats.values(), key=lambda k: -k.cov)[:show]
    for k in stats:
        out.append(f"  {k.key:<34} {k.mean:>9.1f} {k.cov:>7.2%} {k.dispersion:>11.2f}")
    out.append("")
    return "\n".join(out)


def render_analysis(result: AnalysisResult) -> str:
    out = [LINE, "DIFFERENTIAL ANALYSIS", LINE, ""]

    out.append("STAGE B  capture check, then one chi-square over the whole profile")
    out.append("         (reported as a summary; since 2026-09-28 it does not stop any key being tested)")
    if result.gate_p_value is not None and result.gate_statistic is not None:
        out.append(f"  chi-square = {result.gate_statistic:,.1f}   p = {result.gate_p_value:.3g}"
                   f"   alpha = {result.alpha}")
    out.append(f"  profile outcome   {result.outcome.value}")
    out.append(f"  why               {result.outcome_reason}")

    if result.outcome is ProfileOutcome.NOT_TESTABLE:
        out.append("")
        out.append("  THIS RUN COULD NOT BE TESTED.")
        out.append("  It is not evidence that coverage survived the change, and it is not")
        out.append("  evidence of a blind spot. Investigate the capture before re-running.")
        return "\n".join(out)

    out.append(f"  event keys carried into per-key testing: {result.n_tested}")
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
        out.append(f"    rate before   {f.pre_rate:,.1f} per run")
        out.append(f"    rate after    {f.post_rate:,.1f} per run")
        out.append(f"    rate ratio    {rr}"
                   + (f"   95% CI [{f.ci_low:.3f}, {f.ci_high:.3f}]"
                      if f.ci_low is not None and f.ci_high is not None else ""))
        out.append(f"    q value       {f.q_value:.3g}   (BH corrected)")
        out.append(f"    noise floor   {f.cov:.2%} CoV, dispersion {f.dispersion:.2f}")
        out.append(f"    why           {f.reason}")
        out.append("")

    if result.field_losses:
        out.append(f"FIELD-LEVEL LOSS  ({len(result.field_losses)})")
        out.append("  The event is still written, but a field inside it is now empty, so any")
        out.append("  detection rule matching on that field is blind.")
        out.append("")
        for lost_key, new_key, dropped in result.field_losses:
            out.append(f"  was  {lost_key}")
            out.append(f"  now  {new_key}")
            out.append(f"  lost field(s): {', '.join(dropped)}")
            out.append("")

    incon = result.by_class(Classification.INCONCLUSIVE)
    if incon:
        out.append(f"NOT TESTED, REPORTED AS INCONCLUSIVE  ({len(incon)})")
        out.append("  These are not cleared. There was not enough data to test them.")
        for f in incon:
            out.append(f"    {f.key:<34} {f.pre_total} occurrences before the change")
        out.append("")
    return "\n".join(out)


PREVENTION_NOTE = ("A blind technique can also mean the change stopped the attack itself (prevention, as\n"
                   "  ruled for C3 and C5); the per-run check must tell the two apart (OPEN-QUESTIONS 22).")


def render_verdict(result: AnalysisResult, ranked: list[ImpactFinding]) -> str:
    """FINAL's first section: no blind spot, blind spots with count and the top one, or not testable."""
    out = [LINE, "VERDICT", LINE, ""]
    if result.outcome is ProfileOutcome.NOT_TESTABLE:
        out.append("  NOT TESTABLE: the capture did not record enough to compare.")
        out.append(f"  why: {result.outcome_reason}")
        return "\n".join(out) + "\n"
    blind = [h for h in ranked if h.blind_techniques]
    if not blind:
        out.append("  NO BLIND SPOT FOUND")
        out.append(f"  {len(ranked)} lost or reduced key(s); none left an ATT&CK technique with no alert firing after")
        out.append("  the change.")
    else:
        top = blind[0]
        out.append(f"  BLIND SPOTS FOUND: {len(blind)}")
        out.append(f"  top: {top.key}")
        out.append(f"       blind techniques {len(top.blind_techniques)}   highest level {top.max_level}"
                   f"   rules {len(top.rules)}")
        out.append("")
        out.append("  " + PREVENTION_NOTE)
    return "\n".join(out) + "\n"


def render_impact(ranked: list[ImpactFinding]) -> str:
    """FINAL's third section, with remediation level 1 under each finding.

    Ranked by blind techniques, highest level, number of rules (DECISIONS 2026-11-13).
    Remediation level 1 (FINAL Module 5): rules that read events still observed after
    the change and cover the blind technique, but did not fire.
    """
    out = [LINE, "RANKED BLIND SPOTS  (blind techniques, then highest level, then number of rules)", LINE, ""]
    if not ranked:
        out.append("  no lost or reduced key")
    for i, h in enumerate(ranked, 1):
        out.append(f"  {i}. {h.classification.value:<8} {h.key}")
        out.append(f"     blind techniques {len(h.blind_techniques)}   highest level {h.max_level}   rules {len(h.rules)}")
        if not h.rules:
            out.append("     no alerting rule reads this key: it affects no detection")
            out.append("")
            continue
        out.append(f"     rules that read it: {', '.join(h.rules)}")
        out.append(f"     techniques: {', '.join(h.techniques) or '(none named in the rules)'}")
        if h.blind_techniques:
            out.append(f"     BLIND (no alert for it fired after the change): {', '.join(h.blind_techniques)}")
        for t, rules in h.surviving.items():
            out.append(f"     still detected: {t} by {', '.join(rules)}")
        for t, rules in h.could_fire.items():
            out.append(f"     remediation (level 1) for {t}: rules that read still-observed events but did not")
            out.append(f"       fire: {', '.join(rules)}")
        out.append("")
    return "\n".join(out)


def coverage_change(fired_before: Mapping[str, int], fired_after: Mapping[str, int],
                    index: RuleIndex) -> tuple[set[str], set[str], list[str]]:
    """Techniques whose alerts fired before, after, and the ones that stopped firing."""
    def techniques(fired: Mapping[str, int]) -> set[str]:
        out: set[str] = set()
        for rid, n in fired.items():
            rule = index.raw(rid)
            if n > 0 and rule is not None and rule.level >= 1:
                out |= set(rule.mitre)
        return out
    before, after = techniques(fired_before), techniques(fired_after)
    return before, after, sorted(before - after)


def render_coverage(before: set[str], after: set[str], lost: list[str]) -> str:
    """FINAL's fourth section: techniques covered by an alert that fired, before and after."""
    out = [LINE, "COVERAGE CHANGE  (techniques with at least one alert that fired)", LINE, ""]
    out.append(f"  before the change   {len(before)}: {', '.join(sorted(before)) or '-'}")
    out.append(f"  after the change    {len(after)}: {', '.join(sorted(after)) or '-'}")
    out.append(f"  no longer detected  {len(lost)}: {', '.join(lost) or '-'}")
    out.append("")
    return "\n".join(out)


def findings_json(result: AnalysisResult, ranked: list[ImpactFinding],
                  lost_techniques: list[str] | None = None) -> str:
    """The findings as JSON, for a ticketing system (FINAL, Exports)."""
    data = {
        "outcome": result.outcome.value,
        "outcome_reason": result.outcome_reason,
        "ranked": [{
            "rank": i,
            "key": h.key,
            "classification": h.classification.value,
            "blind_techniques": h.blind_techniques,
            "highest_level": h.max_level,
            "rules": h.rules,
            "techniques": h.techniques,
            "still_detected_by": h.surviving,
            "remediation_level_1": h.could_fire,
        } for i, h in enumerate(ranked, 1)],
        "coverage_lost": list(lost_techniques or []),
    }
    return json.dumps(data, indent=2)


CSV_COLUMNS = ["key", "classification", "pre_total", "post_total", "pre_rate", "post_rate",
               "rate_ratio", "ci_low", "ci_high", "q_value", "cov", "dispersion", "reason"]


def comparison_csv(result: AnalysisResult) -> str:
    """One row per event key: the telemetry comparison (FINAL, Exports). Blank = not computed."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(CSV_COLUMNS)
    for f in result.findings:
        row = []
        for col in CSV_COLUMNS:
            v = getattr(f, col)
            if col == "classification":
                v = v.value
            row.append("" if v is None else v)
        w.writerow(row)
    return buf.getvalue()


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
        out.append("  Each of these is an event key that moved on its own. An engineer")
        out.append("  using subtraction would investigate every one of them.")
    else:
        out.append("  The naive method raised no false alarms on this data.")
        out.append("  If that holds across all changes, the study reports it plainly:")
        out.append("  the statistical layer is justified for production, not for the lab.")
    out.append("")
    return "\n".join(out)

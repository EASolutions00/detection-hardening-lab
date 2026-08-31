"""Differential analysis: decide which event types the change actually removed.

Runs in four ordered stages.

1. Align
   Take the union of event-type keys across both phases and insert explicit
   zeros where a key appears in only one. A key that vanished entirely must
   survive into the comparison, so it cannot simply be dropped.

2. Global gate
   One chi-square test of homogeneity on the whole 2-by-K profile. It answers a
   single question nothing else answers: did the emitted profile change at all?

   The test is applied once, to the whole profile, not once per event type.
   Applied per key it fails twice. Expected counts for rare security events fall
   below the value at which the chi-square approximation stays valid, and the
   resulting p value merely duplicates what the rate-ratio test already gives
   for that same key.

3. Per-key rate ratio
   For every key, how much did the rate change, and is that more than this
   laboratory's measured noise? Uses the dispersion from the control runs rather
   than assuming Poisson equidispersion.

4. Multiple-comparison correction
   Several hundred keys are tested at once, so some will look unusual by chance
   alone. Benjamini-Hochberg holds the expected share of false findings to alpha.

A key is only reported as REDUCED when three conditions hold together: the
corrected q value, the effect size, and the measured noise floor. Any one alone
is not enough.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

from .model import AnalysisResult, Classification, Finding, Phase
from .variance import VarianceModel

# Defaults. All are configurable parameters of the method, not constants of it.
ALPHA = 0.05          # false discovery rate
MAX_RATIO = 0.5       # a drop must at least halve the rate to count as REDUCED
MIN_PRE_COUNT = 30    # below this, the test has no power. Reported INCONCLUSIVE.
NOISE_SIGMAS = 3.0    # the drop must exceed this many CoV of the key's own noise


def align(pre: Phase, post: Phase) -> list[str]:
    """Union of keys across both phases, sorted for stable output."""
    return sorted(pre.keys() | post.keys())


def global_gate(pre: Phase, post: Phase, keys: list[str]) -> tuple[bool, float, float]:
    """One chi-square test of homogeneity over the whole profile.

    Returns (passed, p_value, statistic). Columns where both phases are zero
    carry no information and are dropped, because a zero column makes the
    expected-count calculation undefined.

    Degenerate tables are handled before the test rather than allowed to raise.
    A phase that emitted nothing at all is a real outcome: the agent may have
    died, or logging may have stopped completely. That is not a chi-square
    question, and it must not crash the run.
    """
    rows = []
    for k in keys:
        a, b = pre.total(k), post.total(k)
        if a + b > 0:
            rows.append((a, b))

    if len(rows) < 2:
        # Fewer than two informative event types. Nothing to compare.
        return False, 1.0, 0.0

    table = np.array(rows, dtype=float).T  # shape (2, K)
    pre_total, post_total = float(table[0].sum()), float(table[1].sum())

    # One phase emitted nothing. The profile certainly changed, but a chi-square
    # cannot express it, because an all-zero row makes every expected frequency
    # in that row zero.
    if pre_total == 0 and post_total == 0:
        return False, 1.0, 0.0
    if pre_total == 0 or post_total == 0:
        return True, 0.0, float("inf")

    try:
        chi2, p, _dof, _expected = stats.chi2_contingency(table)
    except ValueError:
        # A zero expected frequency survived the checks above. Rather than
        # guessing, decline the gate and let the run be recorded as
        # inconclusive at the profile level.
        return False, 1.0, 0.0
    return bool(p < ALPHA), float(p), float(chi2)


def _test_key(
    key: str,
    pre: Phase,
    post: Phase,
    vm: VarianceModel,
    min_pre_count: int,
) -> Finding:
    """Rate ratio and p value for one key, before correction.

    The classification set here is provisional. REDUCED versus UNCHANGED is
    decided in classify(), after the q values exist.
    """
    a = pre.total(key)          # total occurrences before, across n1 runs
    b = post.total(key)         # total occurrences after, across n2 runs
    n1, n2 = pre.n_runs, post.n_runs

    rate_pre = a / n1 if n1 else 0.0
    rate_post = b / n2 if n2 else 0.0
    phi = vm.dispersion(key)
    cov = vm.cov(key)

    f = Finding(
        key=key,
        classification=Classification.UNCHANGED,
        pre_total=a,
        post_total=b,
        pre_rate=rate_pre,
        post_rate=rate_post,
        cov=cov,
        dispersion=phi,
    )

    # Appeared only after the change. Not a loss, so it is not tested.
    if a == 0 and b > 0:
        f.classification = Classification.NEW
        f.reason = "absent before the change, present after"
        return f

    # Too rare to test. Reported honestly rather than folded into UNCHANGED.
    if a < min_pre_count:
        f.classification = Classification.INCONCLUSIVE
        f.reason = (
            f"only {a} occurrences before the change, below the minimum of "
            f"{min_pre_count} needed for the test to have power"
        )
        return f

    if b == 0:
        # Complete loss. The log rate ratio is undefined, so use the exact
        # Poisson probability of observing zero when the pre-change rate said we
        # should have seen lambda. Dividing by the dispersion keeps the test
        # conservative under overdispersion.
        lam = rate_pre * n2
        lam_eff = lam / phi
        f.rate_ratio = 0.0
        f.ci_low = 0.0
        # Rule of three: with zero observed, the 95% upper bound on the rate is
        # about 3 / exposure. Expressed here as a ratio to the pre-change rate.
        f.ci_high = (3.0 * phi / n2) / rate_pre if rate_pre > 0 else None
        f.p_value = float(math.exp(-lam_eff)) if lam_eff < 700 else 0.0
        f.classification = Classification.LOST
        f.reason = f"present before ({a} occurrences), absent after"
        return f

    # Both phases non-zero: quasi-Poisson rate ratio.
    #   RR              = rate_post / rate_pre
    #   Var(log RR)     = phi * (1/a + 1/b)
    # The dispersion phi widens the interval to match the variance actually
    # measured in the control runs. Under Poisson, phi is 1 and this reduces to
    # the standard result.
    rr = rate_post / rate_pre
    var_log = phi * (1.0 / a + 1.0 / b)
    se = math.sqrt(var_log)
    log_rr = math.log(rr)

    z = log_rr / se if se > 0 else 0.0
    p = float(2.0 * stats.norm.sf(abs(z)))

    f.rate_ratio = rr
    f.ci_low = math.exp(log_rr - 1.96 * se)
    f.ci_high = math.exp(log_rr + 1.96 * se)
    f.p_value = p
    return f


def classify(
    findings: list[Finding],
    alpha: float,
    max_ratio: float,
    noise_sigmas: float,
) -> None:
    """Apply BH correction, then settle REDUCED versus UNCHANGED in place.

    Three conditions must hold together for REDUCED:
      1. statistical:  corrected q value at or below alpha
      2. effect size:  the rate ratio at or below max_ratio
      3. noise floor:  the observed drop exceeds noise_sigmas times the key's
                       own coefficient of variation, measured from control runs

    Requiring all three is the point of the method. A p value alone will flag
    keys whose ordinary swing is larger than the drop being reported.
    """
    tested = [f for f in findings if f.p_value is not None]
    if not tested:
        return

    ps = np.array([f.p_value for f in tested], dtype=float)
    qs = stats.false_discovery_control(ps, method="bh")
    for f, q in zip(tested, qs):
        f.q_value = float(q)

    for f in tested:
        if f.classification is Classification.LOST:
            # A complete loss still has to clear the correction.
            if f.q_value is not None and f.q_value > alpha:
                f.classification = Classification.UNCHANGED
                f.reason = (
                    f"absent after the change, but q={f.q_value:.3g} did not survive "
                    f"correction at alpha={alpha}"
                )
            continue

        if f.rate_ratio is None:
            continue

        drop = 1.0 - f.rate_ratio            # 0.30 means a 30 percent fall
        band = noise_sigmas * (f.cov or 0.0)  # this key's own natural swing

        stat_ok = f.q_value is not None and f.q_value <= alpha
        size_ok = f.rate_ratio <= max_ratio
        noise_ok = drop > band

        if stat_ok and size_ok and noise_ok:
            f.classification = Classification.REDUCED
            f.reason = (
                f"rate fell to {f.rate_ratio:.3f} of baseline "
                f"(q={f.q_value:.3g}, drop {drop:.1%} exceeds noise band {band:.1%})"
            )
        else:
            failed = []
            if not stat_ok:
                failed.append(f"q={f.q_value:.3g} above alpha={alpha}")
            if not size_ok:
                failed.append(f"ratio {f.rate_ratio:.3f} above {max_ratio}")
            if not noise_ok:
                failed.append(f"drop {drop:.1%} within noise band {band:.1%}")
            f.classification = Classification.UNCHANGED
            f.reason = "not reported: " + "; ".join(failed)


def analyse(
    pre: Phase,
    post: Phase,
    vm: VarianceModel,
    alpha: float = ALPHA,
    max_ratio: float = MAX_RATIO,
    min_pre_count: int = MIN_PRE_COUNT,
    noise_sigmas: float = NOISE_SIGMAS,
) -> AnalysisResult:
    """Run the whole comparison for one hardening change."""
    pre.validate()
    post.validate()
    if pre.n_runs != post.n_runs:
        raise ValueError(
            f"phases have different repetition counts ({pre.n_runs} vs {post.n_runs}). "
            "The manifest must fix this before the runs are comparable."
        )
    if abs(pre.window_minutes - post.window_minutes) > 1e-9:
        raise ValueError(
            f"phases have different window lengths ({pre.window_minutes} vs "
            f"{post.window_minutes} minutes). Rates are not comparable."
        )

    keys = align(pre, post)
    passed, gate_p, gate_stat = global_gate(pre, post, keys)

    result = AnalysisResult(
        gate_passed=passed, gate_p_value=gate_p, gate_statistic=gate_stat, alpha=alpha
    )

    if not passed:
        # Recorded, not discarded. Evidence that a change was safe is useful.
        return result

    findings = [_test_key(k, pre, post, vm, min_pre_count) for k in keys]
    classify(findings, alpha, max_ratio, noise_sigmas)

    result.findings = findings
    result.n_tested = sum(1 for f in findings if f.p_value is not None)
    return result

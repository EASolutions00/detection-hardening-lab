"""Differential analysis: decide which event keys the change actually removed.

Runs in four ordered stages.

1. Align
   Take the union of event keys across both phases and insert explicit zeros
   where a key appears in only one. A key that vanished entirely must survive
   into the comparison, so it cannot simply be dropped.

2. Global gate
   First, check the capture itself. A repetition that recorded no events at all
   is a failed capture, and the run is NOT_TESTABLE. Then one chi-square test of
   homogeneity on the whole 2-by-K profile. It answers a single question nothing
   else answers: did the emitted profile change at all?

   The test is applied once, to the whole profile, not once per key.
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
from dataclasses import dataclass

import numpy as np
from scipy import stats

from .model import AnalysisResult, Classification, Finding, Phase, ProfileOutcome
from .variance import VarianceModel

# Defaults. All are configurable parameters of the method, not constants of it.
ALPHA = 0.05          # false discovery rate
MAX_RATIO = 0.5       # a drop must at least halve the rate to count as REDUCED
MIN_PRE_COUNT = 30    # below this, the test has no power. Reported INCONCLUSIVE.
NOISE_SIGMAS = 3.0    # the drop must exceed this many CoV of the key's own noise


def align(pre: Phase, post: Phase) -> list[str]:
    """Union of keys across both phases, sorted for stable output."""
    return sorted(pre.keys() | post.keys())


@dataclass(frozen=True)
class GateResult:
    """What the global gate concluded.

    outcome is None only when the gate does not apply: exactly one event key
    carries events, so there is no profile shape to test. analyse() then tests
    that key directly instead of declaring "no change".
    """

    outcome: ProfileOutcome | None
    p_value: float | None
    statistic: float | None
    reason: str


def capture_problem(pre: Phase, post: Phase) -> str | None:
    """Why this pair of phases cannot be tested, or None if it can.

    A repetition that recorded no events at all is a failed capture. A real
    capture window always contains events, if only the two fence markers the
    harness fires to open and close it. So an all-zero repetition means the
    agent died, the pipeline stopped, or the export failed.

    That must not reach the statistics. Before 2026-09-14 an all-zero
    post-change phase passed the gate with p = 0 and every key with enough
    events before was reported LOST: a dead agent became a list of blind spots.
    An all-zero pre-change phase made every key NEW.

    This catches a repetition that recorded nothing. It does not catch a
    capture that died partway through a window. That needs the harness to
    confirm the end fence arrived, which is recorded against OPEN-QUESTIONS 22.
    """
    for phase in (pre, post):
        for i, total in enumerate(phase.run_totals(), start=1):
            if total == 0:
                return (
                    f"{phase.name} repetition {i} of {phase.n_runs} recorded no events "
                    f"at all. A capture that recorded nothing cannot be told apart "
                    f"from a dead agent or a stopped pipeline"
                )
    return None


def global_gate(pre: Phase, post: Phase, keys: list[str],
                alpha: float = ALPHA) -> GateResult:
    """Check the capture, then one chi-square test of homogeneity over the profile.

    Keys where both phases are zero carry no information and are dropped,
    because a zero column makes the expected-count calculation undefined.

    alpha is the threshold the gate compares against. Before 2026-09-14 the gate
    took no alpha and always used the module default, so analyse(alpha=0.01)
    moved every per-key test and silently left the gate at 0.05. See
    OPEN-QUESTIONS 23.
    """
    problem = capture_problem(pre, post)
    if problem:
        return GateResult(ProfileOutcome.NOT_TESTABLE, None, None, problem)

    rows = []
    for k in keys:
        a, b = pre.total(k), post.total(k)
        if a + b > 0:
            rows.append((a, b))

    # capture_problem() guarantees both phases carry events, so at least one key
    # does. Exactly one means there is no profile shape to compare, and a 2-by-1
    # table has zero degrees of freedom. That is not "no change". The key is
    # tested directly instead. Before 2026-09-14 this returned "not passed", so
    # a profile whose only key fell from 1,000 to 400 was reported as
    # "no significant change".
    if len(rows) < 2:
        return GateResult(
            None, None, None,
            "only one event key carries events, so the profile-level test does "
            "not apply and the key was tested directly",
        )

    # Every row total and every column total is now above zero, so every
    # expected frequency is above zero, and chi2_contingency cannot raise on a
    # zero expected count. An earlier try/except for that case was unreachable
    # and was removed on 2026-09-14 rather than left to suggest otherwise.
    table = np.array(rows, dtype=float).T  # shape (2, K)
    chi2, p, _dof, _expected = stats.chi2_contingency(table)

    if p < alpha:
        return GateResult(ProfileOutcome.CHANGED, float(p), float(chi2),
                          f"chi-square p = {p:.3g} is below alpha = {alpha}")
    return GateResult(ProfileOutcome.UNCHANGED, float(p), float(chi2),
                      f"chi-square p = {p:.3g} is not below alpha = {alpha}")


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
    gate = global_gate(pre, post, keys, alpha)

    if gate.outcome in (ProfileOutcome.NOT_TESTABLE, ProfileOutcome.UNCHANGED):
        # Recorded, not discarded. NOT_TESTABLE says the capture must be
        # investigated. UNCHANGED says no change was detected, which is a
        # narrower claim than "the change was safe": it rests on the stimulus
        # having run the same way in both phases, which OPEN-QUESTIONS 22 says
        # is not yet verified.
        return AnalysisResult(
            outcome=gate.outcome, outcome_reason=gate.reason,
            gate_p_value=gate.p_value, gate_statistic=gate.statistic, alpha=alpha,
        )

    findings = [_test_key(k, pre, post, vm, min_pre_count) for k in keys]
    classify(findings, alpha, max_ratio, noise_sigmas)
    n_tested = sum(1 for f in findings if f.p_value is not None)

    if gate.outcome is ProfileOutcome.CHANGED:
        outcome, reason = ProfileOutcome.CHANGED, gate.reason
    # The gate did not apply: one key only. Decide from that key's own test.
    elif any(f.is_finding for f in findings):
        outcome, reason = ProfileOutcome.CHANGED, gate.reason
    elif n_tested == 0:
        outcome = ProfileOutcome.NOT_TESTABLE
        reason = gate.reason + ", but it had too few events to test"
    else:
        outcome, reason = ProfileOutcome.UNCHANGED, gate.reason

    return AnalysisResult(
        outcome=outcome, outcome_reason=reason,
        gate_p_value=gate.p_value, gate_statistic=gate.statistic,
        findings=findings, n_tested=n_tested, alpha=alpha,
    )

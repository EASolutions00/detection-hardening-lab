"""Tests for the analyser.

Each test states the behaviour it protects. If a panel asks how the correctness
of the analysis is established, this file is the answer.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos import (Classification, Phase, ProfileOutcome, VarianceModel, analyse,
                   naive_differencing)
from telos.differential import global_gate


def make_control(counts: dict[str, list[int]]) -> VarianceModel:
    return VarianceModel.from_control(Phase("control", counts))


STABLE = [100, 101, 99, 100, 100]      # CoV under 1 percent
NOISY = [100, 130, 70, 115, 85]        # CoV around 24 percent


# --------------------------------------------------------------------------
# Variance model
# --------------------------------------------------------------------------

def test_stable_key_has_low_cov():
    vm = make_control({"stable": STABLE})
    assert vm.cov("stable") < 0.01


def test_noisy_key_has_high_cov():
    vm = make_control({"noisy": NOISY})
    assert vm.cov("noisy") > 0.15


def test_dispersion_never_below_poisson():
    """A near-deterministic key would compute dispersion under 1.

    We floor it at 1. With only 5 control runs the variance estimate is itself
    uncertain, and understating it would narrow the confidence interval and
    manufacture significance.
    """
    vm = make_control({"deterministic": [100, 100, 100, 100, 100]})
    assert vm.dispersion("deterministic") == 1.0


def test_variance_model_rejects_too_few_control_runs():
    with pytest.raises(ValueError, match="at least 3 control runs"):
        VarianceModel.from_control(Phase("control", {"a": [1, 2]}))


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------

def test_removed_key_is_lost():
    vm = make_control({"a": STABLE, "b": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100], "b": [100, 100, 100]})
    post = Phase("post", {"a": [0, 0, 0], "b": [100, 100, 100]})
    res = analyse(pre, post, vm)
    got = {f.key: f.classification for f in res.findings}
    assert got["a"] is Classification.LOST


def test_untouched_key_is_unchanged():
    vm = make_control({"a": STABLE, "b": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100], "b": [100, 100, 100]})
    post = Phase("post", {"a": [0, 0, 0], "b": [100, 101, 99]})
    res = analyse(pre, post, vm)
    got = {f.key: f.classification for f in res.findings}
    assert got["b"] is Classification.UNCHANGED


def test_rare_key_is_inconclusive_not_unchanged():
    """The point of the INCONCLUSIVE class.

    A key seen 6 times cannot be tested with any power. Calling it UNCHANGED
    would claim it survived, which the data does not support, and would inflate
    the reported recall.
    """
    vm = make_control({"rare": [2, 2, 2, 2, 2], "big": STABLE, "gone": STABLE})
    pre = Phase("pre", {"rare": [2, 2, 2], "big": [100, 100, 100], "gone": [100, 100, 100]})
    # Changed 2026-09-14. This test used to empty every key in the post-change
    # phase, which is now correctly a failed capture and never reaches the
    # classifier. "big" stays alive so the capture is real, and "gone" is lost
    # so the gate passes and "rare" is actually classified.
    post = Phase("post", {"rare": [0, 0, 0], "big": [100, 100, 100], "gone": [0, 0, 0]})
    res = analyse(pre, post, vm)
    got = {f.key: f.classification for f in res.findings}
    assert got["rare"] is Classification.INCONCLUSIVE


def test_key_appearing_only_after_is_new():
    vm = make_control({"a": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100], "fresh": [0, 0, 0]})
    post = Phase("post", {"a": [0, 0, 0], "fresh": [50, 50, 50]})
    res = analyse(pre, post, vm)
    got = {f.key: f.classification for f in res.findings}
    assert got["fresh"] is Classification.NEW


# --------------------------------------------------------------------------
# The noise-floor guard. This is the core claim of the method.
# --------------------------------------------------------------------------

def test_drop_inside_the_noise_band_is_not_reported():
    """A noisy key that fell by less than its own natural swing is not a finding.

    This is exactly the false positive the naive baseline produces and the
    proposed method does not.
    """
    vm = make_control({"noisy": NOISY, "anchor": STABLE})
    pre = Phase("pre", {"noisy": [100, 100, 100], "anchor": [100, 100, 100]})
    post = Phase("post", {"noisy": [92, 92, 92], "anchor": [0, 0, 0]})
    res = analyse(pre, post, vm)
    got = {f.key: f.classification for f in res.findings}
    assert got["noisy"] is Classification.UNCHANGED


def test_same_drop_on_a_stable_key_is_reported():
    """The same relative drop on a stable key IS a finding.

    Together with the previous test this is the whole argument: an identical
    percentage fall means different things for different event types, and only
    a measured noise floor can tell them apart.
    """
    vm = make_control({"stable": STABLE, "anchor": STABLE})
    pre = Phase("pre", {"stable": [1000, 1000, 1000], "anchor": [1000, 1000, 1000]})
    post = Phase("post", {"stable": [300, 300, 300], "anchor": [1000, 1000, 1000]})
    res = analyse(pre, post, vm)
    got = {f.key: f.classification for f in res.findings}
    assert got["stable"] is Classification.REDUCED


def test_small_drop_fails_the_effect_size_guard():
    """A statistically significant but operationally trivial drop is not reported."""
    vm = make_control({"a": STABLE, "anchor": STABLE})
    pre = Phase("pre", {"a": [10000, 10000, 10000], "anchor": [100, 100, 100]})
    post = Phase("post", {"a": [9000, 9000, 9000], "anchor": [0, 0, 0]})
    res = analyse(pre, post, vm)
    got = {f.key: f.classification for f in res.findings}
    # 10 percent fall, far above the noise floor and hugely significant, but it
    # does not halve the rate, so max_ratio=0.5 keeps it out of the report.
    assert got["a"] is Classification.UNCHANGED


# --------------------------------------------------------------------------
# Global gate
# --------------------------------------------------------------------------

def test_gate_does_not_pass_when_nothing_changed():
    pre = Phase("pre", {"a": [100, 100, 100], "b": [200, 200, 200]})
    post = Phase("post", {"a": [100, 100, 100], "b": [200, 200, 200]})
    gate = global_gate(pre, post, ["a", "b"])
    assert gate.outcome is ProfileOutcome.UNCHANGED
    assert gate.p_value > 0.05


def test_phase_that_emitted_nothing_is_not_testable():
    """Regression, twice over.

    First bug: a post-change phase with zero events everywhere used to raise
    ValueError from chi2_contingency. Fixed by handling it before the test.

    Second bug, found 2026-09-14: that fix made the gate PASS with p = 0, so
    every key with enough events before was then reported LOST. This test used
    to assert exactly that. A dead agent was being reported as blind spots. An
    empty capture is now NOT_TESTABLE, and it still must not crash.
    """
    pre = Phase("pre", {"a": [100, 100, 100], "b": [200, 200, 200]})
    post = Phase("post", {"a": [0, 0, 0], "b": [0, 0, 0]})
    gate = global_gate(pre, post, ["a", "b"])
    assert gate.outcome is ProfileOutcome.NOT_TESTABLE
    assert gate.p_value is None


def test_two_empty_phases_are_not_testable():
    pre = Phase("pre", {"a": [0, 0, 0], "b": [0, 0, 0]})
    post = Phase("post", {"a": [0, 0, 0], "b": [0, 0, 0]})
    gate = global_gate(pre, post, ["a", "b"])
    assert gate.outcome is ProfileOutcome.NOT_TESTABLE


def test_no_findings_produced_when_nothing_changed():
    vm = make_control({"a": STABLE, "b": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100], "b": [200, 200, 200]})
    post = Phase("post", {"a": [100, 100, 100], "b": [200, 200, 200]})
    res = analyse(pre, post, vm)
    assert res.outcome is ProfileOutcome.UNCHANGED
    assert res.findings == []


# --------------------------------------------------------------------------
# A failed capture is not a result. Added 2026-09-14, OPEN-QUESTIONS 16.
# --------------------------------------------------------------------------

def test_dead_agent_is_not_reported_as_blind_spots():
    """The failure this whole thesis is about, inside the analyser itself.

    Before the fix this exact input produced gate_passed=True and two LOST
    findings, verified by running it on 2026-09-14. An agent that stopped
    sending events looked like a hardening change that blinded two detections.
    """
    vm = make_control({"big": STABLE, "mid": [60, 61, 59, 60, 60], "rare": [2, 2, 2, 2, 2]})
    pre = Phase("pre", {"big": [100, 100, 100], "mid": [60, 60, 60], "rare": [2, 2, 2]})
    post = Phase("post", {"big": [0, 0, 0], "mid": [0, 0, 0], "rare": [0, 0, 0]})
    res = analyse(pre, post, vm)
    assert res.outcome is ProfileOutcome.NOT_TESTABLE
    assert res.reported() == []
    assert res.findings == []


def test_one_empty_repetition_makes_the_run_not_testable():
    """An agent that died for part of a phase is the same failure, smaller.

    Before the fix this exact input was reported as "no significant change",
    verified by running it against the previous code on 2026-09-14. Two of the
    three post-change runs recorded nothing, but every key fell by the same
    share, so the profile shape did not move and the gate did not pass. A run
    that was mostly dead was recorded as evidence the change was safe.
    """
    vm = make_control({"a": STABLE, "b": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100], "b": [100, 100, 100]})
    post = Phase("post", {"a": [100, 0, 0], "b": [100, 0, 0]})
    res = analyse(pre, post, vm)
    assert res.outcome is ProfileOutcome.NOT_TESTABLE
    assert "repetition 2 of 3" in res.outcome_reason


def test_empty_pre_change_phase_is_not_testable():
    """Before the fix this passed the gate and reported every key NEW."""
    vm = make_control({"a": STABLE, "b": STABLE})
    pre = Phase("pre", {"a": [0, 0, 0], "b": [0, 0, 0]})
    post = Phase("post", {"a": [100, 100, 100], "b": [100, 100, 100]})
    res = analyse(pre, post, vm)
    assert res.outcome is ProfileOutcome.NOT_TESTABLE
    assert res.findings == []


# --------------------------------------------------------------------------
# A profile with one key is tested, not waved through. Added 2026-09-14.
# --------------------------------------------------------------------------

def test_single_key_profile_is_tested_directly():
    """Before the fix, fewer than two keys returned "not passed", so this real
    70 percent drop was reported as "no significant change". A 2-by-1 table has
    no profile shape to test, so the key is tested on its own.
    """
    vm = make_control({"only": [1000, 1001, 999, 1000, 1000]})
    pre = Phase("pre", {"only": [1000, 1000, 1000]})
    post = Phase("post", {"only": [300, 300, 300]})
    res = analyse(pre, post, vm)
    assert res.outcome is ProfileOutcome.CHANGED
    assert res.gate_p_value is None
    assert {f.key: f.classification for f in res.findings} == {"only": Classification.REDUCED}


def test_single_key_too_rare_to_test_is_not_testable():
    """One key, and it has fewer than 30 events. Nothing was tested, so nothing
    may be claimed, including "unchanged"."""
    vm = make_control({"only": [5, 5, 5, 5, 5]})
    pre = Phase("pre", {"only": [5, 5, 5]})
    post = Phase("post", {"only": [4, 5, 5]})
    res = analyse(pre, post, vm)
    assert res.outcome is ProfileOutcome.NOT_TESTABLE
    assert "too few events" in res.outcome_reason


# --------------------------------------------------------------------------
# The gate uses the alpha it is given. Added 2026-09-14, OPEN-QUESTIONS 23.
# --------------------------------------------------------------------------

def test_gate_uses_the_alpha_it_is_given():
    """This profile gives a gate p of about 0.025.

    Before the fix, analyse(alpha=0.01) still gated at the module default of
    0.05, so the gate passed under a threshold this p value does not meet,
    verified against the previous code on 2026-09-14. A sensitivity sweep on
    alpha would have shown the gate never moving.
    """
    vm = make_control({"a": STABLE, "b": STABLE})
    pre = Phase("pre", {"a": [1000, 1000, 1000], "b": [1000, 1000, 1000]})
    post = Phase("post", {"a": [920, 920, 920], "b": [1000, 1000, 1000]})

    loose = global_gate(pre, post, ["a", "b"], alpha=0.05)
    strict = global_gate(pre, post, ["a", "b"], alpha=0.01)
    assert 0.01 < loose.p_value < 0.05
    assert loose.outcome is ProfileOutcome.CHANGED
    assert strict.outcome is ProfileOutcome.UNCHANGED

    # End to end, through the path that actually carried the bug.
    assert analyse(pre, post, vm, alpha=0.01).outcome is ProfileOutcome.UNCHANGED


# --------------------------------------------------------------------------
# Guards against invalid comparisons
# --------------------------------------------------------------------------

def test_mismatched_repetition_counts_are_rejected():
    vm = make_control({"a": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100]})
    post = Phase("post", {"a": [100, 100]})
    with pytest.raises(ValueError, match="different repetition counts"):
        analyse(pre, post, vm)


def test_mismatched_window_lengths_are_rejected():
    vm = make_control({"a": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100]}, window_minutes=15)
    post = Phase("post", {"a": [100, 100, 100]}, window_minutes=30)
    with pytest.raises(ValueError, match="different window lengths"):
        analyse(pre, post, vm)


def test_ragged_phase_is_rejected():
    with pytest.raises(ValueError, match="uneven repetitions"):
        Phase("bad", {"a": [1, 2, 3], "b": [1, 2]}).validate()


# --------------------------------------------------------------------------
# The baseline, and the head-to-head
# --------------------------------------------------------------------------

def test_naive_reports_every_decrease_however_small():
    pre = Phase("pre", {"a": [100, 100, 100], "b": [100, 100, 100]})
    post = Phase("post", {"a": [99, 99, 99], "b": [100, 100, 100]})
    found = {f.key for f in naive_differencing(pre, post)}
    assert found == {"a"}


def test_proposed_method_beats_naive_on_a_noisy_key():
    """The study's headline claim, as a test.

    One key really was removed. One noisy key drifted down on its own. The naive
    method reports both. The proposed method reports only the real one.
    """
    vm = make_control({"real": STABLE, "noisy": NOISY})
    pre = Phase("pre", {"real": [100, 100, 100], "noisy": [100, 100, 100]})
    post = Phase("post", {"real": [0, 0, 0], "noisy": [93, 91, 95]})

    naive_keys = {f.key for f in naive_differencing(pre, post)}
    proposed_keys = {f.key for f in analyse(pre, post, vm).reported()}

    truth = {"real"}
    assert naive_keys == {"real", "noisy"}      # one true, one false alarm
    assert proposed_keys == truth               # one true, no false alarm
    assert len(naive_keys - truth) == 1
    assert len(proposed_keys - truth) == 0

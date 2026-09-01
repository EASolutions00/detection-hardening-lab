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

from telos import Classification, Phase, VarianceModel, analyse, naive_differencing
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
    vm = make_control({"rare": [2, 2, 2, 2, 2], "big": STABLE})
    pre = Phase("pre", {"rare": [2, 2, 2], "big": [100, 100, 100]})
    post = Phase("post", {"rare": [0, 0, 0], "big": [0, 0, 0]})
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
    passed, p, _ = global_gate(pre, post, ["a", "b"])
    assert not passed
    assert p > 0.05


def test_phase_that_emitted_nothing_does_not_crash():
    """Regression. A post-change phase with zero events everywhere used to raise
    ValueError from chi2_contingency, because an all-zero row makes every
    expected frequency in that row zero.

    This is a real outcome, not a bad input. The agent may have died, or logging
    may have stopped completely. It must be reported, not crash the run.
    """
    pre = Phase("pre", {"a": [100, 100, 100], "b": [200, 200, 200]})
    post = Phase("post", {"a": [0, 0, 0], "b": [0, 0, 0]})
    passed, p, _ = global_gate(pre, post, ["a", "b"])
    assert passed
    assert p == 0.0


def test_two_empty_phases_do_not_crash():
    pre = Phase("pre", {"a": [0, 0, 0], "b": [0, 0, 0]})
    post = Phase("post", {"a": [0, 0, 0], "b": [0, 0, 0]})
    passed, p, _ = global_gate(pre, post, ["a", "b"])
    assert not passed
    assert p == 1.0


def test_no_findings_produced_when_gate_does_not_pass():
    vm = make_control({"a": STABLE, "b": STABLE})
    pre = Phase("pre", {"a": [100, 100, 100], "b": [200, 200, 200]})
    post = Phase("post", {"a": [100, 100, 100], "b": [200, 200, 200]})
    res = analyse(pre, post, vm)
    assert not res.gate_passed
    assert res.findings == []


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

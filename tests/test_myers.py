"""Tests for Myers' difference algorithm (step 3 of the method).

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.myers import (DELETE, EQUAL, INSERT, compare_counts, compare_phases, diff, event_list, joined,
                         merge_sort, render_myers)


def _lcs(a, b) -> int:
    """Length of the longest common subsequence, by the textbook table (for checking only)."""
    t = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            t[i][j] = t[i + 1][j + 1] + 1 if a[i] == b[j] else max(t[i + 1][j], t[i][j + 1])
    return t[0][0]


def _rebuild(ops):
    a = [x for op, x in ops if op in (EQUAL, DELETE)]
    b = [x for op, x in ops if op in (EQUAL, INSERT)]
    return a, b


def test_the_example_from_myers_1986_has_d_5():
    """The paper's own example: ABCABBA to CBABAC needs 5 edits."""
    a, b = list("ABCABBA"), list("CBABAC")
    ops, d = diff(a, b)
    assert d == 5
    assert _rebuild(ops) == (a, b)


def test_the_script_rebuilds_both_lists_and_is_shortest_on_random_lists():
    """Minimal means D = N + M - 2 x (longest common subsequence)."""
    rng = random.Random(1986)
    for _ in range(300):
        a = [rng.choice("ABC") for _ in range(rng.randint(0, 12))]
        b = [rng.choice("ABC") for _ in range(rng.randint(0, 12))]
        ops, d = diff(a, b)
        assert _rebuild(ops) == (a, b)
        assert d == sum(op != EQUAL for op, _ in ops)
        assert d == len(a) + len(b) - 2 * _lcs(a, b)


def test_empty_lists():
    assert diff([], [])[1] == 0
    assert diff(["x", "y"], [])[1] == 2
    assert diff([], ["x"])[1] == 1


def test_merge_sort_sorts_like_python():
    rng = random.Random(7)
    items = [rng.randint(0, 50) for _ in range(200)]
    assert merge_sort(items) == sorted(items)
    assert merge_sort([]) == []


def test_on_sorted_event_lists_myers_equals_count_subtraction():
    before = {"Sysmon-10[GrantedAccess=other]": 44, "Sysmon-1[Image]": 40, "Security-4624[LogonType=10]": 2}
    after = {"Sysmon-1[Image]": 43, "Security-4624[LogonType=10]": 2}
    r = compare_counts(before, after)
    assert event_list({"B": 1, "A": 2}) == ["A", "A", "B"]
    assert r.deleted == {"Sysmon-10[GrantedAccess=other]": 44}
    assert r.inserted == {"Sysmon-1[Image]": 3}
    assert r.d == 47 and r.matches_count_subtraction
    assert (r.events_before, r.events_after) == (86, 45)


def test_phases_are_joined_and_single_run_pairs_are_counted():
    control = [{"K": 10}, {"K": 11}, {"K": 10}]
    before = [{"K": 10, "L": 5}, {"K": 11, "L": 4}]
    after = [{"K": 10}, {"K": 12}]
    assert joined(before) == {"K": 21, "L": 9}
    cmp = compare_phases(control, before, after)
    assert cmp.phases.deleted == {"L": 9} and cmp.phases.inserted == {"K": 1}
    assert cmp.control_pair_d == [1, 0, 1]
    assert len(cmp.before_after_pair_d) == 4
    text = render_myers(cmp)
    assert "Edit distance D = 10" in text and "L" in text
    assert "control against control (no change)   0 to 1 (3 pairs)" in text
    assert cmp.to_dict()["phases"]["deleted"] == {"L": 9}

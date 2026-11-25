"""Myers' difference algorithm: step 3 of the method, "what was removed".

Myers, E. W. (1986). An O(ND) difference algorithm and its variations.
Algorithmica, 1(2), 251-266. https://doi.org/10.1007/BF01840446

The algorithm takes two lists and finds the smallest set of deletions and
insertions that turns the first list into the second (the shortest edit script).
The number of those edits is the edit distance D. It runs in O((N + M) * D) time,
where N and M are the lengths of the two lists. `git diff` uses the same algorithm.

How the method uses it (DECISIONS 2026-11-26):

1. **Each phase becomes one list.** The counts of every valid run of the phase are
   added up, and each event key is written once per event. Raw archive lines cannot
   be compared, because every line carries its own time; event keys can.
2. **The list is sorted** with merge sort, so equal keys sit together.
3. **Myers compares the list before the change with the list after it.** The
   deletions are the events that were lost, the insertions are the new events.

On sorted lists the deletions of one key always equal its count before minus its
count after. The result therefore matches a plain subtraction of counts, and the
module checks this every time (`matches_count_subtraction`). What Myers adds is a
published, proven method for "what was removed" and one number, D, for the size of
the change.

Myers reports every difference, normal variation included: two control runs with no
change still differ. Deciding which differences are larger than the noise floor is
step 4 (`differential.analyse`), not this module.

Two supporting parts, named because the adviser's list names them (OPEN-QUESTIONS 41):
merge sort (`merge_sort`) and a hash map (the dict of counts per key).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations
from typing import Hashable, Mapping, Sequence

EQUAL, DELETE, INSERT = "=", "-", "+"


def merge_sort(items: Sequence) -> list:
    """Sort a list by merge sort: split in two halves, sort each, merge them."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left, right = merge_sort(items[:mid]), merge_sort(items[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    return out + left[i:] + right[j:]


def diff(a: Sequence[Hashable], b: Sequence[Hashable]) -> tuple[list[tuple[str, Hashable]], int]:
    """Myers' greedy shortest edit script from `a` to `b`.

    Returns (ops, D). `ops` is the whole script in order: ("=", item) for an item
    kept, ("-", item) for an item deleted from `a`, ("+", item) for an item inserted
    from `b`. D is the number of "-" and "+" ops.
    """
    n, m = len(a), len(b)
    v = {1: 0}            # furthest x reached on each diagonal k = x - y
    trace: list[dict[int, int]] = []
    for d in range(n + m + 1):
        trace.append(dict(v))
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v[k + 1]          # step down: insert from b
            else:
                x = v[k - 1] + 1      # step right: delete from a
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x, y = x + 1, y + 1   # follow the diagonal: equal items
            v[k] = x
            if x >= n and y >= m:
                return _backtrack(trace, a, b), d
    raise RuntimeError("unreachable: an edit script of length n + m always exists")


def _backtrack(trace: list[dict[int, int]], a: Sequence, b: Sequence) -> list[tuple[str, Hashable]]:
    x, y = len(a), len(b)
    ops: list[tuple[str, Hashable]] = []
    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
        prev_x = v.get(prev_k, 0)
        prev_y = prev_x - prev_k
        while x > prev_x and y > prev_y:
            ops.append((EQUAL, a[x - 1]))
            x, y = x - 1, y - 1
        if d > 0:
            if x == prev_x:
                ops.append((INSERT, b[prev_y]))
            else:
                ops.append((DELETE, a[prev_x]))
        x, y = prev_x, prev_y
    return ops[::-1]


def event_list(counts: Mapping[str, int]) -> list[str]:
    """One entry per event, sorted by merge sort: {"A": 2, "B": 1} -> ["A", "A", "B"]."""
    return merge_sort([key for key, n in counts.items() for _ in range(int(n))])


def joined(runs: Sequence[Mapping[str, int]]) -> dict[str, int]:
    """The counts of several runs added up, key by key (a hash map)."""
    total: dict[str, int] = {}
    for counts in runs:
        for key, n in counts.items():
            total[key] = total.get(key, 0) + int(n)
    return total


@dataclass
class MyersResult:
    """Myers on two sorted event lists."""
    events_before: int
    events_after: int
    d: int
    deleted: dict[str, int] = field(default_factory=dict)
    inserted: dict[str, int] = field(default_factory=dict)
    matches_count_subtraction: bool = True

    def to_dict(self) -> dict:
        return {"events_before": self.events_before, "events_after": self.events_after, "d": self.d,
                "deleted": dict(sorted(self.deleted.items(), key=lambda kv: (-kv[1], kv[0]))),
                "inserted": dict(sorted(self.inserted.items(), key=lambda kv: (-kv[1], kv[0]))),
                "matches_count_subtraction": self.matches_count_subtraction}


def compare_counts(before: Mapping[str, int], after: Mapping[str, int]) -> MyersResult:
    """Myers on the sorted event lists of two count tables."""
    a, b = event_list(before), event_list(after)
    ops, d = diff(a, b)
    deleted = Counter(item for op, item in ops if op == DELETE)
    inserted = Counter(item for op, item in ops if op == INSERT)
    same = deleted == Counter(a) - Counter(b) and inserted == Counter(b) - Counter(a)
    return MyersResult(events_before=len(a), events_after=len(b), d=d, deleted=dict(deleted),
                       inserted=dict(inserted), matches_count_subtraction=same)


@dataclass
class MyersComparison:
    """Step 3 for one comparison: the joined phases, plus single-run distances as context."""
    phases: MyersResult
    runs_before: int
    runs_after: int
    control_pair_d: list[int]
    before_after_pair_d: list[int]

    def to_dict(self) -> dict:
        return {"method": "Myers (1986) on the sorted event lists; each phase's runs joined",
                "runs_before": self.runs_before, "runs_after": self.runs_after,
                "phases": self.phases.to_dict(),
                "single_runs": {"control_vs_control_d": self.control_pair_d,
                                "before_vs_after_d": self.before_after_pair_d}}


def compare_phases(control: Sequence[Mapping[str, int]], before: Sequence[Mapping[str, int]],
                   after: Sequence[Mapping[str, int]]) -> MyersComparison:
    """Myers between the joined phases, and D for every pair of single runs.

    The single-run D values are context for the reader: control runs against each
    other show how large D is when nothing changed. They are not a test; step 4 is.
    """
    return MyersComparison(
        phases=compare_counts(joined(before), joined(after)),
        runs_before=len(before), runs_after=len(after),
        control_pair_d=[compare_counts(x, y).d for x, y in combinations(control, 2)],
        before_after_pair_d=[compare_counts(x, y).d for x in before for y in after])


def _span(values: list[int]) -> str:
    if not values:
        return "none"
    return f"{min(values)} to {max(values)} ({len(values)} pairs)"


def render_myers(cmp: MyersComparison, show: int = 10) -> str:
    LINE = "=" * 78
    r = cmp.phases
    out = [LINE, "MYERS COMPARISON  (step 3: what was removed; Myers 1986)", LINE, ""]
    out.append(f"  Before: {cmp.runs_before} runs joined, {r.events_before} events.   "
               f"After: {cmp.runs_after} runs joined, {r.events_after} events.")
    out.append(f"  Edit distance D = {r.d}   ({sum(r.deleted.values())} deleted, "
               f"{sum(r.inserted.values())} inserted)")
    out.append("")
    out.append("  D between single runs, for context:")
    out.append(f"    control against control (no change)   {_span(cmp.control_pair_d)}")
    out.append(f"    before against after                  {_span(cmp.before_after_pair_d)}")
    out.append("")
    for title, table in (("Deleted (in the runs before, missing after)", r.deleted),
                         ("Inserted (new in the runs after)", r.inserted)):
        out.append(f"  {title}: {len(table)} keys")
        for key, n in sorted(table.items(), key=lambda kv: (-kv[1], kv[0]))[:show]:
            out.append(f"    {n:>6}  {key}")
        if len(table) > show:
            out.append(f"    ... and {len(table) - show} more")
        out.append("")
    out.append(f"  Same result as subtracting the counts per key: {'yes' if r.matches_count_subtraction else 'NO'}")
    out.append("  Myers lists every difference, normal variation included. The telemetry")
    out.append("  comparison below (step 4) decides which ones are larger than the noise floor.")
    out.append("")
    return "\n".join(out)

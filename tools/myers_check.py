"""Check: can Myers' diff run on the system's exported data?

Reads two runs' counts.json (made from Wazuh archives.json), turns each into a
sorted list of event keys (one entry per event), and runs Myers' diff on the two
lists. Prints the deleted and inserted keys with how many times each.
Reads files only. Writes nothing.
"""
import json
import sys
from collections import Counter


def merge_sort(items):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left, right = merge_sort(items[:mid]), merge_sort(items[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]


def myers(a, b):
    """Myers 1986 greedy shortest edit script. Returns a list of ('-', item) / ('+', item)."""
    n, m = len(a), len(b)
    v = {1: 0}
    trace = []
    for d in range(n + m + 1):
        trace.append(dict(v))
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v[k + 1]
            else:
                x = v[k - 1] + 1
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x, y = x + 1, y + 1
            v[k] = x
            if x >= n and y >= m:
                return _back(trace, a, b), d
    raise RuntimeError("unreachable")


def _back(trace, a, b):
    x, y = len(a), len(b)
    edits = []
    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
            pk = k + 1
        else:
            pk = k - 1
        px = v.get(pk, 0)
        py = px - pk
        while x > px and y > py:
            x, y = x - 1, y - 1
        if d > 0:
            if x == px:
                edits.append(("+", b[py]))
            else:
                edits.append(("-", a[px]))
        x, y = px, py
    return edits[::-1]


def sequence(path):
    counts = json.load(open(path, encoding="utf-8"))["counts"]
    items = [k for k, c in counts.items() for _ in range(c)]
    return merge_sort(items)


def main(before, after):
    a, b = sequence(before), sequence(after)
    edits, d = myers(a, b)
    dels = Counter(x for op, x in edits if op == "-")
    ins = Counter(x for op, x in edits if op == "+")
    print(f"events: before {len(a)}, after {len(b)}; edit distance D = {d}")
    print(f"deleted keys: {len(dels)}  (events {sum(dels.values())})")
    for k, c in dels.most_common():
        print(f"  - {c:4d}  {k}")
    print(f"inserted keys: {len(ins)}  (events {sum(ins.values())})")
    for k, c in ins.most_common():
        print(f"  + {c:4d}  {k}")
    # Check: on sorted lists, Myers must give the same answer as a counter difference.
    same = dels == Counter(a) - Counter(b) and ins == Counter(b) - Counter(a)
    print(f"same result as plain count subtraction: {same}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

# Decision Log

Every choice that would be expensive to reverse, or that you will forget the reason for.
Newest at the top. Never delete an entry. If a decision is reversed, add a new entry that
says so and link back.

Format: date, the decision, why, and what it costs if wrong.

---

## 2026-08-19 - Repo stays private until the defense

**Decision:** GitHub repo is private now. Flip to public on defense day.
**Why:** Three unsubmitted thesis proposals in a public repo is an academic integrity and
scooping risk. The commit history still proves months of work when it goes public, which is
the part that has portfolio value.
**Cost if wrong:** Delayed portfolio visibility by a few months. Low.

## 2026-08-19 - Raw run data never enters git

**Decision:** `data/runs/` is gitignored. Only small derived files in `data/summaries/`
are committed.
**Why:** GitHub rejects files over 100 MB and warns past 1 GB per repo. 101 gzipped archive
exports will not fit. Git LFS free tier is 1 GB storage and 1 GB bandwidth per month, which
this would blow past and start costing money.
**Cost if wrong:** Raw data exists on one disk only. Mitigate with a separate backup copy
to a second physical drive, not with git.

## 2026-08-19 - Everything lives in E:\Claude general

**Decision:** Repo, code, docs, and archives all in this one folder on E:.
**Why:** One place to look. Nothing to forget. The blueprint originally put code on C: for
speed, but the only hard rule is that **VMs** must never run from E:. Git and Python on a
hard disk are just slower, not wrong.
**Cost if wrong:** Slower git operations and Python imports. Acceptable.

## 2026-08-19 - T1 gets full structure, T2 and T3 get stubs

**Decision:** Build out `thesis/T1/` properly. T2 and T3 keep a folder and a README that
holds the fallback reasoning.
**Why:** Only one topic will be built. Empty scaffolding for two abandoned topics is
maintenance work for nothing. But the fallback trail must stay written down, because T1
can still fail its spike gate.
**Cost if wrong:** If T1 fails and you switch to T3, you build that structure then. Cheap.

---

# Pinned versions (fill these in during Phase 4 of the runbook)

Nothing below is filled in yet. A version bump partway through the experiment means every
earlier run must be discarded. Record these **before** taking the golden snapshot.

| Item | Value | Date recorded |
|---|---|---|
| Wazuh version | not yet recorded | |
| Sysmon binary version | not yet recorded | |
| Sysmon config SHA256 | not yet recorded | |
| Atomic Red Team commit | not yet recorded | |
| Windows build number | not yet recorded | |
| Harness git commit | not yet recorded | |
| `wazuh/wazuh` clone commit (T2) | not yet recorded | |
| `SigmaHQ/sigma` clone commit (T3) | not yet recorded | |

---

# Spike results (fill in after Phase 7)

The go/no-go gate for T1. Both must be answered before committing.

| Question | Result | Date |
|---|---|---|
| Q1 CoV under Config S | not yet measured | |
| Q1 CoV under Config N | not yet measured | |
| Q2 real wall clock per run | not yet measured | |
| Q2 projected total for 101 runs | not yet measured | |
| **T1 or T3 decision** | **not yet made** | |

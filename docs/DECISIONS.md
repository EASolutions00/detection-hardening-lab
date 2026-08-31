# Decision Log

Every choice that would be expensive to reverse, or that you will forget the reason for.
Newest at the top. Never delete an entry. If a decision is reversed, add a new entry that
says so and link back.

Format: date, the decision, why, and what it costs if wrong.

---

## 2026-08-19 - Windows hypervisor turned off (host runs VMware natively)

**Decision:** Disabled the Windows hypervisor with `bcdedit /set hypervisorlaunchtype off`,
then rebooted. Verified: HypervisorPresent went True to False, VBS status went 2 to 0, vmrun
still works.

**Why:** Phase 0 found a Windows hypervisor running. The cause was the Hyper-V feature, not any
security feature (Memory Integrity off, Credential Guard off, EnableVirtualizationBasedSecurity=0,
no Docker, no WSL2). Two reasons to turn it off:
  1. VMware now runs directly on the hardware. Sharing the machine with the Windows hypervisor
     can add timing changes, and T1 measures timing variance. This removes that variance source.
  2. Hardening change #8 (Credential Guard) needs nested virtualization inside the guest. VMware
     exposes that more reliably when the host hypervisor is off.

**Cost if wrong / how to reverse:** `bcdedit /set hypervisorlaunchtype auto` then reboot. This
also disables Docker Desktop, WSL2, and host Credential Guard while off, but none of those are
in use here.

**Must stay off for the whole experiment.** Changing this mid-experiment changes timing and
invalidates prior runs. It is now part of the host baseline, same status as a pinned version.

## 2026-08-31 - Build the analysis core before the lab, using synthetic data

**Decision:** Write stages 2, 3 and 5 of the pipeline (variance model, differential analysis,
reporting) now, tested against generated counts. Leave stage 1 (acquisition from live VMs) and
stage 4 (impact scoring) until later.

**Why:** The analyser consumes event counts. It does not care whether a real Windows machine or
a script produced them. So nothing about stages 2, 3 and 5 needs a lab, Wazuh, or Atomic Red
Team. Waiting for the lab before writing any code would have cost weeks for no reason.

This also corrects an earlier claim in this log. The broken hardening catalogue
(OPEN-QUESTIONS item 1) was described as blocking everything. It is not. It blocks the
**experiment design**, not the analyser.

**Cost if wrong:** Synthetic data proves the code is correct. It proves nothing about real
telemetry. Real event counts are not normally distributed, and the demo generator draws from a
rounded normal. No result from `src/demo.py` may be presented as a finding. The moment real
captures exist, the same tests must be re-run against them.

**Immediate benefit:** the test suite found a genuine crash before any real data existed. See
the WORKLOG entry for the same date.

## 2026-08-19 - T3 loses its fallback status (SigmaHQ has only 6 STP-annotated rules)

**Finding:** `SigmaHQ/sigma` at commit `da9bb07` carries STP robustness tags on only **6 of
3,783 rules (0.16%)**. See the full evidence in OPEN-QUESTIONS.md, Answered section.

**Decision:** T3 can no longer be treated as the safe fallback to T1. Its Objective 5 (validate
automated scores against the manually annotated subset with Cohen's kappa) cannot be executed on
6 rules across 4 levels.

**Why this matters now:** The plan assumed T1 primary, T3 fallback. As of this finding there is
**no verified fallback.** If T1 fails its spike gate, the options are:
  1. Redesign T3's validation: annotate a subset yourself with a second annotator and report
     inter-rater agreement. This turns T3 into a partly manual study and weakens its main
     selling point (that it validates against someone else's labels).
  2. Switch the fallback to **T2** (severity inversion), which needs no external annotation
     corpus. Its weakness is self-created ground truth, which is a smaller problem than having
     no ground truth at all.

**Cost if wrong:** Low to act on now, high to ignore. Knowing this in August means the fallback
can be rebuilt calmly. Discovering it in October, after a failed T1 spike, means no time to
recover.

**Not yet decided:** which of the two paths above. This is a strategic call to make alongside
the T1 spike result, not before it. T1 is still the primary and still the goal.

## 2026-08-19 - Repo can be public now (supersedes the private decision below)

**Decision:** The repo can be public from the start. No need to wait for the defense.

**Why:** The professor confirmed two things. There are no intellectual property rules that
stop a student publishing thesis work early. And there is no similarity-check problem: a
match between the final paper and the student's own public repo is not treated as an issue.

This removes both reasons the earlier entry gave for staying private.

**Still true, separate point:** the repo has no code yet. It is not a strong portfolio piece
until the harness exists. Being public early does not harm this, because the value of a public
repo is the commit history built over time. Publishing now starts that history and also backs
up the work off the single local disk.

**Cost if wrong:** Low. A public repo can be made private again at any time.

## 2026-08-19 - Repo stays private until the defense (SUPERSEDED, see entry above)

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

A version bump partway through the experiment means every earlier run must be discarded.
Record these **before** taking the golden snapshot.

## Host and analysis stack (recorded 2026-08-31)

| Item | Value | Date recorded |
|---|---|---|
| Host OS | Windows 11 Pro 10.0.26200 | 2026-08-31 |
| CPU | AMD Ryzen 9 7950X, 16C/32T | 2026-08-20 |
| VMware Workstation | 17.5.1 build-23298084 | 2026-08-20 |
| Windows hypervisor | **OFF** (`hypervisorlaunchtype off`) | 2026-08-20 |
| Python | 3.13.14 (`C:\Program Files\Python313`) | 2026-08-31 |
| numpy | 2.5.2 | 2026-08-31 |
| scipy | 1.18.1 | 2026-08-31 |
| pandas | 3.0.5 | 2026-08-31 |
| PyYAML | 6.0.3 | 2026-08-31 |
| pytest | 9.1.1 | 2026-08-31 |
| Analyser git commit | `78f41f4` (first version of the analysis core) | 2026-08-31 |

`scipy` supplies Benjamini-Hochberg through `scipy.stats.false_discovery_control`, so
`statsmodels` is not a dependency. `scikit-learn` was in the original plan for Cohen's kappa,
which belonged to T3 and is no longer in scope.

## Lab stack (fill in during Runbook Phase 4)

| Item | Value | Date recorded |
|---|---|---|
| Wazuh version | not yet recorded | |
| Sysmon binary version | not yet recorded | |
| Sysmon config SHA256 | not yet recorded | |
| Atomic Red Team commit | not yet recorded | |
| Windows build number (guest) | not yet recorded | |
| Ubuntu ISO used | `ubuntu-24.04.4-live-server-amd64.iso` (selected, not yet installed) | 2026-08-20 |
| Windows ISO used | `Windows 11 Enterprise Eval 26200.6584...25h2` (selected, not yet installed) | 2026-08-20 |

## Reference corpora

| Item | Value | Date recorded |
|---|---|---|
| `SigmaHQ/sigma` clone commit | `da9bb07d642a2826e89702445d32c795209ec108` | 2026-08-19 |
| `wazuh/wazuh` clone commit | not yet cloned | |

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

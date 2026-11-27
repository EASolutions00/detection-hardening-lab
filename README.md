# TeLoS

**Te**lemetry **Lo**ss. A tool that checks whether a security hardening change created detection blind spots.

Undergraduate BS Computer Science thesis, plus the purple team lab built to run it.

> **Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Myers' Difference
> Algorithm**
>
> Elijah Amorsolo, OED20-0012616

This is the title of the revised proposal. It changed on 2026-11-26, when Myers' difference algorithm
became the core algorithm (`docs/DECISIONS.md` 2026-11-26). The adviser takes the revision to the panel
for approval. The title approved in September 2026 ended "Using Differential Analysis Algorithm".

---

## The problem

A detection rule never watches an attacker directly. It watches the events a system emits, and
configuration decides which events a system emits.

Security hardening is the act of changing configuration. So a change made to reduce risk can
also delete the evidence a detection rule depends on. The rule stays enabled. It stays green on
the coverage report. It detects nothing.

Nothing errors. Nothing alerts. Teams usually find out during an incident, months later.

---

## What it does

TeLoS does not harden anything. It measures what one hardening change did to the evidence.

1. The engineer exports Wazuh's event archive from the SIEM: runs before the change, runs after it,
   and control runs with no change at all.
2. TeLoS reads the export and compares the events before and after the change.
3. It reports which events disappeared or dropped by more than their normal run-to-run variation,
   which Wazuh rules and MITRE ATT&CK techniques depended on them, and which techniques had alerts
   before the change and none after.

Output: `report.txt`, `findings.json`, `comparison.csv`, and an ATT&CK Navigator layer. It runs from
the command line today; the window (graphical interface) is not built yet.

---

## Results from the lab

The evaluation ran on 2026-11-26 and 2026-11-27: **26 valid runs** on one Windows 11 endpoint,
restored to the same snapshot before every run, with one pinned attack list. Six cases:

- three hardening changes: C1 (WDigest off), C3 (LSA Protection on), C5 (Network Level Authentication on);
- three test cases, K1 to K3, which turn off a logging setting on purpose, so the right answer is known
  in advance. A test case is a configuration mistake, never a hardening change.

Every expected result was committed before the runs ([docs/EXPECTED-RESULTS.md](docs/EXPECTED-RESULTS.md)).
Which rules were fixed before the data and which were decided after the control runs: [docs/FREEZE-DATES.md](docs/FREEZE-DATES.md).
Scored at the level of event keys (defined below):

| Method | Expected losses | Found | False alarms | Missed |
|---|---|---|---|---|
| TeLoS | 7 | 7 | 0 | 0 |
| Plain subtraction of counts | 7 | 7 | 1 | 0 |

**What these numbers cover.** All 7 expected losses come from the three test cases, K1 to K3: logging settings turned
off on purpose, not hardening. K2 and K3 expect the same event key, so the 7 losses are 6 distinct keys. None of the
three hardening changes caused a blind spot: in C1 and C5 no key fell at all, and C3 blocked the attack itself. So the table
shows that TeLoS finds evidence losses that are known to exist. It is not a measured rate for blind spots caused by
hardening, because this study had no such case. In each case, 15 to 18 of the 35 or 36 event keys had enough events to
be tested; the others are reported as INCONCLUSIVE or NEW, never as safe.

- **K1, "Audit Logon" off:** the 5 expected event keys LOST, and exactly the 3 expected techniques no
  longer detected: T1021.001, T1078.002 and T1550.002. The sign-in still worked (Sysmon shows its Remote Desktop
  session start in all 3 runs), so this is a blind spot.
- **K2, command line off:** a field-level loss. Event 4688 was still written, but without `CommandLine`.
- **K3, process creation auditing off:** the 4688 key LOST; no technique lost, as expected.
- **C1 and C5:** no key lost or reduced, as expected.
- **C3 did not come out as expected.** The credential dump was blocked, as expected: the three test programs
  started, but none could open `lsass.exe`, and no dump file was written. But Sysmon event 10
  fell to 0.672 of its rate, which is above the 0.5 reporting limit, and T1055 still counts as detected
  through two other rules. Reported as found, not re-run ([docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md)
  item 44).

**Read these numbers with care.** It is a small study: 7 expected losses, all in the 3 test cases, in one lab. All
3 before runs happened to fall in the quieter of two groups the control runs showed, so plain
subtraction had an easy case in C1 and C5. The score also depends on the test used for a key that falls to zero.
Four other tests, tried after the runs, find 7, 6, 5 and 0 of the 7 losses, and none finds a false one; the 0 comes
from a test that counts runs, which cannot pass the correction with only 3 runs per side. Full scoring:
`docs/EXPECTED-RESULTS.md` section 7. Reports: `data/summaries/eval-2026-11-26/`.

---

## The noise floor, shown on synthetic data

This is real output from `src/demo.py`. I simulated one hardening change: one event key removed
outright, one that lost a field while the event kept firing, one genuinely cut to 29 percent, and
seven quiet keys that drifted on their own.

```
  method                       TP   FP   FN  precision   recall      F1
  -------------------------- ---- ---- ---- ---------- -------- -------
  naive differencing            3    7    0     30.0%  100.0%   0.462
  proposed system               3    0    0    100.0%  100.0%   1.000
```

Both methods found all three real losses. The difference is the seven false alarms.

Each false alarm is an event key that moved on its own, by less than the amount it was already
measured to move. An engineer comparing raw counts would investigate every one of them. TeLoS
measures each event key's natural variation first, then only reports a drop that exceeds it.

An **event key** is the event type plus which of its tracked fields actually carried a value, for
example `Security-4688[CommandLine,NewProcessName]`. That is how a change that empties one field,
while the event keeps firing at its usual rate, becomes visible at all. K2 above is that case. For
three fields that detection rules match by value (`GrantedAccess`, `LogonType` and
`AuthenticationPackageName`), the key also keeps the value, grouped into the classes the rules look for
(built 2026-11-03).

**These numbers are synthetic.** They demonstrate that the code is correct. They are not
measurements, and they are not a result of the study. Full output:
[docs/demo-output.txt](docs/demo-output.txt)

---

## Run it

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

```bash
.venv/Scripts/python.exe src/demo.py
```

```bash
.venv/Scripts/python.exe -m pytest tests -q
```

The demo needs no lab, no SIEM, and no virtual machines. The analyser consumes event counts and
does not care where they came from. The lab commands (one capture, the evaluation batch, one
comparison from run folders) are listed in [CLAUDE.md](CLAUDE.md); they need the lab.

---

## Status

Honest state of the work, not a plan. Checked 2026-11-27.

| Part | Status |
|---|---|
| Reading Wazuh's archive into event keys, with value classes | **Built** |
| Myers' difference algorithm, step 3 of the pipeline | **Built** 2026-11-26 |
| Noise floor, rate ratio per key, Benjamini-Hochberg correction, classification | **Built** |
| Links from lost keys to Wazuh rules and ATT&CK techniques; ranking; coverage change | **Built** |
| Report and exports (text, JSON, CSV, ATT&CK Navigator layer); reproducibility record | **Built** |
| Recommendations from a curated list of compensating controls | **Built**; entries for C3 and C5 only |
| Capture harness (Python over `vmrun`): restore, change, attack tests, export, run checks | **Built**; used for all 26 evaluation runs |
| Lab, runbook Phases 0 to 7 | **Done**. Golden snapshot `golden-base-v2` taken 2026-11-26 |
| Evaluation runs and their scoring | **Done** 2026-11-27 (results above) |
| Percentage of techniques lost | Not built. Proposed in the revised form, not decided |
| Graphical interface (a desktop application, not a web application; decided 2026-09-14, kept 2026-10-07) | Not built |
| Evaluation by security engineers with an ISO/IEC 25010 form | Not started |
| Domain controller `DC-01` (decided 2026-09-29, dropped 2026-11-11) | Will not be built |

196 tests pass (`pytest`, 2026-11-28). Day-to-day status: [docs/STATUS.md](docs/STATUS.md).

---

## How the analysis works

In the order the code runs it (`src/telos/pipeline.py`):

1. **Read and key the events.** Each run's archive export becomes counts per event key.
2. **Check the runs.** Only valid runs are used: at least 3 per phase, all with the same settings (one
   parameters hash), and all "after" runs of one change. The harness voids a run whose attack tests did
   not run as pinned: its number of process starts (Sysmon event 1) is outside the control runs' mean
   plus or minus 3 standard deviations, or the sign-in step failed (`docs/DECISIONS.md` 2026-11-27).
3. **Myers' difference algorithm.** Each phase's runs are joined into one sorted list of events. Myers
   finds the shortest list of deletions and insertions that turns the "before" list into the "after"
   list. It lists every difference, normal noise included (Myers 1986; `docs/DECISIONS.md` 2026-11-26).
4. **Measure the noise floor.** From 5 control runs with nothing changed, measure how much each event
   key moves on its own: its coefficient of variation (the run-to-run spread as a share of its mean) and
   its dispersion (how much wider that spread is than pure chance would give).
5. **Test each key.** A rate ratio (the rate after divided by the rate before) for every key, using the
   spread measured in step 4. Then Benjamini-Hochberg correction, because testing many keys at once
   produces some findings by chance alone. One chi-square test over the whole profile is reported as a
   summary and never stops this step (changed 2026-09-28).
6. **Classify.** LOST, REDUCED, UNCHANGED, NEW, or INCONCLUSIVE.
7. **Impact.** Which Wazuh rules read each lost key, which ATT&CK techniques those rules detect, and
   which techniques had alerts before the change and none after.

A key is only reported as REDUCED when three conditions hold together: the corrected q value (the p
value after the correction) is at most 0.05, the rate at least halved, and the drop exceeds three times
the key's own coefficient of variation. Any one alone is not enough. A key is LOST when the control runs
saw it, it fell to exactly zero after the change, and it still passes the correction. Such a key is
tested with an exact test at any count; a partial drop needs at least 30 events before, or it is
INCONCLUSIVE (`docs/DECISIONS.md` 2026-11-26).

---

## Repository layout

```
docs/     runbook, decision log, work log, open questions, command record, expected results
src/      TeLoS analyser and the lab harness (Python)
tests/    196 tests
thesis/   the proposal, its figures, and the two alternatives that were not chosen
lab/      lab design, pinned configs, change scripts
data/     runs/ is local only; summaries/ holds the committed results
tools/    the document checker, and the Word conversion tools
```

Start with [CLAUDE.md](CLAUDE.md). It is the index to everything.

---

## Build the lab yourself

[docs/RUNBOOK-homelab.md](docs/RUNBOOK-homelab.md) rebuilds the whole thing from a bare host,
in phases 0 to 8, with a check at the end of each one.

Host: AMD Ryzen 9 7950X, 64 GB RAM, VMware Workstation 17.5.1. A Wazuh 4.14.7 SIEM on Ubuntu, and
Sysmon and Atomic Red Team on a Windows 11 endpoint, driven over `vmrun` from Python on the Windows
host. There is no domain controller (dropped 2026-11-11). Every command run on the host is recorded in
[docs/COMMANDS.md](docs/COMMANDS.md), with what a correct result looks like.

---

## Methodology notes

Three things here are deliberate.

**A pre-declared falsifiable outcome.** Before collecting any data, I state the result that
would prove my own central claim unnecessary, and commit to reporting it without softening. The
statistical layer is only justified if the laboratory's run-to-run variance is non-zero. If it
turns out to be negligible, I report that plainly and restrict the claim to production
deployment, where the variance floor is not controlled by snapshot restoration.
**Measured since:** in the feasibility spike (2026-11-16), the median event key did not vary between
runs with no change, and 5 of 20 keys varied by more than 5%. In the evaluation, plain subtraction
reported 1 false loss and TeLoS none (`docs/EXPECTED-RESULTS.md` section 7). That one false loss, a key that fell
from 211 to 209, is also removed by the simple rule that a loss must at least halve, and every true loss fell to zero.
So this evaluation does not yet show what measuring the noise adds.

**Untestable is reported, not assumed safe.** An event key seen too few times before a change
cannot be tested with any power. TeLoS reports these as INCONCLUSIVE rather than folding them
into UNCHANGED. Calling them unchanged would claim they survived, which the data does not
support, and would inflate the reported recall. The exception is a key that disappears
completely: the exact chance of seeing no event needs no minimum count, so such a key is tested
whatever its count (DECISIONS 2026-11-26).

**A failed capture is not a result.** The same rule applies to a whole run. Before 14 September
2026, a run whose agent had sent nothing after the change was reported as a list of lost event
keys. In a three-key test, two came back LOST: the analyser made the exact mistake this thesis
is about. It now reports that run as not
testable, and the tests that prove it were first run against the old code to show they catch the
defect.

Claims that are engineering judgment rather than sourced fact are labeled `(unverified)`
inline throughout.

---

## Alternatives considered

I wrote up two other topics as full proposals before choosing T1. Both remain in
[thesis/](thesis/README.md).

**T2, severity inversion in the Wazuh ruleset.** Rules form a dependency graph, and a serious
alert can sit at a severity level no analyst ever sees. Not chosen, and not a fallback: T1 is the
final thesis with no fallback topic (`docs/DECISIONS.md` 2026-09-26). T1's feasibility spike ran on
2026-11-16 (19 of 19 runs valid), and the full evaluation on 2026-11-26 and 2026-11-27 (26 of 26 valid).

**T3, analytic robustness scoring.** Score how hard each detection rule is to evade, and
validate against the manually annotated subset of the Sigma corpus. **I killed it after
checking the assumption it rested on.** Counting the corpus at pinned commit `da9bb07` turned
up only **6 rules out of 3,783** carrying a Summiting the Pyramid annotation, which is 0.16
percent. Far too few for the agreement statistic the evaluation depended on. Method and
evidence in [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md).

---

## License

Code and documentation are released under the [MIT License](LICENSE). You may use, copy,
modify, and redistribute the work, including for commercial use, as long as the copyright
notice is kept. This keeps the tool usable by small companies, which is a stated goal of the
thesis.

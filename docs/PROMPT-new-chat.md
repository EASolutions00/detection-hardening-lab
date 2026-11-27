# TeLoS project map

Paste this whole file into a new chat. Select all, copy, paste. Nothing needs trimming.

There are no tables in this file on purpose. Everything is plain lines, so it survives being
copied from any view and survives being soft-wrapped in any editor.


## Read only

Do not edit or create any file. Do not commit, push, or generate anything. If something needs
changing, tell me **what** and **where**, and I will decide whether to do it here or in a
separate working chat.

**What "do not start work" means:** do not change anything, and do not begin a task I have not
asked for. **Reading files, running the read-only commands in section 7, and reporting back are
not work.** Those are expected. `pytest` writes a small cache folder and that is fine.

This map is a **supplement**. `CLAUDE.md` in the repository carries the project summary, the four
answering rules, the commands, the rules that fail silently, the session habits, and the defense
brief. This file deliberately does not repeat any of it. It adds what `CLAUDE.md` has no room
for: a routing list from question to file, the settled numbers, the open items, and what is built
versus only designed.


## 0. Paths, read this first

This chat may not be running inside the project folder, so every path below is absolute.

```
REPO = E:\Claude general
DOCS = E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)
```

Wherever you see `REPO\` or `DOCS\` below, **expand it to the full path above before reading.**
Commands in section 7 are already written out in full and must be copied literally.

`REPO` is the git repository, public at `github.com/EASolutions00/hardening-blind-spots` (renamed
2026-11-27 from `detection-hardening-lab`; the old address redirects).
`DOCS` is outside the repository and is not version controlled; the `.docx` files are assembled
there. `DOCS\prep-local\` holds defense preparation deliberately removed from the public repo on
2026-09-10. Do not propose putting it back.

**If a read is refused because the path is outside your working directory, tell me plainly.** I
will either grant access or reopen the chat in `REPO`. **Do not guess at file contents, and do
not answer from memory of this project.**

**If you have no filesystem at all** (a browser chat, a phone), say so immediately. Nothing here
is readable, and you should ask me to paste `REPO\CLAUDE.md` and
`C:\Users\Elijah\.claude\CLAUDE.md` instead. Expect narrower answers.


## 1. Boot sequence

Read these five, in order. Expand `REPO` first.

1. `REPO\CLAUDE.md`
   This auto-loads only if the chat was opened in `REPO`. Otherwise read it explicitly.
   It goes stale: four claims in it were wrong on 2026-09-10 and were corrected that day.
   **Treat it as a map, not as truth.**

2. `REPO\docs\STATUS.md`
   The current blockers and dates, kept short. Added to this list 2026-09-28.

3. `REPO\docs\OPEN-QUESTIONS.md`
   Items **1, 25 to 28, 32, 33, 35, 38 and 44** are still open, in whole or in part. Items 0, 15 to
   24, 29, 30, 36, 37 and 39 to 43 are answered, decided or built; item 31 no longer arises and item
   34 did not arise in the study. All are summarised in section 5
   (checked 2026-11-27). The file is ranked by damage, so read from the top.

4. `REPO\docs\DECISIONS.md`
   Every entry from the newest back to 2026-09-26 (sixteen entries on 2026-10-08).

5. `REPO\docs\WORKLOG.md`
   The newest three entries.

Then run this, exactly as written, so it works from any folder:

```
git -C "E:\Claude general" log --oneline -8
```

Then stop. Section 9 says what to report.


## 2. The map: where to look, by question type

Read the file on the right before answering a question on the left.

Where a file or folder is, inside or outside the repo; which file is the source and which a copy;
what must never be committed
    -> `REPO\docs\FILE-MAP.md`

Why a choice was made, or whether something is settled
    -> `REPO\docs\DECISIONS.md`

What is uncertain, what might change the plan
    -> `REPO\docs\OPEN-QUESTIONS.md`

What happened, and when
    -> `REPO\docs\WORKLOG.md`, newest first, plus `git log`

A command that was run, or what a correct result looks like
    -> `REPO\docs\COMMANDS.md`

Building the lab, VMs, networking, phases
    -> `REPO\docs\RUNBOOK-homelab.md`

Lab design, resource budget, the hardening change catalogue
    -> `REPO\lab\blueprint.md`

The event key, what is counted, field presence
    -> `REPO\src\telos\eventkey.py`

Myers' difference algorithm, the core algorithm (step 3 of the pipeline)
    -> `REPO\src\telos\myers.py`; the order of all steps: `REPO\src\telos\pipeline.py`, `compare()`

The statistics: capture check, whole-profile chi-square (a summary, not a gate), rate ratio,
correction, classification
    -> `REPO\src\telos\differential.py`

One capture window on the lab, and the run checks (item 22's void rule)
    -> `REPO\src\telos\harness.py`; the lab's fixed pieces: `REPO\src\telos\catalog.py`

The evaluation: each case's expected result, the scoring, and the results
    -> `REPO\docs\EXPECTED-RESULTS.md` (section 7 holds the results); the reports:
    `REPO\data\summaries\eval-2026-11-26\`

The noise floor, coefficient of variation, dispersion
    -> `REPO\src\telos\variance.py`

The naive baseline the method is measured against
    -> `REPO\src\telos\baseline.py`

Data shapes: Phase, Finding, Classification
    -> `REPO\src\telos\model.py`

The activity diagram
    -> `REPO\thesis\T1\figures\make_activity_diagram.py`, which **is** the diagram

The other three figures
    -> `REPO\thesis\T1\figures\make_pipeline_figure.py`
    -> `REPO\thesis\T1\figures\make_noise_floor_figure.py`
    -> `REPO\thesis\T1\figures\svgkit.py`

Proposal numbering and template rules
    -> `REPO\thesis\README.md`

The diagram explained in plain words, for a junior analyst
    -> `DOCS\ACTIVITY-DIAGRAM-EXPLAINED.md`

The proposal revision that goes to the panel next
    -> `DOCS\proposal-form-SIMPLIFIED.md` (its working note lists the student's open choices)
    The version submitted 2026-10-15 is `DOCS\proposal-form-FINAL.md`, now frozen.

The adviser's instructions of 2026-11-23, each with its transcript line and status
    -> `DOCS\CONSULTATION-2026-11-23-CHECKLIST.md`, and `REPO\docs\DECISIONS.md` 2026-11-23

Panel questions and the reasoning behind each answer
    -> `DOCS\T1-PANEL-RESPONSE.md`

What changed after the title defense, up to the 2026-10-15 submission (superseded)
    -> `DOCS\T1-REVISIONS-LIST.md`

Whether documents contradict the code
    -> `REPO\tools\check_docs.py`, see section 7


## 3. Authority order, when two sources disagree

1. The code in `REPO\src\telos\`. What is actually built.
2. `REPO\docs\DECISIONS.md`. What was decided, and why.
3. `DOCS\proposal-form-SIMPLIFIED.md`. What will be submitted next.
4. Everything else is explanatory and loses.

**A document is never evidence about another document.**


## 4. Settled numbers, so you start from the right place

Verify any you rely on. Listed so you do not re-derive them every session. Files named below are
in `REPO\src\telos\` unless stated otherwise.

- An event key is `Source-EventID[PopulatedField,...]`, for example
  `Security-4688[CommandLine,NewProcessName]`. The lab endpoint audits process creation with the
  command line since 2026-11-03 (item 20); test case K2 turns the command line off.
  `eventkey.py`

- The key records **that** a tracked field carried a value. **Built 2026-11-03** (decided
  2026-09-29, item 18): for three fields that rules match by value it also records **which**
  value, grouped into the classes the rules look for, and `other` for every other value:
  `GrantedAccess` (Sysmon 10), and `LogonType` and `AuthenticationPackageName` (4624). Each
  class holds the rule's own pattern. `LmPackageName` and the ticket encryption type are not read
  by any rule, so they are not tracked (DECISIONS 2026-10-01). The key has no host part (item 31).
  `eventkey.py`, `VALUE_KEYED_FIELDS`, `is_populated()`

- **Myers' difference algorithm** is step 3 of the pipeline (DECISIONS 2026-11-26): each phase's
  runs are joined into one sorted list, and D is the number of deletions plus insertions. On
  sorted lists it equals per-key subtraction, and the module checks this on every run. On the
  spike's C3 runs, single runs gave D = 1 to 28 control against control, and 56 to 76 before
  against after. The classification still comes from the statistics below.
  `myers.py`; `pipeline.py`, `compare()`

- The rule set is **Wazuh 4.14.7's shipped rules**, exported whole: 454 rules in 15 files read a
  Windows event. With them only **C1, C3 and C5** can blind a detection, and the study reports that
  (choice 1). The attack tests are chosen from those rules; Atomic Red Team has no T1078 test, so
  C1's test is chosen during lab setup. DECISIONS 2026-10-01; OPEN-QUESTIONS 1.

- Empty, `-`, `N/A`, `(null)` and `NULL` count as absent. **Numeric zero counts as present.**
  `eventkey.py`, `is_populated()`

- Chi-square runs **once** over the whole 2 by K profile, never per key, and since 2026-09-28 it
  is **reported, never a filter**: every key is tested whatever it says. Among 299 steady keys a
  key falling from 198 events to 0 gave p = 0.999, and the old gate then tested no key.
  `differential.py`, `global_gate()` and `analyse()`; DECISIONS 2026-09-28

- A run has one of three profile outcomes: **CHANGED, UNCHANGED, NOT_TESTABLE**. Since
  2026-09-28 the outcome comes from the keys: CHANGED if any key is LOST or REDUCED, UNCHANGED if
  keys were tested and none is, NOT_TESTABLE if the capture failed or no key had enough events.
  Any repetition that recorded zero events in total makes the run NOT_TESTABLE, never LOST
  (since 2026-09-14). A profile with only one key skips the chi-square.
  `model.py`, `ProfileOutcome`; `differential.py`, `capture_problem()`, `analyse()`

- Classification order is **NEW; then LOST by the exact test for a key the control runs saw that
  drops to zero, at any count (added 2026-11-26); then INCONCLUSIVE for fewer than 30 before;
  then INCONCLUSIVE for a key the control runs never saw (added 2026-09-28); then the rate-ratio
  test**. A rare LOST that fails the correction becomes INCONCLUSIVE, never UNCHANGED.
  `differential.py`, `_test_key()`, `classify()`; `variance.py`, `VarianceModel.measured()`

- LOST requires the post-change count to be **exactly zero**.
  `differential.py`, `_test_key()`

- REDUCED needs all three together: `q <= 0.05`, `RR <= 0.5`, and `(1 - RR) > 3 * CoV`.
  `differential.py`, `classify()`

- The noise floor comparison is **exceed**, not "below".
  `differential.py`, `classify()`

- `ALPHA = 0.05`, `MAX_RATIO = 0.5`, `MIN_PRE_COUNT = 30`, `NOISE_SIGMAS = 3.0`.
  `MIN_PRE_COUNT` applies to partial drops only since 2026-11-26 (DECISIONS 2026-11-26).
  `differential.py`

- Rate is the count divided by the **number of runs**, not per unit time.
  `differential.py`, `_test_key()`

- Dispersion is floored at 1.0.
  `variance.py`

- Field-loss pairing matches a LOST key to a NEW key of the same event type whose field set is a
  strict subset.
  `eventkey.py`, `field_loss_pairs()`

- **The evaluation, done 2026-11-27:** 5 control runs, 3 before runs shared by all cases, and 3
  after runs for each of C1, C3, C5 and the test cases K1 to K3: 26 runs, all valid, one
  parameters hash `9895d0cf...14cd` (DECISIONS 2026-11-27; EXPECTED-RESULTS sections 5 and 7).
  A run is voided by item 22's rule: Sysmon 1 in the window outside 79.8 to 141.8, or the step
  `rdp-signin-30s` did not exit 0. A voided run is captured again under a new id.
  **Scope, decided 2026-09-29:** keep every measurable class C change (3 under Wazuh's shipped
  rules: C1, C3, C5, DECISIONS 2026-10-01); if a checkpoint is missed, cut the graphical
  interface first and then class B. "16" is no longer a target.
  `REPO\src\telos\evaluation.py`; `REPO\lab\blueprint.md`

- **The result, scored as fixed before the runs:** TP 7, FP 0, FN 0 over C1, C5, K1, K2 and K3;
  plain subtraction found the same 7 with 1 false positive (in K2). K1 is a blind spot: exactly
  T1021.001, T1078.002 and T1550.002 no longer detected, while the sign-in still worked. K2 shows
  the field-level loss of `CommandLine`. **C3 did not come out as expected** (item 44).
  EXPECTED-RESULTS section 7.

- One attack-test list, window and repetition count, pinned once in Phase 0 for every change.
  Remediation suggestions are **two levels**: surviving sources and known compensating controls.
  Fixes are applied **by script**; the accepted baseline is the snapshot plus the scripts.
  All three are design, `REPO\docs\DECISIONS.md` 2026-09-28.

- The feasibility spike answers **six** questions, not two: runbook Phase 7. It ran 2026-11-16,
  19 of 19 runs valid; the answers are in runbook Phase 7 and STATUS ("The spike").

### Facts that get stated wrong, including in this project's own documents

- **Event 4104 is PowerShell script block logging**, in
  `Microsoft-Windows-PowerShell/Operational`. **Not** the Security log.

- **Event 4688 carries `ParentProcessName`.** `ParentImage` is a Sysmon field name.

- **Rate is per run, not per minute.**

- **Figures are generated, not drawn.** The generator script is the source. Two real defects here
  were caught only by rendering the picture and looking at it.


## 5. Open, so do not state these as settled

Item 44: open, new 2026-11-27. C3's real effect is below the REDUCED threshold
    In the evaluation C3 blocked the dump: rules 92403 and 61625 (T1055, level 12) fired in all 8
    control and before runs and in none of the 3 C3 runs. But `Sysmon-10` fell only to a rate
    ratio of 0.672 (q = 8.8e-5), above the 0.5 limit, and T1055 stays "detected" through rules
    61632 and 61634. So the system says "no blind spot"; by the rules that stopped, the truth is
    prevention. Reported as found; nothing is re-run or retuned. For the student and the adviser.

Item 38: open, for the adviser. No hardening change shows a blind spot under the shipped rules
    C1 and C5 show no change, and C3 is prevention: measured in the trials (2026-11-13) and again
    in the evaluation (2026-11-27). The way forward taken: test cases with a known answer, K1 to
    K3 (item 42, 2026-11-26). K1 is a blind spot, as expected. The adviser has not yet taken it up
    (DECISIONS 2026-11-23).

Item 21: ANSWERED 2026-11-11, DC-01 dropped
    Every class C hardening change is an authentication control, and there is no domain
    controller. **The archive count ran 2026-09-26: 4768, 4769 and 4776 are zero on every date,
    and 0 of 2,892 logons were network logons.** **Decided: build DC-01**, with its own Wazuh
    agent and a test that makes network logons, before the golden snapshot. **Superseded
    2026-11-11: DC-01 is dropped.** The lab is WIN-EP-01 and SIEM-01; C5 uses a local account
    over RDP from the host; C4, C6 and B5 leave the study.

Item 18: ANSWERED 2026-11-03, built
    The key saw field presence, not value. Six of the eight class C hardening changes state a
    telemetry effect that is a value change, which the analyser cannot see. The planned capture
    (`RunAsPPL`, then read `GrantedAccess`) **could not run as written**, found 2026-09-26: the
    pinned Sysmon config records no Event 10 at all, and `RunAsPPL = 1` writes a UEFI firmware
    variable. **Decided:** value keying for a short list of fields (final list after the C3
    capture); an `lsass.exe` Sysmon rule; `RunAsPPL = 2`, a stated deviation, because CIS
    18.9.27.2 (Windows 11 Enterprise v5.1.0) requires the lock. **Built 2026-11-03:** the
    `lsass.exe` Sysmon rule is applied (Sysmon 10 = 121 in the archive that day) and value keying
    is coded and tested. C3 was measured with it in the spike (2026-11-16) and in the evaluation
    (2026-11-27).

Item 22: ANSWERED 2026-11-27, decided and built
    The stimulus was asserted identical across runs and never verified. **The void rule**
    (DECISIONS 2026-11-27): a run is voided when its stimulus fingerprint, the Sysmon 1 events in
    the window, is outside the 5 control runs' mean plus or minus 3 standard deviations (79.8 to
    141.8), or when the step `rdp-signin-30s` did not exit 0. Built as `harness.RunChecks`; each
    run's fingerprint is in its record, not in the hashed parameters. It cannot tell C3's blocked
    attack from lost evidence: under C3 the test programs still start.

Item 26: partly built
    The harness's own `vmrun` guest calls write logons inside the window: 2,285 type 4 across the
    archive, 1,641 on 2026-09-02. **Cause confirmed 2026-11-12:** one `vmrun` guest call wrote two
    4624 type 4 logons by `vmtoolsd.exe`, and Wazuh rule 67022 (level 3) fired on each; with
    Credential Validation on, also two 4776. The harness records the number of guest calls in each
    run's manifest (`guest_calls`). A different count does not void a run (not built).

Item 27 — the lab network, cause unknown
    The host's VMware adapters broke on their own twice, 2026-08-31 and before 2026-09-26.
    Repaired by hand. The pre-flight check and the harness must confirm VMnet2 holds
    `10.20.10.1` before any run.

Item 28 — boot-time evidence
    Events written before the Wazuh agent starts never reach the archive: zero 6005 and zero
    Wininit events on every date. Boot-time checks, such as Wininit event 12 for LSA
    protection, must be made inside the guest. Cause unverified. Seen again after a restart on
    2026-11-12: 0 event 6005, 0 Wininit.

Item 30 — ANSWERED 2026-11-03, connected
    `analyse()` now calls `field_loss_pairs()` and `report.py` prints the result (OPEN-QUESTIONS 30).

Item 29 — ANSWERED 2026-09-28, all four fixed by decision
    Chat 4e01d810's four findings all held and are fixed (DECISIONS 2026-09-28): the
    chi-square is a reported summary and every key is tested; one attack-test list is pinned
    in Phase 0 and a key the control runs never saw is INCONCLUSIVE; remediation is two
    levels; fixes are applied by script. The first two are in code with tests.

Item 25: the schedule. Data collection answered 2026-11-27; the rest open
    **Data collection is done:** the spike ran 2026-11-16 (19 of 19 valid, 9.8 minutes per run),
    and the 26 evaluation runs were all valid by 2026-11-27, before the 2026-11-30 checkpoint.
    Testable keys: 15 of 35 in the evaluation's control runs (WORKLOG 2026-11-27). **Decided
    2026-09-29:** school deadline 4 June 2027; target a final defense by the end of January 2027
    (March was recommended); keep every measurable class C change; if a checkpoint is missed, cut
    the graphical interface first, then class B. **Next defense: the pre-oral**, a 50% working
    system and chapters 1 to 3; no date stated (DECISIONS 2026-11-23). Still open: the graphical
    interface, the evaluation by security engineers, the chapters, and the dates. Checkpoints are
    in STATUS.md.

Item 24 — ANSWERED 2026-11-03, built
    `VarianceModel.from_control()` now refuses a control run that recorded nothing (OPEN-QUESTIONS 24).

Item 23: ANSWERED 2026-11-16 by the spike
    The alpha half is fixed. The other half, the gate passing on noise, no longer matters: since
    2026-09-28 the chi-square is reported, not a filter. The question it pointed at, do the per-key
    tests produce false findings on real noise: 0 false findings in the spike's 10
    control-versus-control pairs (2026-11-16), and 0 in 70 comparisons of the evaluation's 5
    control runs (2026-11-27, DECISIONS 2026-11-27).

Item 20: ANSWERED 2026-11-03
    Process Creation auditing with command line, and Credential Validation auditing, are on in
    WIN-EP-01 (COMMANDS 2.11); in the archive the same day, 4688 = 117. Both golden snapshots keep
    them (`golden-base` 2026-11-16, `golden-base-v2` 2026-11-26).

Item 34: did not arise in the study (2026-11-27)
    A negative control blocks its own attack test on purpose, and the design voided any run whose
    tests did not all complete. Found 2026-10-20. The void rule built 2026-11-27 checks only the
    Sysmon 1 fingerprint and the sign-in step, so C3, whose dump the change blocks, kept 3 valid
    after runs. The study has no class B negative control. Reopen if one is added.

Item 35 — which LSASS tests fire rule 92900
    Part 1 of the LSASS trial (2026-11-03): Defender stopped all three tests, 0 lsass events.
    Part 2 (2026-11-13, Defender off): tests 1, 2 and 13 never fire 92900 (it fires only on
    Defender's and svchost's own access). Test 13 fires 92403 and 61625 (level 12) with LSA
    Protection off, none with it on: **decided as prevention, not a blind spot** (DECISIONS
    2026-11-13). Test 13 leaves a second `lsass.exe` running, so it must run last. Tests 3, 4,
    9 (fresh boot), 12 and 14 not run. The pinned attack list uses tests 1, 2 and 13, after a
    Remote Desktop sign-in (DECISIONS 2026-11-18).

Item 36: ANSWERED 2026-11-16. LSA Protection was already on, decided 2026-11-03
    The baseline turns it off (`RunAsPPL = 0`); C3 turns it on. Shown 2026-11-16 on a test boot of
    `golden-base`: no Wininit event 12 since boot, and `RunAsPPL 0` (COMMANDS 2.16).

Item 37: ANSWERED, the C5 test, decided 2026-11-12 and 2026-11-13
    Baseline: Remote Desktop on, NLA off, firewall open to `10.20.10.1` only. With the default
    client, NLA on and off write the same events (two type 3 NTLM with 92657, two type 10 with
    92653), so C5 is reported as "the predicted effect was not seen". The sign-in runs from the
    host with `eli`'s password stored by `cmdkey`, no box. No sign-out step: the revert ends the
    session. A second sign-in into an existing session writes type 7 and no 92653. Confirmed
    2026-11-16 on the first revert of `golden-base`: no `eli` logon from the boot until the
    student's own sign-in (COMMANDS 2.16).

Item 15 — answered 2026-10-15
    Submitted 2026-10-15 by email: `DOCS\Detecting … Algorithm.pdf` (made from
    `DOCS\Detecting … Algorithm.docx`) and the two diagram sheets as full-size PDFs. The revisions
    list was not sent; it was not required. The Word file is now the source of the submitted
    text: if FINAL changes, the Word file must be changed to match, and the HTML copies made again.

Item 31 — the event key has no host part
    With DC-01 there are two monitored Windows hosts, and the same key from both is counted
    together, so a drop on one host can be hidden by a rise on the other. Found 2026-09-30. No
    longer arises since DC-01 was dropped (2026-11-11).

Item 32 — four harness and index points with no record
    Whether the capture window has a fixed length or ends when the suite ends; whether DC-01 is
    restored before each run; a mapping from Wazuh field names to the key's field names; and
    whether DC-01 still earns its days now that no positive case needs it. Recorded 2026-10-08.
    The DC-01 points were decided 2026-11-11: dropped. The window has a fixed length (decided
    2026-11-13), and the field-name mapping is built in `archive.py` and `index.py` (2026-11-13).
    **Left, for the student:** the key map does not track three 4624 fields that rules read
    (`IpAddress`, `TargetUserSid`, `WorkstationName`); adding them changes the keys.

Item 33: the professor's guidelines, two of four points open
    From the Research 1A lectures (paths in the item). Point 1: the next defense is the pre-oral
    (50% working system, chapters 1 to 3); its date was not stated (DECISIONS 2026-11-23). Point 4:
    answered 2026-11-23, the form gets an evaluation objective, with security engineers as
    respondents. Still open: point 2, related study 2 is a preprint; point 3, no APA in-text
    citations. Found 2026-10-12.

Item 1: the catalogue, no longer blocks data collection
    The study used C1, C3 and C5, plus the test cases K1 to K3 (EXPECTED-RESULTS section 1). Their
    numbers are those of CIS Microsoft Windows 11 Enterprise v3.0.0, the version Wazuh's scan
    checks (DECISIONS 2026-11-26). Several control IDs of changes outside the study are still
    `(unverified)` (item 4).

Settled 2026-09-14, so do not reopen these
    The title is the panel's proposed wording, verbatim, with no article added (item 0).
    **Superseded 2026-11-26:** the title of the revised proposal ends "Using Myers' Difference
    Algorithm" (DECISIONS 2026-11-26); the panel has not yet approved the revision. The system
    is a Python application with a graphical interface beside the SIEM, not a web application
    (item 17; kept 2026-10-07, see below). The interface toolkit is not decided. Both in
    `REPO\docs\DECISIONS.md`.

Settled 2026-09-26 and 2026-09-28, so do not reopen these
    T1 is final, with no fallback topic (2026-09-26). The chi-square is a reported summary and every
    key is tested; one attack-test list is pinned in Phase 0 and a key the control runs never saw is
    INCONCLUSIVE; remediation is two levels; fixes are applied by script (all 2026-09-28, closing
    item 29). All in `REPO\docs\DECISIONS.md`.

Settled 2026-09-29, so do not reopen these
    Target: final defense by the end of January 2027, school deadline 4 June 2027. Scope keeps every
    measurable class C change. Build DC-01 with a network-logon test (dropped 2026-11-11). Value keying for a short list
    of fields, an `lsass.exe` Sysmon rule, `RunAsPPL = 2`. Process creation and credential
    validation auditing in the golden snapshot. All in `REPO\docs\DECISIONS.md`; built and applied
    2026-11-03, and in the golden snapshots since 2026-11-16.

Settled 2026-10-01 to 2026-10-08, so do not reopen these
    Operator access: the system has no login; only the operator's MFA account can read its
    credentials. The rule set is Wazuh 4.14.7's shipped rules, choice 1 (C1, C3, C5). The attack
    tests are chosen from those rules. The system stays a desktop application (2026-10-07). The
    web-based idea was the student's own at the title defense; the chair then asked that the
    document declare it. The answer went in the submission email, which asks the panel whether it
    accepts the desktop application; Revision 8 was not sent (corrected note, 2026-10-15).
    Submitted 2026-10-15, after the 2026-10-12 latest date (2026-10-08 entry, overtaken). All in
    `REPO\docs\DECISIONS.md`.

Settled 2026-11-03 to 2026-11-13, so do not reopen these
    C3 is measured with Defender off; the baseline turns LSA Protection off (both 2026-11-03).
    DC-01 is dropped; the lab is WIN-EP-01 and SIEM-01 (2026-11-11). The baseline has Remote
    Desktop on with NLA off (2026-11-12). C5 uses the default client and is reported as "the
    predicted effect was not seen"; the revert ends the C5 session (both 2026-11-13). C3's lost
    level-12 alerts are prevention, not a blind spot (2026-11-13). All in `REPO\docs\DECISIONS.md`.
    **Measured the same day:** the C1 trial changed no sign-in event, so no candidate change shows
    a blind spot under the shipped rules (`REPO\docs\OPEN-QUESTIONS.md` item 38, for the student and
    the adviser).

Settled 2026-11-16 to 2026-11-27, so do not reopen these
    `golden-base` taken, with no `cfg-suppressed` or `cfg-natural` snapshot: Config S by an
    after-boot script (2026-11-16). The pinned attack list: a Remote Desktop sign-in, then LSASS
    tests 1, 2 and 13 (item 40, 2026-11-18). The study host stays the current PC until the defense
    (2026-11-18). Test cases K1 to K3 with expected results written before any run (item 42); a
    key that drops to zero gets the exact test at any count (item 43); `golden-base-v2` with one
    CIS version, v3.0.0; the guest scripts run only on WIN-EP-01; Myers' difference algorithm is
    the core algorithm, each phase's runs joined (item 41) (all 2026-11-26). The harness's wait
    for VMware Tools; 3 runs per phase; item 22's void rule (all 2026-11-27). All in
    `REPO\docs\DECISIONS.md`.

Not an item yet — no longer blocks anything (the revisions list was not sent, 2026-10-15)
    The REVISED-to-FINAL diff has never been run. Measured 2026-09-10: FINAL is 6,395 words
    against REVISED's 7,742. **Re-measure rather than quoting these.**


## 6. Built versus only designed

**Do not describe designed parts as if they exist.**

Built, tested, and used on the real lab, in `REPO\src\telos\` (checked 2026-11-27):
    `archive.py` (reads Wazuh's archive into counts per fenced window), `eventkey.py` (event keys,
    with value classes since 2026-11-03), `myers.py` (Myers' difference algorithm, step 3,
    2026-11-26), `variance.py`, `differential.py`, `index.py` (which Wazuh rules read an event key,
    from the rule export in `REPO\data\rules\`, not in git), `impact.py` (ranks lost keys by blind
    techniques, highest severity, number of rules; surviving coverage counts rules that did fire
    after the change, DECISIONS 2026-11-13), `report.py` (verdict, noise floor, findings, ranked
    blind spots with remediation level 1, coverage change, remediation level 2, reproducibility
    record; JSON, CSV and ATT&CK Navigator exports; the Myers section comes from `myers.py`), `pipeline.py` with the command
    `src/run.py`, `harness.py` (one capture window over `vmrun`; fixed-length windows; run checks
    with item 22's void rule since 2026-11-27), `catalog.py` with `src/capture.py`, `spike.py` with
    `src/spike.py`, `evaluation.py` with `src/evaluate.py`, `baseline.py`, `model.py`, `synth.py`.
    12 test files in `REPO\tests\`, 170 tests passing (2026-11-27). Remediation level 2 reads
    `REPO\lab\knowledge\compensating-controls.json`, which has entries for C3 and C5 only.

Designed only, no code exists:
    the graphical interface (a window: upload the export, "Run analysis", then the report); the
    percentage of techniques lost (proposed in the revised form, not decided); the evaluation form
    for security engineers (ISO/IEC 25010). Voiding a run whose `vmrun` call count differs
    (item 26) is not built either.

The lab:
    SIEM-01 and WIN-EP-01 exist; DC-01 will not be built. Runbook Phases 0 to 7 are done.
    `golden-base` (2026-11-16) and `golden-base-v2` (2026-11-26) exist; every evaluation run reverts
    to `golden-base-v2`. The spike's 19 runs (2026-11-16) and the evaluation's 26 runs (2026-11-26
    to 2026-11-27) are all valid. Read `REPO\docs\STATUS.md` and `REPO\docs\WORKLOG.md` for the
    current state rather than assuming.

T1 is final and there is no fallback (`REPO\docs\DECISIONS.md` 2026-09-26). T2 and T3 were not
chosen. If the spike shows T1 cannot finish, the answer is a scope cut (item 25), not a new topic.


## 7. Read-only commands that work from any folder

Copy these literally. No `cd` is needed and no shell-specific chaining is used. All three were
tested from an unrelated directory on 2026-09-10 and work unchanged.

```
git -C "E:\Claude general" log --oneline -8

"E:\Claude general\.venv\Scripts\python.exe" -m pytest "E:\Claude general\tests" -q

"E:\Claude general\.venv\Scripts\python.exe" "E:\Claude general\tools\check_docs.py" "E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)"
```

In PowerShell a quoted executable needs the call operator, so write
`& "E:\Claude general\.venv\Scripts\python.exe" ...`. In cmd or bash the quotes alone are enough.

`pytest` should print `170 passed` (2026-11-27). If it prints anything else, stop and tell me,
because the record is stale.

`check_docs.py` flags statements in any document that contradict the code. **It flags, it does
not judge.** A hit is a question, not a verdict. File status decides whether a hit matters:
FROZEN files are the version the panel read, so old wording there is **correct**. It produces
false positives on purpose, for example a sentence explaining why chi-square is *not* per event
type.

**Do not run the figure generators in this chat.** They write files, and this chat is read only.

**Never run** `git-filter-repo`, a force push, or any history rewrite.


## 8. Answering, beyond what CLAUDE.md already says

1. **Answer the question I asked, then add what I will need next.** Do not make me ask three
   follow-ups to get a complete answer.

2. **When I question something, do not change your answer on contact.** Verify at the source,
   show me the evidence, say plainly whether you were wrong or right, then propose. My question
   is not proof you were wrong.

3. **When you do not know, say so**, then name the file that would answer it and offer to read
   it. Do not fill a gap with something plausible.

4. **If anything in this message contradicts what you actually read, tell me.** This map goes
   stale, and the file it points at is always the truth.


## 9. Start

Do the boot sequence in section 1. Then tell me, in five lines: what is decided, what is
blocked, and what is next. Then stop and wait for my question.

Before I close this chat, give me a WORKLOG entry for it, in the template at the top of
`REPO\docs\WORKLOG.md`, inside one code block so I can paste it. Name what we found and what I
decided, even if no file changed. Do not write it to the file yourself.

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

`REPO` is the git repository, public at `github.com/EASolutions00/detection-hardening-lab`.
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
   Items **1, 18, 20 to 28, and 30 to 33** are the live ones (23 reframed as a spike check; 18,
   20, 21, 24, 25 and 30 decided but not built). All
   are summarised in section 5. Items 0, 15, 16, 17, 19 and 29 are answered. The file is ranked by damage, so read from
   the top.

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

The statistics: capture check, whole-profile chi-square (a summary, not a gate), rate ratio,
correction, classification
    -> `REPO\src\telos\differential.py`

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

The proposal being submitted
    -> `DOCS\proposal-form-FINAL.md`

Panel questions and the reasoning behind each answer
    -> `DOCS\T1-PANEL-RESPONSE.md`

What changed after the title defense
    -> `DOCS\T1-REVISIONS-LIST.md`

Whether documents contradict the code
    -> `REPO\tools\check_docs.py`, see section 7


## 3. Authority order, when two sources disagree

1. The code in `REPO\src\telos\`. What is actually built.
2. `REPO\docs\DECISIONS.md`. What was decided, and why.
3. `DOCS\proposal-form-FINAL.md`. What will be submitted.
4. Everything else is explanatory and loses.

**A document is never evidence about another document.**


## 4. Settled numbers, so you start from the right place

Verify any you rely on. Listed so you do not re-derive them every session. Files named below are
in `REPO\src\telos\` unless stated otherwise.

- An event key is `Source-EventID[PopulatedField,...]`, for example
  `Security-4688[CommandLine,NewProcessName]`. A format example only: the lab endpoint writes
  no 4688 events, because process creation auditing is off (item 20).
  `eventkey.py`

- The key records **that** a tracked field carried a value, never **which** value. That is the
  code today. **Decided 2026-09-29, not built:** for a short list of fields (set after the C3
  capture) the key will record the value, grouped into a few classes. DECISIONS 2026-09-29.
  Under Wazuh's shipped rules the candidates are `GrantedAccess`, `LogonType` and
  `AuthenticationPackageName`; `LmPackageName` and the ticket encryption type are not read by any
  rule, so they are not tracked (DECISIONS 2026-10-01). The key has no host part (item 31).
  `eventkey.py`, `is_populated()`

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

- Classification order is **NEW, then INCONCLUSIVE for fewer than 30 before, then INCONCLUSIVE
  for a key the control runs never saw (added 2026-09-28), then LOST**.
  `differential.py`, `_test_key()`; `variance.py`, `VarianceModel.measured()`

- LOST requires the post-change count to be **exactly zero**.
  `differential.py`, `_test_key()`

- REDUCED needs all three together: `q <= 0.05`, `RR <= 0.5`, and `(1 - RR) > 3 * CoV`.
  `differential.py`, `classify()`

- The noise floor comparison is **exceed**, not "below".
  `differential.py`, `classify()`

- `ALPHA = 0.05`, `MAX_RATIO = 0.5`, `MIN_PRE_COUNT = 30`, `NOISE_SIGMAS = 3.0`.
  `differential.py`

- Rate is the count divided by the **number of runs**, not per unit time.
  `differential.py`, `_test_key()`

- Dispersion is floored at 1.0.
  `variance.py`

- Field-loss pairing matches a LOST key to a NEW key of the same event type whose field set is a
  strict subset.
  `eventkey.py`, `field_loss_pairs()`

- 5 control runs, 3 pre and 3 post per change, as designed. The catalogue holds 14. **Scope,
  decided 2026-09-29:** keep every measurable class C change (about 3 under Wazuh's shipped rules:
  C1, C3, C5, DECISIONS 2026-10-01), reduce the graphical
  interface first and then class B; the spike sets the final number. "16" is no longer a target.
  Each phase ends with 3 **valid** runs: a failed run is voided and captured again (design,
  2026-09-28).
  `REPO\lab\blueprint.md`

- One attack-test list, window and repetition count, pinned once in Phase 0 for every change.
  Remediation suggestions are **two levels**: surviving sources and known compensating controls.
  Fixes are applied **by script**; the accepted baseline is the snapshot plus the scripts.
  All three are design, `REPO\docs\DECISIONS.md` 2026-09-28.

- The feasibility spike answers **six** questions, not two: runbook Phase 7.

### Facts that get stated wrong, including in this project's own documents

- **Event 4104 is PowerShell script block logging**, in
  `Microsoft-Windows-PowerShell/Operational`. **Not** the Security log.

- **Event 4688 carries `ParentProcessName`.** `ParentImage` is a Sysmon field name.

- **Rate is per run, not per minute.**

- **Figures are generated, not drawn.** The generator script is the source. Two real defects here
  were caught only by rendering the picture and looking at it.


## 5. Open, so do not state these as settled

Item 21 — decided 2026-09-29, not built
    Every class C hardening change is an authentication control, and there is no domain
    controller. **The archive count ran 2026-09-26: 4768, 4769 and 4776 are zero on every date,
    and 0 of 2,892 logons were network logons.** **Decided: build DC-01**, with its own Wazuh
    agent and a test that makes network logons, before the golden snapshot. **Superseded
    2026-11-11: DC-01 is dropped.** The lab is WIN-EP-01 and SIEM-01; C5 uses a local account
    over RDP from the host; C4, C6 and B5 leave the study.

Item 18 — decided 2026-09-29, not built
    The key sees field presence, not value. Six of the eight class C hardening changes state a
    telemetry effect that is a value change, which the analyser cannot see. The planned capture
    (`RunAsPPL`, then read `GrantedAccess`) **could not run as written**, found 2026-09-26: the
    pinned Sysmon config records no Event 10 at all, and `RunAsPPL = 1` writes a UEFI firmware
    variable. **Decided:** value keying for a short list of fields (final list after the C3
    capture); an `lsass.exe` Sysmon rule; `RunAsPPL = 2`, a stated deviation, because CIS
    18.9.27.2 (Windows 11 Enterprise v5.1.0) requires the lock. **Built 2026-11-03:** the
    `lsass.exe` Sysmon rule is applied (Sysmon 10 = 121 in the archive that day) and value keying
    is coded and tested. No class C change has been measured yet: no capture run exists.

Item 22 — blocks the harness design
    The stimulus is asserted identical across the two phases and never verified. A hardening
    change that makes an atomic test fail produces a rate drop the analyser reports as LOST.
    Per-atomic exit status and a stimulus fingerprint must go in the run manifest, because they
    cannot be reconstructed after the run.

Item 26 — blocks the harness design
    The harness's own `vmrun` guest calls write logons inside the window: 2,285 type 4 across the
    archive, 1,641 on 2026-09-02. **Cause confirmed 2026-11-12:** one `vmrun` guest call wrote two
    4624 type 4 logons by `vmtoolsd.exe`, and Wazuh rule 67022 (level 3) fired on each; with
    Credential Validation on, also two 4776. The harness must count its calls and record the number.

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

Item 25 — the schedule; target and scope decided 2026-09-29
    The harness does not exist and the spike has never run. The 2026-09-22 tripwire passed with no
    capture window run. **Decided 2026-09-29:** school deadline 4 June 2027; target a final defense
    by the end of January 2027 (March was recommended); keep every measurable class C change,
    reduce the graphical interface first, then class B; the spike sets the number, by 2026-11-07
    since 2026-10-16 (was 2026-10-31; the lab checkpoint moved to 2026-10-30, after the re-presentation).
    Checkpoints are in STATUS.md. The panel said the re-presentation will focus on the activity
    diagram, and sets its date 3 to 7 days after the revised documentation is submitted. It was
    submitted 2026-10-15, after three missed dates (2026-10-02, 2026-10-07, 2026-10-12); the panel set
    the re-presentation for Thursday 2026-10-22, 3:30 to 5:00 pm. Also: 30
    pre-change events over 3 runs is about 10 per run, so many keys may be untestable. The spike
    measures it.

Item 24 — ANSWERED 2026-11-03, built
    `VarianceModel.from_control()` now refuses a control run that recorded nothing (OPEN-QUESTIONS 24).

Item 23 — reframed 2026-09-28, a spike check
    The alpha half is fixed. The other half, the gate passing on noise, no longer matters: since
    2026-09-28 the chi-square is reported, not a filter. What remains is the question it pointed
    at: do the per-key tests produce false findings on real noise? Run `analyse()` on the ten
    control-versus-control pairs from the Phase 7 spike. There should be no findings.

Item 20 — applied 2026-11-03 in the guest
    Process Creation auditing with command line, and Credential Validation auditing, are on in
    WIN-EP-01 (COMMANDS 2.11); in the archive the same day, 4688 = 117. The golden snapshot does
    not exist yet, so they are in no snapshot.

Item 34 — the run check voids every post-change run of a negative control
    A negative control blocks its own attack test on purpose, and the run check voids any run
    whose tests did not all complete. Found 2026-10-20. Open.

Item 35 — which LSASS tests fire rule 92900
    Part 1 of the LSASS trial (2026-11-03): Defender stopped all three tests, 0 lsass events.
    Part 2 (2026-11-13, Defender off): tests 1, 2 and 13 never fire 92900 (it fires only on
    Defender's and svchost's own access). Test 13 fires 92403 and 61625 (level 12) with LSA
    Protection off, none with it on: **decided as prevention, not a blind spot** (DECISIONS
    2026-11-13). Test 13 leaves a second `lsass.exe` running, so it must run last. Tests 3, 4,
    9 (fresh boot), 12 and 14 not run.

Item 36 — LSA Protection was already on, decided 2026-11-03
    The baseline turns it off (`RunAsPPL = 0`); C3 turns it on. Open until the golden image is
    shown to boot without Wininit event 12.

Item 37 — the C5 test, decided 2026-11-12 and 2026-11-13
    Baseline: Remote Desktop on, NLA off, firewall open to `10.20.10.1` only. With the default
    client, NLA on and off write the same events (two type 3 NTLM with 92657, two type 10 with
    92653), so C5 is reported as "the predicted effect was not seen". The sign-in runs from the
    host with `eli`'s password stored by `cmdkey`, no box. No sign-out step: the revert ends the
    session. A second sign-in into an existing session writes type 7 and no 92653. Left open:
    confirm on the first real revert of the golden snapshot.

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
    The DC-01 points were decided 2026-11-11: dropped. The window length and the mapping remain.

Item 33 — the professor's guidelines, four open points
    From the Research 1A lectures (paths in the item): is January the pre-oral defense (50% working
    system) or the final; related study 2 is a preprint; no APA in-text citations; no usability
    evaluation with respondents. Found 2026-10-12. Point 1 changes the schedule.

Item 1 — blocks data collection
    The catalogue: 14 changes, no longer a target of 16. Three control IDs verified, several
    still `(unverified)`. Under Wazuh's shipped rules, three positive cases (2026-10-01).

Settled 2026-09-14, so do not reopen these
    The title is the panel's proposed wording, verbatim, with no article added (item 0). The system
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
    validation auditing in the golden snapshot. All in `REPO\docs\DECISIONS.md`, none built.

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
    **Measured the same day, not yet decided:** the C1 trial changed no sign-in event, so no
    candidate change shows a blind spot under the shipped rules (`REPO\docs\OPEN-QUESTIONS.md`
    item 38, for the student and the adviser).

Not an item yet — no longer blocks anything (the revisions list was not sent, 2026-10-15)
    The REVISED-to-FINAL diff has never been run. Measured 2026-09-10: FINAL is 6,395 words
    against REVISED's 7,742. **Re-measure rather than quoting these.**


## 6. Built versus only designed

**Do not describe designed parts as if they exist.**

Built and tested, in `REPO\src\telos\`:
    `eventkey.py`, `variance.py`, `differential.py`, `baseline.py`, `report.py`, `model.py`,
    `synth.py`. Two test files in `REPO\tests\`, 65 tests passing (run 2026-11-13). Value keying
    for the short field list, the control-run check (item 24) and field-loss pairing (item 30)
    were added 2026-11-03.

Designed only, no code exists:
    the event-key to rule to ATT&CK dependency index, impact scoring, remediation candidate
    generation, all of Phase 5, the reader for Wazuh's archive JSON, and the capture harness that
    would drive Phases 0 to 3. Also designed only, added to the diagram 2026-09-28: the per-run
    check that voids and re-captures a failed run (item 22), and confirming the change on the host
    (item 28).

The lab:
    SIEM-01 and WIN-EP-01 exist; DC-01 will not be built. The runbook is partly executed: no
    golden snapshot, no change script and no capture run exist yet (2026-11-13). Read
    `REPO\docs\STATUS.md` ("Now, as of 2026-11-13" and "Lab state") and `REPO\docs\WORKLOG.md`
    for how far rather than assuming.

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

`pytest` should print `58 passed`. If it prints anything else, stop and tell me, because the
record is stale.

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

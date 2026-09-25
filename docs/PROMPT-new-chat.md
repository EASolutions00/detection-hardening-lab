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

Read these four, in order. Expand `REPO` first.

1. `REPO\CLAUDE.md`
   This auto-loads only if the chat was opened in `REPO`. Otherwise read it explicitly.
   It goes stale: four claims in it were wrong on 2026-09-10 and were corrected that day.
   **Treat it as a map, not as truth.**

2. `REPO\docs\OPEN-QUESTIONS.md`
   Items **1, 15, 18, and 20 to 25** are the live ones. All are summarised in section 5.
   Items 0, 16, 17 and 19 are answered. The file is ranked by damage, so read from the top.

3. `REPO\docs\DECISIONS.md`
   The newest five entries.

4. `REPO\docs\WORKLOG.md`
   The newest three entries.

Then run this, exactly as written, so it works from any folder:

```
git -C "E:\Claude general" log --oneline -8
```

Then stop. Section 9 says what to report.


## 2. The map: where to look, by question type

Read the file on the right before answering a question on the left.

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

The statistics: gate, rate ratio, correction, classification
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
  `Security-4688[CommandLine,NewProcessName]`.
  `eventkey.py`

- The key records **that** a tracked field carried a value, never **which** value.
  `eventkey.py`, `is_populated()`

- Empty, `-`, `N/A`, `(null)` and `NULL` count as absent. **Numeric zero counts as present.**
  `eventkey.py`, `is_populated()`

- Chi-square runs **once** over the whole 2 by K profile, never per key.
  `differential.py`, `global_gate()`

- A run has one of three profile outcomes: **CHANGED, UNCHANGED, NOT_TESTABLE**. Any
  repetition that recorded zero events in total makes the run NOT_TESTABLE, never LOST. A
  profile with only one key skips the chi-square and tests that key directly. Since 2026-09-14.
  `model.py`, `ProfileOutcome`; `differential.py`, `capture_problem()`

- Classification order is **NEW, then INCONCLUSIVE, then LOST**.
  `differential.py`, `_test_key()`

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

- 16 hardening changes, 5 control runs, 3 pre and 3 post per change.
  `REPO\lab\blueprint.md`

### Facts that get stated wrong, including in this project's own documents

- **Event 4104 is PowerShell script block logging**, in
  `Microsoft-Windows-PowerShell/Operational`. **Not** the Security log.

- **Event 4688 carries `ParentProcessName`.** `ParentImage` is a Sysmon field name.

- **Rate is per run, not per minute.**

- **Figures are generated, not drawn.** The generator script is the source. Two real defects here
  were caught only by rendering the picture and looking at it.


## 5. Open, so do not state these as settled

Item 21 — blocks the catalogue, the golden snapshot, and data collection
    Every class C hardening change is an authentication control, and there is no domain
    controller. `DC-01` is Tier B in `lab/blueprint.md` and was never built. **The archive count
    ran 2026-09-26: 4768, 4769 and 4776 are zero on every date, and 0 of 2,892 logons were
    network logons.** What remains is the student's choice among the four ways out. DC-01 alone
    is not enough; the stimulus must also make network logons. **Answer this before item 18.**

Item 18 — blocks data collection
    The key sees field presence, not value. Six of the eight class C hardening changes state a
    telemetry effect that is a value change, which the analyser cannot see. Only C4 and C6 are
    rate changes, and item 21 shows both of those need the missing domain. The planned capture
    (`RunAsPPL`, then read `GrantedAccess`) **cannot run as written**, found 2026-09-26: the
    pinned Sysmon config records no Event 10 at all, and `RunAsPPL = 1` writes a UEFI firmware
    variable. Decide first: an `lsass.exe` Sysmon rule or drop C3 and C8; and `RunAsPPL = 2`,
    a stated deviation, because CIS 18.9.27.2 (Windows 11 Enterprise v5.1.0) requires the lock.
    As configured today, **no class C change is measurable on this lab.**

Item 22 — blocks the harness design
    The stimulus is asserted identical across the two phases and never verified. A hardening
    change that makes an atomic test fail produces a rate drop the analyser reports as LOST.
    Per-atomic exit status and a stimulus fingerprint must go in the run manifest, because they
    cannot be reconstructed after the run.

Item 26 — blocks the harness design
    The harness's own `vmrun` guest calls most likely each write a batch logon (4624 type 4)
    inside the window: 2,285 across the archive, 1,641 on 2026-09-02. Unverified cause. The
    harness must count its calls and record the number.

Item 27 — the lab network, cause unknown
    The host's VMware adapters broke on their own twice, 2026-08-31 and before 2026-09-26.
    Repaired by hand. The pre-flight check and the harness must confirm VMnet2 holds
    `10.20.10.1` before any run.

Item 28 — boot-time evidence
    Events written before the Wazuh agent starts never reach the archive: zero 6005 and zero
    Wininit events on every date. Boot-time checks, such as Wininit event 12 for LSA
    protection, must be made inside the guest. Cause unverified.

Item 25 — the schedule, with a date on it
    The harness does not exist, the spike has never run, and 101 windows need about 67 hours
    unattended. Recommended tripwire, not yet accepted: if one full unattended capture window has
    not completed by **2026-09-22**, cut scope, for example to 8 changes, 53 windows, about 35
    hours. Also: 30 pre-change events over 3 runs is about 10 per run, so many keys may be
    untestable. The spike measures both.

Item 24 — blocks trusting any UNCHANGED result
    `VarianceModel.from_control()` accepts a control run that recorded nothing. That inflates
    every noise band and pushes real losses toward UNCHANGED. Found 2026-09-14, not fixed.

Item 23 — half fixed, half blocks a reported result
    The alpha half is fixed: `global_gate()` now takes the alpha passed to `analyse()`. Still
    open: the gate is the only stage with no noise model, so it may pass on run-to-run variation
    alone. Ten control pairs from the Phase 7 spike settle it.

Item 20 — blocks two headline claims
    WIN-EP-01 does not audit process creation. 200 process spawns produced zero `Security-4688`
    events, so the canonical event key example does not exist on this endpoint. Sysmon Event 1
    is carrying process creation instead.

Item 15 — blocks submission
    Which documents still carry the superseded event key. The `.docx` still embeds the
    2026-08-15 diagram, not either revised sheet.

Item 1 — blocks data collection
    The 16-change catalogue. Three control IDs verified, several still `(unverified)`.

Settled 2026-09-14, so do not reopen these
    The title is the panel's proposed wording, verbatim, with no article added (item 0). The system
    is a Python application with a graphical interface beside the SIEM, not a web application
    (item 17). The interface toolkit is not decided. Both in `REPO\docs\DECISIONS.md`.

Not an item yet — blocks the revisions list
    The REVISED-to-FINAL diff has never been run. Measured 2026-09-10: FINAL is 6,395 words
    against REVISED's 7,742. **Re-measure rather than quoting these.**


## 6. Built versus only designed

**Do not describe designed parts as if they exist.**

Built and tested, in `REPO\src\telos\`:
    `eventkey.py`, `variance.py`, `differential.py`, `baseline.py`, `report.py`, `model.py`,
    `synth.py`. Two test files in `REPO\tests\`, 55 tests passing.

Designed only, no code exists:
    the event-key to rule to ATT&CK dependency index, impact scoring, remediation candidate
    generation, all of Phase 5, and the capture harness that would drive Phases 0 to 3.

The lab:
    SIEM-01 and WIN-EP-01 exist. The runbook is partly executed. Read `REPO\docs\WORKLOG.md`
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

`pytest` should print `55 passed`. If it prints anything else, stop and tell me, because the
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

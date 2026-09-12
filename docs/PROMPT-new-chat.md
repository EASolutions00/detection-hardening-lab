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
   Items **0, 1, 15 to 18, and 20 to 23** are the live ones. All are summarised in section 5.
   Item 19 is answered. The file is ranked by damage, so read from the top.

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
    controller. `DC-01` is Tier B in `lab/blueprint.md` and was never built. Combined with item
    18 the measurable class C set is currently zero. One count against the existing archive
    settles it. **Answer this before item 18.**

Item 18 — blocks data collection
    The key sees field presence, not value. Six of the eight class C hardening changes state a
    telemetry effect that is a value change, which the analyser cannot see. Only C4 and C6 are
    rate changes, and item 21 shows both of those need the missing domain. One lab capture
    settles it: set `RunAsPPL = 1`, then read what `GrantedAccess` actually contains.

Item 22 — blocks the harness design
    The stimulus is asserted identical across the two phases and never verified. A hardening
    change that makes an atomic test fail produces a rate drop the analyser reports as LOST.
    Per-atomic exit status and a stimulus fingerprint must go in the run manifest, because they
    cannot be reconstructed after the run.

Item 23 — blocks a reported result
    `global_gate()` ignores the alpha passed to `analyse()`, and it is the only stage with no
    noise model, so it may pass on run-to-run variation alone. Ten control pairs from the Phase
    7 spike settle the second half. Fix with item 16, same function.

Item 20 — blocks two headline claims
    WIN-EP-01 does not audit process creation. 200 process spawns produced zero `Security-4688`
    events, so the canonical event key example does not exist on this endpoint. Sysmon Event 1
    is carrying process creation instead.

Item 17 — blocks on the adviser
    Three live documents state the system is a server-side web application. It is in no decision
    record and was never confirmed.

Item 16 — blocks a result-model change
    `global_gate()` returns not-passed for "no change" and for "could not test" alike, and both
    are reported as "no significant change".

Item 15 — blocks submission
    Which documents still carry the superseded event key. The `.docx` still embeds the
    2026-08-15 diagram, not either revised sheet.

Item 1 — blocks data collection
    The 16-change catalogue. Three control IDs verified, several still `(unverified)`.

Item 0 — blocks on the adviser
    Exact approved title wording, whether the article "a" is added.

Not an item yet — blocks the revisions list
    The REVISED-to-FINAL diff has never been run. Measured 2026-09-10: FINAL is 6,395 words
    against REVISED's 7,742. **Re-measure rather than quoting these.**


## 6. Built versus only designed

**Do not describe designed parts as if they exist.**

Built and tested, in `REPO\src\telos\`:
    `eventkey.py`, `variance.py`, `differential.py`, `baseline.py`, `report.py`, `model.py`,
    `synth.py`. Two test files in `REPO\tests\`, 49 tests passing.

Designed only, no code exists:
    the event-key to rule to ATT&CK dependency index, impact scoring, remediation candidate
    generation, all of Phase 5, and the capture harness that would drive Phases 0 to 3.

The lab:
    SIEM-01 and WIN-EP-01 exist. The runbook is partly executed. Read `REPO\docs\WORKLOG.md`
    for how far rather than assuming.

T3 is dead, killed 2026-08-19. If T1 fails its spike, go to T2.


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

`pytest` should print `49 passed`. If it prints anything else, stop and tell me, because the
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

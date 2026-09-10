# New chat prompt: the project map

Paste everything between the horizontal rules into a new chat. **It works from any folder.**
Every path in it is absolute, and it tells the model to read `CLAUDE.md` explicitly rather than
assuming the folder loaded it.

**This is a supplement, not a replacement.** `CLAUDE.md` carries the project summary, the four
answering rules, the commands, the rules that fail silently, the session habits and the defense
brief. **This file deliberately does not repeat any of that.** Two copies would drift, which is
the failure this project keeps having. It adds what `CLAUDE.md` has no room for: a routing table
from question to file, the settled numbers, the open items, and built versus only designed.

**Two things to know when pasting outside `E:\Claude general`:**

1. `CLAUDE.md` does **not** load on its own. Step 1 of the boot sequence reads it explicitly.
2. Reads outside the chat's working directory may need permission. The prompt tells the model to
   say so rather than guess.

**If you paste this where there is no filesystem** (a browser chat, a phone), nothing here can be
read. Paste the two `CLAUDE.md` files instead and expect narrower answers.

**Keep this current.** When an open item closes or a file moves, update it. A stale map is worse
than no map, because it gets trusted.

---

# Project map, supplement to CLAUDE.md

**Do not start any work.** This message exists so that when I ask something, you already know
where to look.

## 0. Paths, read this first

This chat may not be running inside the project folder, so every path below is absolute.

```
REPO = E:\Claude general
DOCS = E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)
```

Wherever you see `REPO\` or `DOCS\` below, **expand it to the full path above before reading.**

`REPO` is the git repository, public at `github.com/EASolutions00/detection-hardening-lab`.
`DOCS` is outside the repository and is not version controlled; the `.docx` files are assembled
there. `DOCS\prep-local\` holds defense preparation deliberately removed from the public repo on
2026-09-10. Do not propose putting it back.

**If a read is refused because the path is outside your working directory, tell me plainly.** I
will either grant access or reopen the chat in `REPO`. **Do not guess at file contents instead,
and do not answer from memory of this project.**

## 1. Boot sequence

Read these, in order. Expand `REPO` first.

1. `REPO\CLAUDE.md`. **This auto-loads only if the chat was opened in `REPO`. Otherwise read it
   explicitly.** It goes stale: four claims in it were wrong on 2026-09-10 and were corrected
   that day. **Treat it as a map, not as truth.**
2. `REPO\docs\OPEN-QUESTIONS.md`, **items 15 to 18**. These are the live ones.
3. `REPO\docs\DECISIONS.md`, the newest five entries.
4. `REPO\docs\WORKLOG.md`, the newest three entries.

Then run, exactly as written, so it works from any folder:

```
git -C "E:\Claude general" log --oneline -8
```

Then tell me in five lines: what is decided, what is blocked, what is next. Then stop and wait.

## 2. The map: where to look, by question type

| If I ask about | Read |
|---|---|
| **Why a choice was made**, or whether something is settled | `REPO\docs\DECISIONS.md` |
| **What is uncertain**, what might change the plan | `REPO\docs\OPEN-QUESTIONS.md` |
| **What happened, and when** | `REPO\docs\WORKLOG.md` newest first, plus `git log` |
| **A command that was run**, or what a correct result looks like | `REPO\docs\COMMANDS.md` |
| **Building the lab**, VMs, networking, phases | `REPO\docs\RUNBOOK-homelab.md` |
| **Lab design**, resource budget, the hardening catalogue | `REPO\lab\blueprint.md` |
| **The event key**, what is counted, field presence | `REPO\src\telos\eventkey.py` |
| **The statistics**: gate, rate ratio, correction, classification | `REPO\src\telos\differential.py` |
| **The noise floor**, coefficient of variation, dispersion | `REPO\src\telos\variance.py` |
| **The naive baseline** the method is measured against | `REPO\src\telos\baseline.py` |
| **Data shapes**: Phase, Finding, Classification | `REPO\src\telos\model.py` |
| **The activity diagram** | `REPO\thesis\T1\figures\make_activity_diagram.py`, which **is** the diagram |
| **The other three figures** | `REPO\thesis\T1\figures\` : `make_pipeline_figure.py`, `make_noise_floor_figure.py`, `svgkit.py` |
| **Proposal numbering and template rules** | `REPO\thesis\README.md` |
| **The diagram in plain words** | `DOCS\ACTIVITY-DIAGRAM-EXPLAINED.md` |
| **The proposal being submitted** | `DOCS\proposal-form-FINAL.md` |
| **Panel questions and the reasoning per answer** | `DOCS\T1-PANEL-RESPONSE.md` |
| **What changed after the title defense** | `DOCS\T1-REVISIONS-LIST.md` |
| **Whether documents contradict the code** | `REPO\tools\check_docs.py`, see section 7 |

## 3. Authority order, when two sources disagree

1. **The code** in `REPO\src\telos\`. What is actually built.
2. **`REPO\docs\DECISIONS.md`.** What was decided, and why.
3. **`DOCS\proposal-form-FINAL.md`.** What will be submitted.
4. Everything else is explanatory and loses.

**A document is never evidence about another document.**

## 4. Settled numbers, so you start from the right place

Verify any you rely on. Listed so you do not re-derive them every session. All files below are
in `REPO\src\telos\` unless stated.

| Fact | Where |
|---|---|
| An event key is `Source-EventID[PopulatedField,...]`, e.g. `Security-4688[CommandLine,NewProcessName]` | `eventkey.py` |
| The key records **that** a tracked field carried a value, never **which** value | `eventkey.py`, `is_populated()` |
| Empty, `-`, `N/A`, `(null)`, `NULL` are absent. **Numeric zero is present** | `eventkey.py` |
| Chi-square runs **once** over the whole 2 by K profile, never per key | `differential.py`, `global_gate()` |
| Classification order is **NEW, then INCONCLUSIVE, then LOST** | `differential.py`, `_test_key()` |
| LOST requires the post-change count to be **exactly zero** | `differential.py` |
| REDUCED needs all three: `q <= 0.05`, `RR <= 0.5`, `(1 - RR) > 3 * CoV` | `differential.py`, `classify()` |
| The noise floor comparison is **exceed**, not "below" | `differential.py` |
| `ALPHA=0.05`, `MAX_RATIO=0.5`, `MIN_PRE_COUNT=30`, `NOISE_SIGMAS=3.0` | `differential.py` |
| Rate is count divided by **number of runs**, not per unit time | `differential.py` |
| Dispersion is floored at 1.0 | `variance.py` |
| Field-loss pairing matches a LOST key to a NEW key of the same event type whose field set is a strict subset | `eventkey.py`, `field_loss_pairs()` |
| 16 changes, 5 control runs, 3 pre and 3 post per change | `REPO\lab\blueprint.md` |

### Facts that get stated wrong, including by me

- **Event 4104 is PowerShell script block logging**, in
  `Microsoft-Windows-PowerShell/Operational`. **Not** the Security log.
- **Event 4688 carries `ParentProcessName`.** `ParentImage` is a Sysmon field.
- **Rate is per run, not per minute.**
- **Figures are generated, not drawn.** Edit the generator, re-run, then **render it and look.**
  Two real defects here were caught only by looking at the picture.

## 5. Open, so do not state these as settled

| Item | What is open | Blocks |
|---|---|---|
| **18** | The key sees field presence, not value. **Six of the eight class C changes state a telemetry effect that is a value change**, which the analyser cannot see. Only C4 and C6 are rate changes. One capture settles it: `RunAsPPL = 1`, then read `GrantedAccess` | Data collection |
| **17** | Three live documents say the system is a server-side web application. In no decision record, never confirmed | The adviser |
| **16** | `global_gate()` returns not-passed for "no change" and "could not test" alike, and reports both as "no significant change" | A result-model change |
| **15** | Which documents still carry the superseded event key. The `.docx` still embeds the 2026-08-15 diagram | Submission |
| **1** | The 16-change catalogue. Three control IDs verified, several still `(unverified)` | Data collection |
| **0** | Exact approved title wording, whether the article "a" is added | The adviser |
| not an item | The REVISED-to-FINAL diff has never run. Measured 2026-09-10: FINAL 6,395 words, REVISED 7,742. **Re-measure rather than quoting these** | The revisions list |

## 6. Built versus only designed

**Do not describe designed parts as if they exist.**

**Built and tested:** in `REPO\src\telos\` : `eventkey.py`, `variance.py`, `differential.py`,
`baseline.py`, `report.py`, `model.py`, `synth.py`. Two test files in `REPO\tests\`, 49 tests.

**Designed only:** the event-key to rule to ATT&CK dependency index, impact scoring, remediation
candidate generation, all of Phase 5, and the capture harness that would drive Phases 0 to 3.

**The lab:** SIEM-01 and WIN-EP-01 exist. The runbook is partly executed. Read
`REPO\docs\WORKLOG.md` for how far rather than assuming.

**T3 is dead**, killed 2026-08-19. If T1 fails its spike, go to T2.

## 7. Commands that work from any folder

Copy these literally. **No `cd` is needed and no shell-specific syntax is used.** All four were
tested from an unrelated directory on 2026-09-10 and work unchanged.

```
git -C "E:\Claude general" log --oneline -8

"E:\Claude general\.venv\Scripts\python.exe" -m pytest "E:\Claude general\tests" -q

"E:\Claude general\.venv\Scripts\python.exe" "E:\Claude general\tools\check_docs.py" "E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)"

"E:\Claude general\.venv\Scripts\python.exe" "E:\Claude general\thesis\T1\figures\make_activity_diagram.py"
```

In PowerShell a quoted command needs the call operator, so write `& "E:\Claude general\.venv\...`
for the last three. In cmd or bash the quotes alone are enough.

`pytest` should print `49 passed`. If it prints anything else, stop and tell me, because the
record is stale.

`check_docs.py` flags statements in any document that contradict the code. **It flags, it does
not judge.** A hit is a question. File status decides whether it matters: FROZEN files are the
version the panel read, so old wording there is **correct**. It produces false positives on
purpose, for example a sentence explaining why chi-square is *not* per event type.

The diagram generator writes two SVG files. **Then render them and look.**

**Never run** `git-filter-repo`, a force push, or any history rewrite without asking me first.

## 8. Answering, beyond what CLAUDE.md already says

1. **Answer the question I asked, then add what I will need next.** Do not make me ask three
   follow-ups to get a complete answer.
2. **When I question something, do not change it on contact.** Verify at the source, show me the
   evidence, say plainly whether you were wrong or right, then propose. My question is not proof
   you were wrong.
3. **When you do not know, say so**, then name the file that would answer it and offer to read
   it. Do not fill a gap with something plausible.

---

Now do the boot sequence in section 1, give me the five lines, then wait for my question.

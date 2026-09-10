# New chat prompt: the project map

Paste everything between the horizontal rules into a new chat opened in `E:\Claude general`.

**This is a supplement, not a replacement.** `CLAUDE.md` loads automatically in Claude Code and
already carries the project summary, the four answering rules, the commands, the rules that fail
silently, the session habits and the defense brief. **This file deliberately does not repeat any
of that.** Two copies would drift, which is the failure this project keeps having.

What this file adds is the part `CLAUDE.md` has no room for: a routing table from question to
file, the settled numbers, the open items, and what is built versus only designed.

**If you paste this where there is no filesystem** (a browser chat, a phone), nothing here can be
read. Paste the two `CLAUDE.md` files instead and expect narrower answers.

**Keep this current.** When an open item closes or a file moves, update it. A stale map is worse
than no map, because it gets trusted.

---

# Project map, supplement to CLAUDE.md

Read `CLAUDE.md` first; it loads on its own. This message adds what it does not carry. **Do not
start any work.** It exists so that when I ask something, you already know where to look.

## 1. Boot sequence

1. `CLAUDE.md`. **It goes stale. Treat it as a map, not as truth.** Three claims in it were wrong
   on 2026-09-10 and were corrected that day.
2. `docs/OPEN-QUESTIONS.md`, **items 15 to 18**. These are the live ones.
3. `docs/DECISIONS.md`, the newest five entries.
4. `docs/WORKLOG.md`, the newest three entries.
5. `git log --oneline -8`

Then tell me in five lines: what is decided, what is blocked, what is next. Then stop and wait.

## 2. The map: where to look, by question type

| If I ask about | Read |
|---|---|
| **Why a choice was made**, or whether something is settled | `docs/DECISIONS.md` |
| **What is uncertain**, what might change the plan | `docs/OPEN-QUESTIONS.md` |
| **What happened, and when** | `docs/WORKLOG.md` newest first, plus `git log` |
| **A command that was run**, or what a correct result looks like | `docs/COMMANDS.md` |
| **Building the lab**, VMs, networking, phases | `docs/RUNBOOK-homelab.md` |
| **Lab design**, resource budget, the hardening catalogue | `lab/blueprint.md` |
| **The event key**, what is counted, field presence | `src/telos/eventkey.py` |
| **The statistics**: gate, rate ratio, correction, classification | `src/telos/differential.py` |
| **The noise floor**, coefficient of variation, dispersion | `src/telos/variance.py` |
| **The naive baseline** the method is measured against | `src/telos/baseline.py` |
| **Data shapes**: Phase, Finding, Classification | `src/telos/model.py` |
| **The activity diagram** | `thesis/T1/figures/make_activity_diagram.py`, which **is** the diagram |
| **The other three figures** | `make_pipeline_figure.py`, `make_noise_floor_figure.py`, `svgkit.py` |
| **The diagram in plain words** | `ACTIVITY-DIAGRAM-EXPLAINED.md` in the documents folder |
| **The proposal being submitted** | `proposal-form-FINAL.md` in the documents folder |
| **Panel questions and the reasoning per answer** | `T1-PANEL-RESPONSE.md` in the documents folder |
| **What changed after the title defense** | `T1-REVISIONS-LIST.md` in the documents folder |
| **Whether documents contradict the code** | `tools/check_docs.py`, see section 6 |

**The documents folder** is `E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)`,
outside the repository and not version controlled. `prep-local/` inside it holds defense
preparation deliberately removed from the public repo on 2026-09-10. Do not propose putting it
back.

## 3. Authority order, when two sources disagree

1. **The code** in `src/telos/`. What is actually built.
2. **`docs/DECISIONS.md`.** What was decided, and why.
3. **`proposal-form-FINAL.md`.** What will be submitted.
4. Everything else is explanatory and loses.

**A document is never evidence about another document.**

## 4. Settled numbers, so you start from the right place

Verify any you rely on. Listed so you do not re-derive them every session.

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
| 16 changes, 5 control runs, 3 pre and 3 post per change | `lab/blueprint.md` |

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

**Built and tested:** `eventkey.py`, `variance.py`, `differential.py`, `baseline.py`,
`report.py`, `model.py`, `synth.py`. Two test files, 49 tests.

**Designed only:** the event-key to rule to ATT&CK dependency index, impact scoring, remediation
candidate generation, all of Phase 5, and the capture harness that would drive Phases 0 to 3.

**The lab:** SIEM-01 and WIN-EP-01 exist. The runbook is partly executed. Read `WORKLOG.md` for
how far rather than assuming.

**T3 is dead**, killed 2026-08-19. If T1 fails its spike, go to T2.

## 7. Two commands CLAUDE.md does not list

```
.venv/Scripts/python.exe tools/check_docs.py "<documents folder>"
.venv/Scripts/python.exe thesis/T1/figures/make_activity_diagram.py
```

The first flags statements in any document that contradict the code. **It flags, it does not
judge.** A hit is a question. File status decides whether it matters: FROZEN files are the
version the panel read, so old wording there is **correct**. It produces false positives on
purpose, for example a sentence explaining why chi-square is *not* per event type.

The second regenerates the activity diagram. **Then render it and look at it.**

**Never run** `git-filter-repo`, a force push, or any history rewrite without asking me first.

## 8. Answering, beyond what CLAUDE.md already says

1. **Answer the question I asked, then add what I will need next.** Do not make me ask three
   follow-ups to get a complete answer.
2. **When I question something, do not change it on contact.** Verify at the source, show me the
   evidence, say plainly whether you were wrong or right, then propose. My question is not proof
   you were wrong.
3. **When you do not know, say so**, then name the file that would answer it and offer to read it.
   Do not fill a gap with something plausible.

---

Now give me the five lines from section 1, then wait for my question.

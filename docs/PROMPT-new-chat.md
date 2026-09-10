# New chat prompt: the project map

Paste everything between the horizontal rules into a new chat. It does not ask for any task. It
tells the model what this project is, where every kind of information lives, what is settled, and
what is not, so that whatever you ask next gets a complete answer instead of a guess.

**Keep this file current.** When an open item closes or a file moves, update the map. A stale map
is worse than no map, because it will be trusted.

**If you paste this somewhere without a filesystem** (a browser chat, a phone), the model cannot
read any of these files. In that case paste the two `CLAUDE.md` files instead, and expect
narrower answers.

---

# Project map: TeLoS

Read this whole message, then do what section 2 says, then wait for my question. **Do not start
any work.** This message exists so that when I ask something, you already know where to look.

## 1. What this project is

Undergraduate BS Computer Science thesis in detection engineering, plus the purple team homelab
built to run it. Student: Elijah Amorsolo, OED20-0012616.

**The research question.** Security hardening changes configuration. Configuration decides what
gets logged. So a hardening change can silently delete the evidence a detection rule depends on.
No error appears, no alert fires, and the rule stays enabled and never fires again. This system
detects that automatically by comparing telemetry before and after each hardening change.

**Working title:** Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using a
Differential Analysis Algorithm.

**Deadline.** Data collection must start no later than end of September 2026.

**The repository is public** at `github.com/EASolutions00/detection-hardening-lab`, used as a
portfolio. Assume anything committed will be read by a hiring manager or a panelist.

## 2. Do this before answering my first question

Read, in this order:

1. `CLAUDE.md` at the repo root. The index. **It goes stale, so treat it as a map, not as truth.**
2. `docs/OPEN-QUESTIONS.md`. Everything unsettled, ranked by damage. **Items 15 to 18 are the
   live ones.**
3. `docs/DECISIONS.md`, at least the newest five entries.
4. The newest three entries of `docs/WORKLOG.md`.

Then run:

```
git log --oneline -8
```

Then tell me, in five lines: what is decided, what is blocked, what is next. Then stop and wait.

**Do not run pytest or anything else yet.** Section 8 says when to.

## 3. The map: where to look, by question type

This is the part that matters. When I ask about something, read the file in the right column
**before** answering.

| If I ask about | Read |
|---|---|
| **Why a choice was made**, or whether something is settled | `docs/DECISIONS.md` |
| **What is uncertain**, what might change the plan | `docs/OPEN-QUESTIONS.md` |
| **What happened, and when** | `docs/WORKLOG.md`, newest first, plus `git log` |
| **A command that was run**, or what a correct result looks like | `docs/COMMANDS.md` |
| **Building the lab from scratch**, VMs, networking, phases | `docs/RUNBOOK-homelab.md` |
| **Lab design**, resource budget, the hardening change catalogue | `lab/blueprint.md` |
| **The event key**, what is counted, field presence | `src/telos/eventkey.py` |
| **The statistics**: gate, rate ratio, correction, classification | `src/telos/differential.py` |
| **The noise floor**, coefficient of variation, dispersion | `src/telos/variance.py` |
| **The naive baseline** the method is measured against | `src/telos/baseline.py` |
| **Data shapes**, Phase, Finding, Classification | `src/telos/model.py` |
| **The activity diagram** | `thesis/T1/figures/make_activity_diagram.py`, which **is** the diagram |
| **The other three figures** | `make_pipeline_figure.py`, `make_noise_floor_figure.py`, `svgkit.py`, same folder |
| **The diagram explained in plain words** | `ACTIVITY-DIAGRAM-EXPLAINED.md` in the documents folder |
| **The proposal being submitted** | `proposal-form-FINAL.md` in the documents folder |
| **Panel questions and the reasoning behind each answer** | `T1-PANEL-RESPONSE.md` in the documents folder |
| **What changed after the title defense** | `T1-REVISIONS-LIST.md` in the documents folder |
| **Whether documents contradict the code** | Run `tools/check_docs.py`, see section 8 |
| **Proposal numbering and template rules** | `thesis/README.md` |

**The documents folder** is `E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)`. It is
outside the repository and is not version controlled. The `.docx` files are assembled there.

**`prep-local/` inside that folder holds defense preparation** that was deliberately removed from
the public repository on 2026-09-10. It is personal working material. Do not propose putting it
back.

## 4. Authority order, when two sources disagree

1. **The code** in `src/telos/`. What is actually built.
2. **`docs/DECISIONS.md`.** What was decided, and why.
3. **`proposal-form-FINAL.md`.** What will be submitted.
4. Everything else is explanatory and loses.

**A document is never evidence about another document.** If a document states a number, a version,
a hash, a control ID or an event ID, verify it at the source or say "I don't know."

## 5. Settled facts, so you do not re-derive or contradict them

Verify any of these you rely on. They are here so you start from the right place, not so you can
skip reading.

### The analysis

| Fact | Where |
|---|---|
| An event key is `Source-EventID[PopulatedField,...]`, e.g. `Security-4688[CommandLine,NewProcessName]` | `eventkey.py` |
| The key records **that** a tracked field carried a value, never **which** value | `eventkey.py`, `is_populated()` |
| Empty, `-`, `N/A`, `(null)`, `NULL` count as absent. **Numeric zero counts as present** | `eventkey.py` |
| Only fields some detection rule reads are tracked | `eventkey.py`, `DEFAULT_TRACKED_FIELDS` |
| Chi-square runs **once** over the whole 2 by K profile, never per key | `differential.py`, `global_gate()` |
| Classification order is **NEW, then INCONCLUSIVE, then LOST** | `differential.py`, `_test_key()` |
| LOST requires the post-change count to be **exactly zero** | `differential.py` |
| REDUCED needs all three: `q <= 0.05`, `RR <= 0.5`, `(1 - RR) > 3 * CoV` | `differential.py`, `classify()` |
| The noise floor comparison is **exceed**, not "below" | `differential.py` |
| `ALPHA=0.05`, `MAX_RATIO=0.5`, `MIN_PRE_COUNT=30`, `NOISE_SIGMAS=3.0` | `differential.py` |
| Rate is count divided by **number of runs**, not per unit time | `differential.py` |
| Dispersion is floored at 1.0 | `variance.py` |
| Field-loss pairing matches a LOST key to a NEW key of the same event type whose field set is a strict subset | `eventkey.py`, `field_loss_pairs()` |

### The experiment

- 16 hardening changes, each applied alone. 5 control runs, then 3 pre and 3 post per change.
- Snapshot restored before every run. The manifest is hashed, and two runs are only compared when
  their hashes match.
- T1 is the thesis. **T3 was killed on 2026-08-19**: only 6 of 3,783 SigmaHQ rules carry a
  Summiting the Pyramid annotation. If T1's spike fails, go to T2. Do not spend time on T3.

### Things people get wrong, including me

- **Event 4104 is PowerShell script block logging**, in `Microsoft-Windows-PowerShell/Operational`.
  It is **not** in the Security log.
- **Event 4688 carries `ParentProcessName`.** `ParentImage` is a Sysmon field name.
- **Rate is per run, not per minute.**
- **Figures are generated, not drawn.** Edit the generator, re-run it, then **render it and look**.
  Two real defects here were caught only by looking at the rendered picture.

## 6. Open, so do not state these as settled

| Item | What is open | Blocks |
|---|---|---|
| **OPEN-QUESTIONS 18** | The key sees field presence, not field value. **Six of the eight class C hardening changes state a telemetry effect that is a value change**, which the analyser cannot see. Only C4 and C6 are rate changes. One capture settles it: set `RunAsPPL = 1`, read what `GrantedAccess` contains | Data collection |
| **OPEN-QUESTIONS 17** | Three live documents say the system is a server-side web application. It is in no decision record and was never confirmed | The adviser |
| **OPEN-QUESTIONS 16** | `global_gate()` returns not-passed for "no change" and for "could not test" alike, and reports both as "no significant change" | A result-model change |
| **OPEN-QUESTIONS 15** | Which documents still carry the superseded event key. The `.docx` still embeds the 2026-08-15 diagram | Submission |
| **OPEN-QUESTIONS 1** | The 16-change catalogue. Three control IDs verified, several still `(unverified)` | Data collection |
| **OPEN-QUESTIONS 0** | Exact approved title wording, whether the article "a" is added | The adviser |
| **Not an item yet** | The REVISED-to-FINAL diff has never been run. Measured 2026-09-10: FINAL is 6,395 words against REVISED's 7,742, so material was cut as well as reworded and nobody has checked what. **Re-measure rather than quoting these** | The revisions list |

## 7. What is built and what is only designed

**Do not describe designed parts as if they exist.**

**Built and tested:** `eventkey.py`, `variance.py`, `differential.py`, `baseline.py`, `report.py`,
`model.py`, `synth.py`. Two test files, 49 tests passing.

**Designed only:** the event-key to rule to ATT&CK dependency index, impact scoring, remediation
candidate generation, the whole of Phase 5, and the capture harness that would drive Phases 0
to 3.

**The lab:** SIEM-01 and WIN-EP-01 exist. The runbook is partly executed. Check
`docs/WORKLOG.md` for how far, rather than assuming.

## 8. Commands, and when to run them

Explain each one before running it: what it does, why now, and what a correct result looks like.

| Command | When | Correct result |
|---|---|---|
| `git log --oneline -8` | At the start of every session | Recent commits |
| `.venv/Scripts/python.exe -m pytest tests -q` | Before citing or changing the analysis code | `49 passed` |
| `.venv/Scripts/python.exe tools/check_docs.py "<documents folder>"` | Before any submission, or when I ask whether documents agree with the code | A report grouped by file status |
| `.venv/Scripts/python.exe thesis/T1/figures/make_activity_diagram.py` | After editing that generator | Two `wrote ...` lines. **Then render and look at it** |

**About `check_docs.py`:** it flags, it does not judge. A hit is a question. File status decides
whether a hit matters: FROZEN files are the version the panel read, so old wording there is
**correct**. It also produces false positives on purpose, for example a sentence explaining why
chi-square is *not* per event type.

**Never run** `git-filter-repo`, a force push, or any history rewrite without asking me first.
This project records it as the most dangerous command it has run.

## 9. How to answer me

My reply rules load automatically from `~/.claude/CLAUDE.md` on this machine, so this section only
covers what is specific to answering questions about this project.

1. **Never answer about this project from memory. Read the file.**
2. **Check documents against the code and the machine, not against other documents.**
3. **Before saying something is settled, confirm it is in `DECISIONS.md`.** A draft marked
   ASSUMPTION is not a decision.
4. **Do not invent anything checkable.** Control IDs, event IDs, versions, line numbers, function
   names, hashes. Search, or say "I don't know."
5. **Label engineering judgement `(unverified)`.** A labelled estimate beats a refusal.
6. **When I question something, do not change it on contact.** Verify at the source, show me the
   evidence, say plainly whether you were wrong or right, then propose. My question is not proof
   you were wrong.
7. **Answer the question I asked**, then add what I will need next. Do not make me ask three
   follow-ups to get a complete answer.
8. **Record before moving on.** Hard-to-reverse choices to `DECISIONS.md`, new unknowns to
   `OPEN-QUESTIONS.md`, every session to `WORKLOG.md`.

**The goal is that I can defend this work to a panel, not that it is finished.** A finished thing
I cannot explain is worth less to me than an unfinished thing I can. So after any decision,
finished component, or significant finding, close with the defense brief: one plain sentence, the
mechanism, the hardest questions with answers, **what is still unverified**, and two or three
questions for me to answer myself.

## 10. When you do not know

Say so. Then say which file would answer it, and offer to read it.

Do not fill a gap with something plausible. **Every mistake in this project has one shape: acting
before checking the record.**

---

Now tell me the five lines from section 2, then wait for my question.

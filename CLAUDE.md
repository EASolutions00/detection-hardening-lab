# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Index only. It points at the detail, it does not hold it.**

---

## What this is

Undergraduate BS Computer Science thesis in detection engineering, plus the purple team
homelab built to run it. Student: Elijah Amorsolo, OED20-0012616.

T1, T2 and T3 are **alternatives, not components.** One gets built. T1 is the primary choice
and is gated behind a feasibility spike that has not run yet. Data collection must start no
later than end of September 2026.

---

## Where everything lives

| Path | What is in it |
|---|---|
| [docs/RUNBOOK-homelab.md](docs/RUNBOOK-homelab.md) | **Build the lab from scratch.** 8 phases, each ends with a check. |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Why choices were made. Pinned versions. Spike results. |
| [docs/WORKLOG.md](docs/WORKLOG.md) | What happened each session, newest first. |
| [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) | Unverified things that change the plan. Ranked. |
| [docs/COMMANDS.md](docs/COMMANDS.md) | Every command run on this machine, why, and what a correct result looks like. Has the pre-flight check. |
| [thesis/](thesis/README.md) | Proposal template and numbering rules. |
| [thesis/T1/](thesis/T1/README.md) | Hardening-induced blind spots. Primary. |
| [thesis/T2/](thesis/T2/README.md) | Severity inversion in the Wazuh ruleset. Second fallback. |
| [thesis/T3/](thesis/T3/README.md) | Analytic robustness scoring. **Dead, killed 2026-08-19.** Kept as a record. |
| [lab/blueprint.md](lab/blueprint.md) | Lab design, resource budget, go/no-go analysis. |
| [lab/configs/](lab/configs/README.md) | Pinned Sysmon and Wazuh configs. Hash them. |
| [lab/scripts/](lab/scripts/README.md) | One script per hardening change. Not snapshots. |
| [src/](src/README.md) | Python package `telos`. Analysis core built: 8 modules, 49 tests passing. |
| `data/runs/` | Raw archives. Gitignored, too big for GitHub. One disk only, so back up elsewhere. |
| `data/summaries/` | Small derived CSVs. Committed. |

---

## Before answering anything about this project

Read `docs/OPEN-QUESTIONS.md` and `docs/DECISIONS.md` before writing, building, or advising.
Not after. Four rules, each written because breaking it caused a real error here.

**1. Never answer from memory. Read the file.**
This index goes stale. On 2026-09-08 it still claimed no code existed while 49 tests were
passing, and still named T3 as the fallback three weeks after T3 was killed. **Treat this file
as a map, not as truth.** The truth is in the file it points at.

**2. Check documents against the code and the machine, not against other documents.**
`T1-REVISIONS-LIST.md` described the event key as using field *values*. The code uses field
*presence*. Reading only documents would have confirmed the error. A `grep` of
`differential.py` found it. **If a document states a number, a version, or a hash, verify it
at the source.**

**3. Before stating anything as settled, confirm it appears in `DECISIONS.md`.**
The web-application deployment was marked ASSUMPTION four times in a draft, never confirmed,
never tracked in OPEN-QUESTIONS, and then written into a submission document as fact. **A draft
marked ASSUMPTION is not a decision.** If it is not in `DECISIONS.md`, say so.

**4. Do not invent anything checkable.**
Control IDs, versions, hashes, commit IDs, file paths, event IDs. Search, or say "I don't
know." A wrong CIS or DISA control ID is worse than none, because the entire value of a control
ID is that an examiner can look it up.

**The failure these prevent has one shape: acting before checking the record.** Every mistake
made in this project so far fits it. `docs/T1-WALKTHROUGH.md` was written around a hardening
change that OPEN-QUESTIONS had already disproved nineteen days earlier. Two WORKLOG entries
were dated from file timestamps instead of `git log` and were wrong by a day.

**Where uncertainty goes:** `OPEN-QUESTIONS.md`, not a comment in a draft. An unknown recorded
only inside a document nobody rereads will be forgotten and then asserted as fact.

---

## Commands

```bash
.venv/Scripts/python.exe src/demo.py          # end to end on synthetic data
.venv/Scripts/python.exe -m pytest tests -q   # expect: 49 passed
```

Stack pinned in `requirements.txt`: numpy 2.5.2, scipy 1.18.1, pandas 3.0.5, PyYAML 6.0.3,
pytest 9.1.1. Do not upgrade mid-experiment. See [src/](src/README.md).

The pre-flight check before any runbook phase is in
[docs/COMMANDS.md](docs/COMMANDS.md) Part 5.

---

## Rules that fail silently

Breaking these produces no error, just wrong results. The reasons are in the runbook.

1. **No VM ever runs from E:.** It is a hard disk. VMs live on F:. (Phase 0)
2. **Pin every version and record it before the golden snapshot.** Wazuh, Sysmon binary and
   config hash, Atomic Red Team commit, Windows build, harness commit. A later bump discards
   every earlier run. (Phase 4, table in DECISIONS.md)
3. **`<logall_json>yes</logall_json>` in `ossec.conf`.** T1 counts what the machine emits, not
   what alerted. (Phase 2)
4. **Golden snapshot is taken with NAT disconnected.** (Phase 5)
5. **Fence capture windows in telemetry, not host clock.** Settle 180 s after boot, drain
   120 s after the suite. (Phase 6)

---

## The open decision

T1 is **approved** and is the thesis. The spike measuring run-to-run variance and real wall
clock has still not run. See [runbook Phase 7](docs/RUNBOOK-homelab.md).

**T3 is dead as a fallback**, killed 2026-08-19: only 6 of 3,783 SigmaHQ rules carry an STP
annotation, too few for the agreement statistic its evaluation depended on. Evidence in
OPEN-QUESTIONS, Answered. **If the spike fails, go to T2. Do not spend time reviving T3.**

The live blocker is **OPEN-QUESTIONS item 18**: six of the eight class C hardening changes
state a telemetry effect that is a *value change*, and the analyser records which fields were
**populated**, not what they contained. Only C4 and C6 are rate changes. One lab capture settles
it: set `RunAsPPL = 1` and read what `GrantedAccess` actually holds afterwards.

Item 1, the catalogue, was rebuilt on 2026-09-08 and is no longer the blocker. Item 17, the
unconfirmed web-application claim, is blocked on the adviser.

---

## Conventions

- **Proposals follow a fixed institutional template.** Preserve the structure and the
  problem-to-objective numbering. See [thesis/README.md](thesis/README.md).
- **Sourcing.** Engineering judgment is marked `(unverified)` inline. Numbers, dates, and any
  claim the reader may act on carry a source link or full reference.
- **Do not soften the falsifiable claims.** T1 and T3 pre-declare the result that would prove
  them wrong. That is deliberate and it is the main defense against the sharpest panel
  objection.
- **Replies.** The user's reply rules load automatically from `~/.claude/CLAUDE.md` on the
  user's machine. That file is private and is kept out of this repo on purpose. It is not
  backed up here, so if it is lost, ask the user for it again.

---

## The work must be defensible, not just finished

This is a thesis. It gets defended to a panel that can ask anything, including indirect and
hostile questions. **A finished component the student cannot explain is worth less than an
unfinished one they can.**

So every piece of work here carries a second deliverable: the explanation.

- After building or deciding anything, state what now has to be explainable, in plain words.
- Name the hardest question an examiner would ask about it, and answer it.
- Where a faster approach is harder to defend, say so and let the choice be made deliberately.
- Flag plainly when something is being accepted that cannot yet be defended, or when a result
  is being relied on that was never seen produced.
- Prefer walking through over doing silently. Say which is happening.

This is why a real test run comes before the proposal revision is submitted: understanding the
system beats describing it.

### Explaining this project

The reply rules cover how to write. This is what to watch for **here**.

**These terms are explained in plain words the first time they appear in a reply, or they are
not used.** Each one has caused real confusion in this project:

> chi-square gate, coefficient of variation, dispersion, rate ratio, false discovery rate,
> Benjamini-Hochberg, q value, event key, field presence, noise floor, manifest hash,
> snapshot restore, confound.

**Prefer a real number from this project over an abstract description.** "1247 events became 0"
is clearer than "the telemetry was lost". The numbers are in `WORKLOG.md` and the test files.

**Say which layer you are answering at**, because the same question has three honest answers:
what the code does today, what the design says, and what a real deployment would need. Mixing
them is the fastest way to confuse a reader. See "built versus only designed" in
[docs/PROMPT-new-chat.md](docs/PROMPT-new-chat.md).

### The defense brief

After any design decision, finished component, completed phase, or significant finding, close
with this shape. Not after routine commands. Scale it to the size of the work.

1. **One sentence.** What the student would say if asked casually, no jargon.
2. **The mechanism.** Two to four points behind that sentence. Why it works, not just what it does.
3. **Hard questions.** Three to five of the sharpest an examiner could ask, each answered.
   Include the one attacking the weakest part, and say when to raise it first.
4. **Unverified.** What is being relied on that nobody has seen proven, and the check that
   would prove it. **Never skip this part.**
5. **Explain it back.** Two or three questions with no answers shown, so gaps surface early.

## Session habits

Recorded, not remembered.

- **Append to [WORKLOG.md](docs/WORKLOG.md) every session.** Include what broke, with the
  error text. A failed attempt recorded beats a clean summary later.
- **Hard to reverse choices go in [DECISIONS.md](docs/DECISIONS.md)** with the reason and the
  cost if wrong. Never delete an entry, supersede it.
- **Answered unknowns move to the Answered section** of OPEN-QUESTIONS.md with the evidence.
- Pinned versions and spike results are tables in DECISIONS.md. Fill them in as you go.

## When a runbook phase finishes

Every time a Phase in [docs/RUNBOOK-homelab.md](docs/RUNBOOK-homelab.md) is completed, do all
of this before starting the next phase. Do not skip it because the phase felt small.

1. **WORKLOG.md (always).** Add an entry: which phase, what was done, the results, and anything
   that broke with its exact error text.
2. **DECISIONS.md (if a choice was made).** Record any hard-to-reverse choice or any pinned
   value set during the phase, with the reason and the cost if wrong.
3. **OPEN-QUESTIONS.md (if it applies).** Move any answered question to the Answered section
   with evidence. Add any new unknown the phase revealed.
4. **Fill the pinned-versions table in DECISIONS.md** if the phase produced a version or hash
   to pin (Phase 4 especially).
5. **Commit and push.** So the record is on GitHub, not on one disk only.

The record is the point, not the memory.

---

## Git

**Live and public** at https://github.com/EASolutions00/detection-hardening-lab
The professor confirmed no IP rule and no similarity-check problem. Reason and cost are in
[DECISIONS.md](docs/DECISIONS.md). `gh` is installed and logged in as EASolutions00, so
`git push` and `gh` commands work directly.

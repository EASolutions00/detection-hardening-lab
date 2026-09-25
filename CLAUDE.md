# CLAUDE.md (project: detection-hardening-lab)

**Index only. It points at the detail, it does not hold it.**
Status changes every week, so it lives in `docs/STATUS.md`, not here.

---

## What this is

Undergraduate BS Computer Science thesis in detection engineering, plus the purple team
homelab built to run it. Student: Elijah Amorsolo, OED20-0012616.

T1, T2 and T3 are **alternatives, not components.** One gets built.
- **T1** is approved and is the thesis. **It is final, and there is no fallback**
  (DECISIONS.md 2026-09-26). It is gated behind a feasibility spike (runbook Phase 7) that
  measures run-to-run variance and real wall clock. If the spike shows T1 cannot finish in
  time, the answer is a scope cut (OPEN-QUESTIONS 25), not a different topic.
- **T2 and T3 were not chosen.** Kept as a record only. T3 lost its fallback status on
  2026-08-19. Do not spend time on either.

---

## Where everything lives

| Path | What is in it |
|---|---|
| [docs/STATUS.md](docs/STATUS.md) | **Current blockers and dates.** Read first. |
| [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) | Unverified things that change the plan. Ranked. |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Why choices were made. Pinned versions. Spike results. |
| [docs/WORKLOG.md](docs/WORKLOG.md) | What happened each session, newest first. |
| [docs/RUNBOOK-homelab.md](docs/RUNBOOK-homelab.md) | Build the lab from scratch. Phases 0 to 8, each ends with a check. |
| [docs/COMMANDS.md](docs/COMMANDS.md) | Every command run on this machine, why, and the correct result. Part 5 is the pre-flight check. |
| [thesis/](thesis/README.md) | Proposal template and numbering rules. |
| [thesis/T1/](thesis/T1/README.md) | Hardening-induced blind spots. The thesis. Final. |
| [thesis/T2/](thesis/T2/README.md) | Severity inversion in the Wazuh ruleset. Not chosen. Record only. |
| [thesis/T3/](thesis/T3/README.md) | Analytic robustness scoring. Not chosen. Record only. |
| [lab/blueprint.md](lab/blueprint.md) | Lab design, resource budget, go/no-go analysis. |
| [lab/configs/](lab/configs/README.md) | Pinned Sysmon and Wazuh configs. Hash them. |
| [lab/scripts/](lab/scripts/README.md) | One script per hardening change. Not snapshots. |
| [src/](src/README.md) | Python package `telos`, the analysis core. |
| `data/runs/` | Raw archives. Gitignored, too big for GitHub. One disk only, so back up elsewhere. |
| `data/summaries/` | Small derived CSVs. Committed. |

---

## Read the record before answering

Before writing, building, or advising, read `docs/STATUS.md`, `docs/OPEN-QUESTIONS.md`,
and `docs/DECISIONS.md`. Not after.

Every mistake in this project so far had one shape: **acting before checking the record.**
For example, `docs/T1-WALKTHROUGH.md` was written around a hardening change that
OPEN-QUESTIONS had already disproved nineteen days earlier. Four rules prevent this.

1. **Never answer from memory. Read the file.** This index goes stale. On 2026-09-08 it
   claimed no code existed while 49 tests were passing. Treat this file as a map, not as truth.
2. **Check documents against the code and the machine, not against other documents.**
   `T1-REVISIONS-LIST.md` said the event key used field *values*. The code uses field
   *presence*. Only a `grep` of `differential.py` found it. If a document states a number,
   a version, or a hash, verify it at the source.
3. **Settled means written in `DECISIONS.md`.** A draft marked ASSUMPTION is not a decision.
   The web-application deployment went from ASSUMPTION to "fact" in a submission document
   this way. If it is not in DECISIONS.md, say so.
4. **Do not invent anything checkable.** Control IDs, versions, hashes, commit IDs, file
   paths, event IDs. Search, or say "I don't know." A wrong CIS or DISA control ID is worse
   than none, because an examiner can look it up.

Dates come from `git log`, never from file timestamps. Two WORKLOG entries were wrong by a
day because of this.

Uncertainty goes in `OPEN-QUESTIONS.md`, not in a comment inside a draft.

---

## Commands

```bash
.venv/Scripts/python.exe src/demo.py          # end to end on synthetic data
.venv/Scripts/python.exe -m pytest tests -q   # expect: 55 passed (update when tests are added)
```

**Shell.** Commands for me to type are Windows PowerShell 5.1 in Windows Terminal (its default
profile, checked 2026-09-26; PowerShell 7 is not installed). Admin tasks: Terminal (Admin), same
shell. Inside SIEM-01: bash.

Stack pinned in `requirements.txt`: numpy 2.5.2, scipy 1.18.1, pandas 3.0.5, PyYAML 6.0.3,
pytest 9.1.1. Do not upgrade mid-experiment. See [src/](src/README.md).

Run the pre-flight check in [docs/COMMANDS.md](docs/COMMANDS.md) Part 5 before any runbook phase.

---

## Rules that fail silently

Breaking these produces no error, just wrong results. The reasons are in the runbook.

1. **No VM ever runs from E:.** It is a hard disk. VMs live on F:. (Phase 0)
2. **Pin every version and record it before the golden snapshot.** Wazuh, Sysmon binary and
   config hash, Atomic Red Team commit, Windows build, harness commit. A later bump discards
   every earlier run. (Phase 4, table in DECISIONS.md)
3. **`<logall_json>yes</logall_json>` in `ossec.conf`.** T1 counts what the machine emits,
   not what alerted. (Phase 2)
4. **Golden snapshot is taken with NAT disconnected.** (Phase 5)
5. **Fence capture windows in telemetry, not host clock.** Settle 180 s after boot, drain
   120 s after the suite. (Phase 6)

---

## Explaining this project

My global reply rules and the `defense-brief` skill cover how to write and how to close work.
This section covers what is special **here**.

- **Explain these terms in plain words the first time they appear in a reply, or do not use
  them.** Each one has caused real confusion: chi-square gate, coefficient of variation,
  dispersion, rate ratio, false discovery rate, Benjamini-Hochberg, q value, event key,
  field presence, noise floor, manifest hash, snapshot restore, confound.
- **Use a real number from this project.** "1247 events became 0" beats "the telemetry was
  lost". The numbers are in `WORKLOG.md` and the test files.
- **Say which layer you are answering at:** what the code does today, what the design says,
  or what a real deployment would need. Mixing them confuses the reader. See "built versus
  only designed" in [docs/PROMPT-new-chat.md](docs/PROMPT-new-chat.md).
- **Do not soften the falsifiable claims.** T1 and T3 state in advance the result that would
  prove them wrong. That is deliberate. It is the main defense against the sharpest panel
  objection.
- **A real test run comes before the proposal revision is submitted.** Understanding the
  system beats describing it.

---

## Conventions

- **Proposals follow a fixed institutional template.** Keep the structure and the
  problem-to-objective numbering. See [thesis/README.md](thesis/README.md).
- **Sourcing.** Engineering judgment is marked `(unverified)` inline. Numbers, dates, and any
  claim the reader may act on carry a source link or full reference.
- **Reply rules** load from `~/.claude/CLAUDE.md` on my machine. That file is private and is
  kept out of this repo on purpose. If it seems missing, ask me for it.

---

## Keep the record

Recorded, not remembered.

- **Append to [WORKLOG.md](docs/WORKLOG.md) every session.** Include what broke, with the
  exact error text. A failed attempt recorded beats a clean summary later.
- **Every chat about the thesis gets a WORKLOG entry that names its chat id** (the first 8
  characters of the Claude Code session id), including chats that only asked questions. A
  read-only chat writes nothing and says once that an entry is missing; the next working chat
  writes it. Thesis work happens in three folders: this repo,
  `E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)` and `F:\TeLoS Homelab`. A
  private hook archives every Claude Code chat in them, records changes made there by hand, and
  lists what WORKLOG is missing at the start of each chat. Chats outside Claude Code are not
  seen, so [docs/PROMPT-new-chat.md](docs/PROMPT-new-chat.md) asks them for a paste-ready entry.
- **Hard-to-reverse choices go in [DECISIONS.md](docs/DECISIONS.md)** with the reason and the
  cost if wrong. Never delete an entry. Supersede it.
- **Answered unknowns move to the Answered section** of OPEN-QUESTIONS.md, with the evidence.
- **Status changed?** Update `docs/STATUS.md` in the same session.
- **When a runbook phase finishes,** use the `phase-closeout` skill before starting the next
  phase. Do not skip it because the phase felt small.

---

## Git

**Live and public** at https://github.com/EASolutions00/detection-hardening-lab
The professor confirmed no IP rule and no similarity-check problem. Reason and cost are in
[DECISIONS.md](docs/DECISIONS.md). `gh` is installed and logged in as EASolutions00, so
`git push` and `gh` commands work directly.

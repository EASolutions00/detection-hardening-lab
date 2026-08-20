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
| [thesis/](thesis/README.md) | Proposal template and numbering rules. |
| [thesis/T1/](thesis/T1/README.md) | Hardening-induced blind spots. Primary. |
| [thesis/T2/](thesis/T2/README.md) | Severity inversion in the Wazuh ruleset. Second fallback. |
| [thesis/T3/](thesis/T3/README.md) | Analytic robustness scoring. First fallback. |
| [lab/blueprint.md](lab/blueprint.md) | Lab design, resource budget, go/no-go analysis. |
| [lab/configs/](lab/configs/README.md) | Pinned Sysmon and Wazuh configs. Hash them. |
| [lab/scripts/](lab/scripts/README.md) | One script per hardening change. Not snapshots. |
| [src/](src/README.md) | Python harness and analysis. No code yet. |
| `data/runs/` | Raw archives. Gitignored, too big for GitHub. One disk only, so back up elsewhere. |
| `data/summaries/` | Small derived CSVs. Committed. |

---

## Commands

**None yet. No code has been written. Do not invent any.**

Planned stack: Python 3.11+ in a venv on C: with `lxml`, `pyyaml`, `networkx`,
`scikit-learn`, `pandas`. See [src/](src/README.md).

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

T1 is gated behind a two week spike measuring run to run variance and real wall clock for
101 runs. See [runbook Phase 7](docs/RUNBOOK-homelab.md).

**The fallback is T3, and T3 has an unverified gate of its own.** Both the primary and the
fallback are unverified, so there is currently no verified option. This is item 1 in
[OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) and it is answerable offline in minutes.

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

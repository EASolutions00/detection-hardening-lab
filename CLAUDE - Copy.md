# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**This is the index. It points at the detail, it does not hold it.** Read the linked file.

---

## What this is

An undergraduate BS Computer Science thesis in detection engineering, plus the purple team
homelab built to run it. Student: Elijah Amorsolo, OED20-0012616.

Three candidate topics (T1, T2, T3). They are **alternatives, not components.** One gets built.
T1 is the primary choice and is gated behind a feasibility spike that has not run yet.

---

## Where everything lives

| Path | What is in it |
|---|---|
| [docs/RUNBOOK-homelab.md](docs/RUNBOOK-homelab.md) | **Build the lab from scratch.** 8 phases, each ends with a check. |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Why choices were made. Pinned versions. Spike results. |
| [docs/WORKLOG.md](docs/WORKLOG.md) | What happened each session, newest first. |
| [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) | Unverified things that change the plan. Ranked. |
| [docs/AI-RULES.txt](docs/AI-RULES.txt) | How the user wants replies written. Applies to every reply. |
| [thesis/T1/](thesis/T1/README.md) | Hardening-induced blind spots. Primary. |
| [thesis/T2/](thesis/T2/README.md) | Severity inversion in the Wazuh ruleset. Second fallback. |
| [thesis/T3/](thesis/T3/README.md) | Analytic robustness scoring. First fallback. |
| [lab/blueprint.md](lab/blueprint.md) | Lab design, resource budget, go/no-go analysis. |
| [lab/configs/](lab/configs/README.md) | Pinned Sysmon and Wazuh configs. Hash them. |
| [lab/scripts/](lab/scripts/README.md) | One script per hardening change. Not snapshots. |
| [src/](src/README.md) | Python harness and analysis. Empty so far. |
| `data/runs/` | Raw archives. **Gitignored.** Local only. |
| `data/summaries/` | Small derived CSVs. Committed. |

---

## Commands

**There are none yet. No code has been written. Do not invent any.**

When code starts, the stack is Python 3.11+ in a venv on C: with `lxml`, `pyyaml`,
`networkx`, `scikit-learn`, `pandas`. See [src/README.md](src/README.md).

Useful now:

```bash
git status
```

---

## Rules that break the thesis if broken

Full detail is in the runbook. These four are the ones that fail silently.

1. **No VM ever runs from E:.** It is a hard disk. Seek delay changes process timing, which
   changes event counts, which lands in the coefficient of variation that T1's whole
   statistics argument rests on. VMs live on F:. See [runbook Phase 0](docs/RUNBOOK-homelab.md).
2. **Pin every version and record it before the golden snapshot.** Wazuh, Sysmon binary and
   config hash, Atomic Red Team commit, Windows build, harness commit. A bump partway through
   discards every earlier run. Table is in [DECISIONS.md](docs/DECISIONS.md).
3. **`<logall_json>yes</logall_json>` must be set in `ossec.conf`.** T1 counts what the machine
   emits, not what alerted. Without this Wazuh keeps only events that fired a rule.
4. **Golden snapshot is taken with NAT disconnected.** Windows Update, Defender cloud lookups,
   certificate checks, and time sync all fire on their own schedule and inject noise into the
   exact window being measured.

Also: mark capture windows with in-telemetry fences, not host clock time. Settle 180 s after
boot, drain 120 s after the test suite.

---

## The open decision

T1 is gated behind a two week spike with two pre-declared questions
([runbook Phase 7](docs/RUNBOOK-homelab.md)):

- **Q1 run to run coefficient of variation.** Near zero under both configs means T1's headline
  result collapses to "justified only in production."
- **Q2 real wall clock.** 101 runs at about 40 minutes is roughly 67 hours. Only works if the
  harness is fully unattended.

**The fallback is T3, and T3 has an unverified gate of its own.** The count of manually
STP-annotated SigmaHQ rules may be too small for a meaningful Cohen's kappa. Right now both
the primary and the fallback are unverified, so there is no verified option. This is item 1
in [OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) and it is answerable offline in minutes.

Data collection must start no later than end of September.

---

## Conventions

**Writing in the proposals.** Each follows a fixed institutional template: Area of
Investigation, Algorithms, Current Process, 5 Problems, 1 general + 5 specific Objectives
(each tagged to a problem), Project Context, Features, 5 System Modules, Activity Diagram,
Importance to 4 audiences, Target Users, Similarities with Previous Studies. **Preserve the
structure and the problem-to-objective numbering.**

**Sourcing.** Engineering judgment is marked `(unverified)` inline. Numbers, dates, and
citations carry a source link or full reference. Prior work entries give authors, year, venue,
DOI or URL, the concrete figures from the paper, then what this proposal does that it did not.

**Do not soften the falsifiable claims.** T1 and T3 both pre-declare the result that would
prove them wrong and commit to reporting a null result plainly. That is deliberate and it is
the main defense against the sharpest panel objection.

**Replies.** Follow [docs/AI-RULES.txt](docs/AI-RULES.txt). Short summary: start with "Totoy,"
simple English, short sentences, never use the long dash character, label guesses
`(unverified)`, say "I don't know" rather than guess. For reviews and plans use critique,
then steelman, then recommendation, then summary.

---

## Session habits

The user forgets things, on purpose recorded rather than remembered. So:

- **Every session, append to [docs/WORKLOG.md](docs/WORKLOG.md).** Include what broke, with
  the error text. A failed attempt recorded is worth more later than a clean summary.
- **Any hard to reverse choice goes in [docs/DECISIONS.md](docs/DECISIONS.md)** with the reason
  and what it costs if wrong. Never delete an entry, supersede it.
- **Answered unknowns move to the Answered section** of OPEN-QUESTIONS.md with the evidence.
- Filling in a pinned version or a spike result means editing the tables in DECISIONS.md.

---

## Git and GitHub

Repo is **private until defense day**, then public. Reason and cost are in DECISIONS.md.

`gh` (GitHub CLI) is **not installed** on this machine. Either install it or create the repo
in the browser and add the remote by hand.

`data/runs/` is gitignored because GitHub blocks files over 100 MB and 101 gzipped archives
will not fit. Raw data therefore exists on one disk only. Back it up to a second physical
drive, not to git.

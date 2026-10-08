# T1 - Hardening-Induced Blind Spots

**Approved title:** Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using
Differential Analysis Algorithm (the panel's wording, kept verbatim, `docs/DECISIONS.md`
2026-09-14). The title first submitted is kept only in `proposal.txt`, the version the panel
read.

**Status:** The thesis. Final, with no fallback topic (`docs/DECISIONS.md` 2026-09-26). The
feasibility spike (runbook Phase 7) has not run; its result now decides scope only. Current
blockers are in `docs/STATUS.md`.

## The idea in one paragraph

You harden a machine to make it safer. Hardening changes configuration. Configuration decides
what events the machine writes. So hardening can silently delete the evidence your detection
rules depend on. The rule stays enabled, stays green on the coverage report, and detects
nothing. Nothing errors. Nobody finds out until an incident. This system catches that at the
moment the change is made.

## What makes it hard

- Needs the full lab. It is the only one of the three topics that does.
- **101 capture runs.** 16 changes times (3 pre + 3 post) = 96, plus 5 control runs. That is the
  design. The catalogue holds 14 changes today (`docs/OPEN-QUESTIONS.md` item 1). **Scope decided
  2026-09-29:** keep every measurable class C change and reduce the rest. Under Wazuh 4.14.7's shipped
  rules, about three changes (C1, C3, C5) can blind a detection (`docs/DECISIONS.md` 2026-10-01). The spike sets
  the final number, so the run count will be lower (`docs/DECISIONS.md` 2026-09-29).
- About 67 hours of wall clock for 101 runs, which only works if the harness is fully unattended.
- Target: final defense by the end of January 2027; the school deadline is 4 June 2027.

## The falsifiable claim

The proposal pre-declares its own failure condition and commits to reporting a null result
without softening it. If the run to run coefficient of variation is near zero, the statistics
layer buys nothing inside the lab and the study says so plainly. Do not edit that out. It is
the strongest defense against the sharpest objection a panel can raise.

## Ground truth

Two-tier labeling. Positive class is event keys the change verifiably removed, where you
know the cause because you caused it. Negative class is everything else in the pre-change
profile. Hand labeling 200 to 500 event keys is not feasible and is not the plan. (The unit
changed from event type to event key on 2026-09-04, `docs/DECISIONS.md`.)

## Files

- `proposal.txt` - the proposal as first submitted, the version the panel read. Old title and
  old wording are correct here. Institutional template, do not restructure
- `proposal-form.md`, `proposal-form-REVISED.md` - earlier Markdown forms of the proposal,
  superseded. The current revision, `proposal-form-FINAL.md`, lives outside this repo
- `figures/` - the scripts that generate the four T1 figures, and their SVG output
- `../../lab/blueprint.md` - lab design and the go/no-go analysis
- `../../docs/RUNBOOK-homelab.md` - how to actually build it

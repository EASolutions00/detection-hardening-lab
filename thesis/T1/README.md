# T1 - Hardening-Induced Blind Spots

**Title of the revised proposal:** Detecting Security Blind Spots Through Pre- and Post-Hardening Events
Using Myers' Difference Algorithm (the student's choice of 2026-11-24, recorded in `docs/DECISIONS.md`
2026-11-26). The adviser takes the revision to the panel for approval.

**Approved title before that:** Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using
Differential Analysis Algorithm (the panel's wording, kept verbatim, `docs/DECISIONS.md` 2026-09-14). The
adviser did not accept "differential analysis algorithm" as an algorithm (`docs/DECISIONS.md` 2026-11-23),
which led to the change. The title first submitted is kept only in `proposal.txt`, the version the panel
read.

**Status:** The thesis. Final, with no fallback topic (`docs/DECISIONS.md` 2026-09-26). The feasibility
spike (runbook Phase 7) ran 2026-11-16, 19 of 19 runs valid. The evaluation runs finished 2026-11-27 host time (2026-11-26 23:58 UTC): 26 of
26 valid, scored TP 7, FP 0, FN 0 (`docs/EXPECTED-RESULTS.md` section 7). Current blockers are in
`docs/STATUS.md`.

## The idea in one paragraph

You harden a machine to make it safer. Hardening changes configuration. Configuration decides
what events the machine writes. So hardening can silently delete the evidence your detection
rules depend on. The rule stays enabled, stays green on the coverage report, and detects
nothing. Nothing errors. Nobody finds out until an incident. This system catches that at the
moment the change is made.

## What made it hard

- Needs the full lab. It is the only one of the three topics that does.
- **The run count.** The first design was 101 capture runs: 16 changes times (3 pre + 3 post) = 96, plus 5
  control runs, about 67 hours at the 40 minutes per run guessed then. Under Wazuh 4.14.7's shipped rules only
  three changes (C1, C3, C5) can blind a detection (`docs/DECISIONS.md` 2026-10-01), so the study added three
  test cases with a known answer, K1 to K3 (`docs/DECISIONS.md` 2026-11-26). **The evaluation ran 26 runs:** 5
  control, 3 before shared by all cases, and 3 after for each of the 6 cases (`docs/DECISIONS.md` 2026-11-27),
  about 8.7 minutes each, 12.7 for C3.
- The runs only finish if the harness is fully unattended. It was: `src/evaluate.py` ran the batch, and resumed
  after a power cut (`docs/WORKLOG.md` 2026-11-27).
- Target: final defense by the end of January 2027; the school deadline is 4 June 2027. The next defense is
  the pre-oral: a 50% working system and chapters 1 to 3 (`docs/DECISIONS.md` 2026-11-23).

## The falsifiable claim

The proposal pre-declares its own failure condition and commits to reporting a null result
without softening it. If the run to run coefficient of variation is near zero, the statistics
layer buys nothing inside the lab and the study says so plainly. Do not edit that out. It is
the strongest defense against the sharpest objection a panel can raise.

## Ground truth

Two-tier labeling. Positive class is event keys the change verifiably removed, where you
know the cause because you caused it. Negative class is everything else in the pre-change
profile. Hand labeling 200 to 500 event keys is not feasible and is not the plan. (The unit
changed from event type to event key on 2026-09-04, `docs/DECISIONS.md`.) Since 2026-11-26 the
positives come from the test cases K1 to K3, whose expected lost keys were written before any run
(`docs/EXPECTED-RESULTS.md` sections 1 and 3).

## Files

- `proposal.txt` - the proposal as first submitted, the version the panel read. Old title and
  old wording are correct here. Institutional template, do not restructure
- `proposal-form.md`, `proposal-form-REVISED.md` - earlier Markdown forms of the proposal,
  superseded. `proposal-form-FINAL.md` (submitted 2026-10-15) and the current revision,
  `proposal-form-SIMPLIFIED.md`, live outside this repo (`docs/FILE-MAP.md` section 3)
- `figures/` - the scripts that generate the four T1 figures, and their SVG output. Figure 1 (the
  pipeline) and the activity diagram still need Myers' step (redraw pending)
- `../../lab/blueprint.md` - lab design and the go/no-go analysis
- `../../docs/RUNBOOK-homelab.md` - how to actually build it

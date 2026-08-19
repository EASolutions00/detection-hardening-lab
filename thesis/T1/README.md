# T1 - Hardening-Induced Blind Spots

**Full title:** Detection of Hardening-Induced Blind Spots via Differential Sequence Alignment
of Pre- and Post-Change Security Event Streams

**Status:** Primary choice. Gated behind the feasibility spike (runbook Phase 7).

## The idea in one paragraph

You harden a machine to make it safer. Hardening changes configuration. Configuration decides
what events the machine writes. So hardening can silently delete the evidence your detection
rules depend on. The rule stays enabled, stays green on the coverage report, and detects
nothing. Nothing errors. Nobody finds out until an incident. This system catches that at the
moment the change is made.

## What makes it hard

- Needs the full lab. It is the only one of the three topics that does.
- **101 capture runs.** 16 changes times (3 pre + 3 post) = 96, plus 5 control runs.
- About 67 hours of wall clock, which only works if the harness is fully unattended.

## The falsifiable claim

The proposal pre-declares its own failure condition and commits to reporting a null result
without softening it. If the run to run coefficient of variation is near zero, the statistics
layer buys nothing inside the lab and the study says so plainly. Do not edit that out. It is
the strongest defense against the sharpest objection a panel can raise.

## Ground truth

Two-tier labeling. Positive class is event types the change verifiably removed, where you
know the cause because you caused it. Negative class is everything else in the pre-change
profile. Hand labeling 200 to 500 event types is not feasible and is not the plan.

## Files

- `proposal.txt` - the submitted proposal, institutional template, do not restructure
- `../../lab/blueprint.md` - lab design and the go/no-go analysis
- `../../docs/RUNBOOK-homelab.md` - how to actually build it

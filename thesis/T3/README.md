# T3 - Analytic-Robustness Scoring of Sigma and Wazuh Rules

**Full title:** Automated Analytic-Robustness Scoring of Sigma and Wazuh Detection Rules Using
a Rule-Feature Dependency Model Based on the Summiting the Pyramid Methodology

> **STATUS: DEAD. Killed 2026-08-19. This file is kept as a record, not as a plan.**
>
> T3's evaluation depended on comparing the system's robustness scores against Sigma rules
> already annotated by hand under the Summiting the Pyramid methodology. **Only 6 of 3,783
> SigmaHQ rules carry such an annotation** at commit `da9bb07`. An agreement statistic on six
> rules means nothing.
>
> **If T1 fails its spike gate, go to T2.** Do not spend time reviving T3. Evidence is in
> `docs/OPEN-QUESTIONS.md`, Answered section.
>
> Everything below was written before that check and describes T3 as a live option. It is
> left unedited so the reasoning, and the mistake of not checking the annotation count first,
> stay visible.

**Status:** Dead. Superseded by the banner above.

## The idea in one paragraph

Coverage asks "is this technique detected at all." Robustness asks "how hard is it to evade
the detection." A rule keyed to a file name dies when the attacker renames the file. A rule
keyed to process behavior survives. Coverage reports treat both as equal, so they overstate
how well defended you are. This scores the difference automatically, across thousands of
rules, offline.

## Why it is the first fallback

No lab. No SIEM. No log ingestion. No network during analysis. Under 10 GB, runs on a laptop.
It can be built after a failed T1 spike without losing the semester.

It also has an **independent reference standard**, which T2 does not: part of the Sigma corpus
already carries robustness annotations assigned by hand under the same methodology. You compare
against someone else's labels, not your own, and report Cohen's kappa.

## The unresolved prerequisite (read before relying on this)

That reference standard may be too small.

The count of manually STP-annotated rules in SigmaHQ is **unverified**. If it is too small,
Cohen's kappa is not meaningful and Objective 5 fails. Which means the fallback has a gate of
its own, exactly like T1 does.

Verify this before treating T3 as the safe option. It is offline and takes minutes.
See `docs/OPEN-QUESTIONS.md` item 1.

## Files

- `proposal.txt` - the submitted proposal, institutional template, do not restructure

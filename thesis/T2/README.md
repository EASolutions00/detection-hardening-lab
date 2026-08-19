# T2 - Severity Inversion in the Wazuh Ruleset

**Full title:** Automated Detection of Severity Inversion in the Wazuh Default Ruleset Using
Parent-Child Dependency-Graph Analysis and Topological Consistency Scoring

**Status:** Not chosen. Second fallback, behind T3.

## The idea in one paragraph

A Wazuh rule can declare a parent rule. So the ruleset is a graph, not a list. Severity is
assigned by hand, one rule at a time, by people who cannot see the whole graph. A rule can
therefore sit at a severity that makes no sense given its ancestors, and the alert never gets
escalated to a human. This finds those automatically.

## Why it is the second fallback, not the first

It is the safest of the three to actually finish. Offline static analysis, no lab, no live
SIEM, runs on a laptop. Kahn topological ordering, Tarjan for cycles, severity bound
propagation. All well understood.

The weakness is the evaluation. T2 has no external ground truth. It relies on a manually
labeled subset that you create yourself, plus seeded defects that you inject yourself. A panel
can fairly ask whether you graded your own homework. T3 has an independent reference standard
(the published STP annotations), which is stronger, and that is why T3 ranks above it.

If T3's annotation count turns out too small (see `docs/OPEN-QUESTIONS.md` item 1), T2
becomes the real fallback and the self-labeling weakness has to be addressed head on, most
likely with a second annotator and a reported agreement statistic.

## Files

- `proposal.txt` - the submitted proposal, institutional template, do not restructure

"""Impact: which lost keys matter most (Module 4, activity diagram Box 24).

DECISIONS 2026-11-13: impact is a **ranking by three measured numbers**, not a
weighted score. For every key the analyser classified LOST or REDUCED:

1. **Blind techniques.** The ATT&CK techniques of the rules that read the key,
   for which **no alerting rule with that technique fired** in the "after" runs.
   Surviving coverage counts rules that **did** fire, read from the `rule.id` on
   each archive line (archive.WindowCounts.fired), not rules that could fire
   (DECISIONS 2026-11-13, "did fire").
2. **Highest severity**: the highest Wazuh level among the rules that read the key.
3. **Number of rules** that read the key.

Keys are ranked by these three, largest first. A key that no alerting rule reads
gets zeros and is ranked last: it "affects no detection" (DECISIONS 2026-10-01).

For each blind technique the report also shows the rules that **could** fire: an
alerting rule with the technique that reads an event type still observed after
the change (from the index). That is context for a reader, never counted: it shows
where a detection exists but the attack tests did not trigger it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .index import RuleIndex
from .model import AnalysisResult, Classification, Phase


@dataclass
class ImpactFinding:
    """One lost or reduced key, with the three ranking numbers and their parts."""

    key: str
    classification: Classification
    rules: list[str] = field(default_factory=list)            # alerting rules that read the key
    max_level: int = 0
    techniques: list[str] = field(default_factory=list)       # of those rules
    blind_techniques: list[str] = field(default_factory=list)
    surviving: dict[str, list[str]] = field(default_factory=dict)   # technique -> rules that did fire after
    could_fire: dict[str, list[str]] = field(default_factory=dict)  # blind technique -> rules that could fire

    @property
    def rank_key(self) -> tuple[int, int, int]:
        return (len(self.blind_techniques), self.max_level, len(self.rules))


def _fired_by_technique(fired_after: Mapping[str, int], index: RuleIndex) -> dict[str, set[str]]:
    """Technique -> alerting rules that fired at least once after the change."""
    out: dict[str, set[str]] = {}
    for rid, n in fired_after.items():
        rule = index.raw(rid)
        if n > 0 and rule is not None and rule.level >= 1:
            for t in rule.mitre:
                out.setdefault(t, set()).add(rid)
    return out


def _could_fire(post: Phase, index: RuleIndex) -> dict[str, set[str]]:
    """Technique -> alerting rules that read a key still observed after the change."""
    out: dict[str, set[str]] = {}
    for key in post.keys():
        if post.total(key) > 0:
            for ir in index.rules_reading(key):
                for t in ir.rule.mitre:
                    out.setdefault(t, set()).add(ir.rule.id)
    return out


def _by_id(ids: set[str]) -> list[str]:
    return sorted(ids, key=lambda r: (int(r) if r.isdigit() else 0, r))


def rank_impact(result: AnalysisResult, post: Phase, index: RuleIndex,
                fired_after: Mapping[str, int]) -> list[ImpactFinding]:
    """Rank the LOST and REDUCED keys of one comparison, most serious first.

    `fired_after` is rule id -> alerts, summed over the "after" windows
    (archive.WindowCounts.fired).
    """
    did = _fired_by_technique(fired_after, index)
    could = _could_fire(post, index)
    out: list[ImpactFinding] = []
    for f in result.findings:
        if f.classification not in (Classification.LOST, Classification.REDUCED):
            continue
        readers = index.rules_reading(f.key)
        techniques = sorted({t for ir in readers for t in ir.rule.mitre})
        surviving = {t: _by_id(did[t]) for t in techniques if did.get(t)}
        blind = [t for t in techniques if t not in surviving]
        out.append(ImpactFinding(
            key=f.key,
            classification=f.classification,
            rules=[ir.rule.id for ir in readers],
            max_level=max((ir.rule.level for ir in readers), default=0),
            techniques=techniques,
            blind_techniques=blind,
            surviving=surviving,
            could_fire={t: _by_id(could[t]) for t in blind if could.get(t)},
        ))
    return sorted(out, key=lambda h: (tuple(-n for n in h.rank_key), h.key))

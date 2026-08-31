"""Data model for the blind-spot analyser.

The unit of analysis is an *event-type key*. A key identifies one kind of security
event, for example Windows Security event 4688. One capture window produces one
count per key. A phase (pre-change, post-change, control) is several repetitions
of the same capture window.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Classification(str, Enum):
    """What the analyser concluded about one event-type key.

    INCONCLUSIVE exists on purpose. A key that occurred too few times before the
    change cannot be tested with any power. Calling it UNCHANGED would claim
    knowledge the data does not support and would inflate the reported recall.
    """

    LOST = "LOST"
    REDUCED = "REDUCED"
    UNCHANGED = "UNCHANGED"
    NEW = "NEW"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class Phase:
    """Repeated capture windows of one phase.

    counts maps an event-type key to one count per repetition. Every key must
    carry the same number of repetitions.

    window_minutes is the length of a single capture window. It is recorded so
    rates can be reported per minute, and so two phases of different window
    length are never silently compared.
    """

    name: str
    counts: dict[str, list[int]]
    window_minutes: float = 15.0

    @property
    def n_runs(self) -> int:
        if not self.counts:
            return 0
        return len(next(iter(self.counts.values())))

    def total(self, key: str) -> int:
        """Sum of counts for one key across every repetition."""
        return sum(self.counts.get(key, []))

    def mean(self, key: str) -> float:
        """Mean count per capture window for one key."""
        if self.n_runs == 0:
            return 0.0
        return self.total(key) / self.n_runs

    def keys(self) -> set[str]:
        return set(self.counts)

    def validate(self) -> None:
        """Fail loudly on ragged input rather than analysing it."""
        if not self.counts:
            raise ValueError(f"phase {self.name!r} has no event types")
        lengths = {len(v) for v in self.counts.values()}
        if len(lengths) != 1:
            raise ValueError(
                f"phase {self.name!r} has uneven repetitions per key: {sorted(lengths)}"
            )
        if self.window_minutes <= 0:
            raise ValueError(f"phase {self.name!r} has non-positive window_minutes")


@dataclass
class Finding:
    """The analyser's verdict on one event-type key."""

    key: str
    classification: Classification

    pre_total: int = 0
    post_total: int = 0
    pre_rate: float = 0.0
    post_rate: float = 0.0

    rate_ratio: float | None = None
    ci_low: float | None = None
    ci_high: float | None = None
    p_value: float | None = None
    q_value: float | None = None

    # from the control runs
    cov: float | None = None
    dispersion: float | None = None

    reason: str = ""

    @property
    def is_finding(self) -> bool:
        """True when this key is reported to the user as a loss."""
        return self.classification in (Classification.LOST, Classification.REDUCED)


@dataclass
class AnalysisResult:
    """Everything one validation run produced."""

    gate_passed: bool
    gate_p_value: float
    gate_statistic: float
    findings: list[Finding] = field(default_factory=list)
    n_tested: int = 0
    alpha: float = 0.05

    def by_class(self, c: Classification) -> list[Finding]:
        return [f for f in self.findings if f.classification is c]

    def reported(self) -> list[Finding]:
        """Findings shown to the user, worst drop first."""
        hits = [f for f in self.findings if f.is_finding]
        return sorted(hits, key=lambda f: (f.rate_ratio if f.rate_ratio is not None else 0.0))

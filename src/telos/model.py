"""Data model for the blind-spot analyser.

The unit of analysis is an *event key*: the event type plus which tracked fields
were populated, for example `Security-4688[CommandLine,NewProcessName]`. See
eventkey.py. One capture window produces one count per key. A phase (pre-change,
post-change, control) is several repetitions of the same capture window.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Classification(str, Enum):
    """What the analyser concluded about one event key.

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

    counts maps an event key to one count per repetition. Every key must carry
    the same number of repetitions.

    counts must hold the whole emitted profile, not a filtered subset. The
    analyser treats a repetition whose counts are all zero as a failed capture,
    which is only correct when every key the capture produced is present.

    window_minutes is the length of a single capture window. Rates are counts
    per repetition, not per minute. The window length is recorded so that two
    phases of different window length are never silently compared.
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

    def run_totals(self) -> list[int]:
        """Total events across every key, one value per repetition."""
        return [sum(vals[i] for vals in self.counts.values())
                for i in range(self.n_runs)]

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


class ProfileOutcome(str, Enum):
    """What the profile-level test concluded about one whole run.

    This is not the verdict on blind spots. Blind spots are the reported
    findings. This answers an earlier question: could the run be tested at all,
    and if so, did the emitted profile change?

    NOT_TESTABLE exists because "this change was safe" and "this run could not
    be tested" are opposite claims. Before 2026-09-14 both were reported as "no
    significant change", and a dead agent was reported as blind spots. See
    OPEN-QUESTIONS 16 and DECISIONS 2026-09-14.
    """

    CHANGED = "CHANGED"
    UNCHANGED = "UNCHANGED"
    NOT_TESTABLE = "NOT_TESTABLE"


@dataclass
class Finding:
    """The analyser's verdict on one event key."""

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
    """Everything one validation run produced.

    gate_p_value and gate_statistic are None when the chi-square was not run:
    the capture failed, or only one event key carried events, in which case the
    profile-level test does not apply and the key is tested directly.
    """

    outcome: ProfileOutcome
    outcome_reason: str
    gate_p_value: float | None = None
    gate_statistic: float | None = None
    findings: list[Finding] = field(default_factory=list)
    n_tested: int = 0
    alpha: float = 0.05

    def by_class(self, c: Classification) -> list[Finding]:
        return [f for f in self.findings if f.classification is c]

    def reported(self) -> list[Finding]:
        """Findings shown to the user, worst drop first."""
        hits = [f for f in self.findings if f.is_finding]
        return sorted(hits, key=lambda f: (f.rate_ratio if f.rate_ratio is not None else 0.0))

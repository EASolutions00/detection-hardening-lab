"""Synthetic telemetry, so the analyser can be built and tested without a lab.

Every number this module produces is generated, not measured. It exists to
exercise the analysis code and to demonstrate behaviour, never to stand in for
experimental results.

Each event type is declared with a mean count per capture window, a coefficient
of variation, and the tracked fields it normally populates. Counts are drawn as
a rounded normal and clipped at zero, which gives direct control over the noise
level. Real telemetry is not normal, but the analyser only consumes counts, so
this is enough to test it.

A hardening change is expressed as an Effect, which can do one of two things:
change an event's rate, or strip a field from it. The second case is the one
that a profile keyed on event type alone cannot see.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field

import numpy as np

from .eventkey import KeySpec
from .model import Phase


@dataclass
class EventSpec:
    """One synthetic event type."""

    source: str
    event_id: str
    mean: float
    cov: float                                  # relative spread, 0.06 is a 6 percent swing
    fields: tuple[str, ...] = ()                # tracked fields normally populated
    label: str = ""                             # human note, for demo output

    @property
    def event_type(self) -> str:
        return f"{self.source}-{self.event_id}"

    def key(self, dropped: frozenset[str] = frozenset()) -> str:
        """The analysis key for this event, optionally with fields stripped."""
        present = tuple(sorted(f for f in self.fields if f not in dropped))
        return str(KeySpec(self.source, self.event_id, present))


@dataclass
class Effect:
    """What a hardening change does to one event type.

    factor scales the rate: 0.0 removes the event entirely, 0.5 halves it,
    1.0 leaves the rate alone.

    drop_fields names tracked fields the change empties. The event still fires
    at its normal rate, but its key changes because those fields are no longer
    populated.
    """

    event_type: str
    factor: float = 1.0
    drop_fields: frozenset[str] = dc_field(default_factory=frozenset)


class Scenario:
    def __init__(self, specs: list[EventSpec], seed: int = 0):
        self.specs = {s.event_type: s for s in specs}
        self.rng = np.random.default_rng(seed)

    def _draw(self, mean: float, cov: float, n: int) -> list[int]:
        if mean <= 0:
            return [0] * n
        sd = mean * cov
        return [max(0, int(round(v))) for v in self.rng.normal(mean, sd, size=n)]

    def phase(
        self,
        name: str,
        n_runs: int,
        effects: list[Effect] | None = None,
        window_minutes: float = 15.0,
    ) -> Phase:
        """Generate one phase.

        Every key that either phase could produce is emitted, with zeros where
        an effect removed it. That keeps the key set consistent across runs
        within a phase, which Phase.validate() requires.
        """
        by_type = {e.event_type: e for e in (effects or [])}
        counts: dict[str, list[int]] = {}

        for event_type, spec in self.specs.items():
            eff = by_type.get(event_type)
            factor = eff.factor if eff else 1.0
            dropped = eff.drop_fields if eff else frozenset()

            full_key = spec.key()                 # all tracked fields populated
            reduced_key = spec.key(dropped)       # after the change, if any dropped

            drawn = self._draw(spec.mean * factor, spec.cov, n_runs)

            if dropped and reduced_key != full_key:
                # The event still fires, but under a different key. The old key
                # falls to zero and the reduced key carries the traffic.
                counts[full_key] = [0] * n_runs
                counts[reduced_key] = drawn
            else:
                counts[full_key] = drawn
                # Emit the reduced key at zero so both phases carry the same key
                # set and alignment has nothing to infer.
                if reduced_key != full_key:
                    counts[reduced_key] = [0] * n_runs

        return Phase(name=name, counts=counts, window_minutes=window_minutes)

    def all_keys(self, effects: list[Effect] | None = None) -> set[str]:
        """Every key this scenario can emit, before or after the effects."""
        by_type = {e.event_type: e for e in (effects or [])}
        keys: set[str] = set()
        for event_type, spec in self.specs.items():
            keys.add(spec.key())
            eff = by_type.get(event_type)
            if eff and eff.drop_fields:
                keys.add(spec.key(eff.drop_fields))
        return keys


def demo_scenario(seed: int = 7) -> tuple[Scenario, list[Effect]]:
    """A scenario built to exercise every classification the analyser can make.

    SYNTHETIC. These are not measurements and no benchmark control is claimed.
    Real Windows event identifiers are used only so the output is readable.

    The five cases, in order of what they prove:

    1. Event removed outright               -> LOST
    2. Event genuinely cut to 30 percent    -> REDUCED
    3. Noisy event drifting on its own      -> UNCHANGED (naive reports it, we do not)
    4. **Field stripped, rate untouched**   -> LOST + NEW pair
    5. Event too rare to test               -> INCONCLUSIVE

    Case 4 is the one an event-type-only profile cannot see at all.
    """
    specs = [
        # 1. Stable and frequent. Removed outright by the change.
        EventSpec("Security", "4688", mean=1247, cov=0.007,
                  fields=("CommandLine", "NewProcessName", "ParentProcessName"),
                  label="stable, high rate"),
        # 3. Noisy and frequent. Background network activity swings on its own.
        EventSpec("Security", "5156", mean=4119, cov=0.062,
                  fields=("DestPort", "Application"),
                  label="NOISY, high rate"),
        # 2. Moderately stable, genuinely cut by the change.
        EventSpec("Security", "4776", mean=612, cov=0.021,
                  fields=("PackageName", "TargetUserName", "Workstation"),
                  label="stable, mid rate"),
        # 4. FIELD LOSS. Rate never moves; ScriptBlockText stops being populated.
        EventSpec("PowerShell", "4104", mean=838, cov=0.015,
                  fields=("ScriptBlockText", "Path"),
                  label="FIELD LOSS case"),
        # 5. Too rare to test at all.
        EventSpec("Security", "4697", mean=2, cov=0.35,
                  fields=("ServiceName", "ServiceFileName"),
                  label="RARE, untestable"),
        # Filler, so the multiple-comparison correction has real work to do.
        *[
            EventSpec("Sysmon", str(eid), mean=m, cov=c, fields=("Image",))
            for eid, m, c in [
                (1, 1580, 0.012), (3, 2240, 0.048), (7, 890, 0.019),
                (10, 310, 0.031), (11, 1120, 0.026), (12, 640, 0.040),
                (13, 705, 0.033), (22, 415, 0.055), (23, 128, 0.070),
                (25, 96, 0.045),
            ]
        ],
    ]

    effects = [
        Effect("Security-4688", factor=0.0),                       # removed outright
        Effect("Security-4776", factor=0.30),                      # cut to 30 percent
        Effect("Security-5156", factor=0.986),                     # inside its own noise
        Effect("PowerShell-4104", drop_fields=frozenset({"ScriptBlockText"})),
    ]
    return Scenario(specs, seed=seed), effects

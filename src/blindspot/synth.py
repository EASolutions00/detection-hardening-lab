"""Synthetic telemetry, so the analyser can be built and tested without a lab.

Every number this module produces is generated, not measured. It exists to
exercise the analysis code and to demonstrate behaviour, never to stand in for
experimental results.

Each event-type key is declared with a mean count per capture window and a
coefficient of variation. Counts are drawn as a rounded normal and clipped at
zero, which gives direct control over the noise level. Real telemetry is not
normal, but the analyser only consumes counts, so this is enough to test it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import Phase


@dataclass
class KeySpec:
    """One synthetic event type."""

    key: str
    mean: float
    cov: float          # relative spread, e.g. 0.06 is a 6 percent swing
    label: str = ""     # human note, for the demo output


@dataclass
class Effect:
    """What a hardening change does to one key.

    factor 0.0 removes the key entirely. 0.5 halves its rate. 1.0 is no effect.
    """

    key: str
    factor: float


class Scenario:
    def __init__(self, specs: list[KeySpec], seed: int = 0):
        self.specs = {s.key: s for s in specs}
        self.rng = np.random.default_rng(seed)

    def _draw(self, mean: float, cov: float, n: int) -> list[int]:
        if mean <= 0:
            return [0] * n
        sd = mean * cov
        vals = self.rng.normal(mean, sd, size=n)
        return [max(0, int(round(v))) for v in vals]

    def phase(self, name: str, n_runs: int, effects: dict[str, float] | None = None,
              window_minutes: float = 15.0) -> Phase:
        """Generate one phase.

        effects maps a key to a multiplier applied to its mean. Keys not listed
        are unaffected.
        """
        effects = effects or {}
        counts: dict[str, list[int]] = {}
        for key, spec in self.specs.items():
            factor = effects.get(key, 1.0)
            counts[key] = self._draw(spec.mean * factor, spec.cov, n_runs)
        return Phase(name=name, counts=counts, window_minutes=window_minutes)


def demo_scenario(seed: int = 7) -> tuple[Scenario, list[Effect]]:
    """A scenario built to exercise every classification the analyser can make.

    SYNTHETIC. These are not measurements and no benchmark control is claimed.
    The event identifiers are real Windows event types, used only so the output
    is readable.
    """
    specs = [
        # Stable and frequent. A scripted stimulus produces nearly the same count
        # every run, so its natural swing is small.
        KeySpec("WinSec-4688-ProcessCreation", mean=1247, cov=0.007,
                label="stable, high rate"),
        # Noisy and frequent. Background network activity swings on its own.
        KeySpec("WinSec-5156-NetworkConnect", mean=4119, cov=0.062,
                label="NOISY, high rate"),
        # Moderately stable, will be genuinely halved by the change.
        KeySpec("WinSec-4776-NtlmAuth", mean=612, cov=0.021,
                label="stable, mid rate"),
        # Too rare to test at all.
        KeySpec("WinSec-4697-ServiceInstall", mean=2, cov=0.35,
                label="RARE, untestable"),
        # Filler, so the multiple-comparison correction has real work to do.
        *[
            KeySpec(f"Sysmon-{eid}-Filler", mean=m, cov=c)
            for eid, m, c in [
                (1, 1580, 0.012), (3, 2240, 0.048), (7, 890, 0.019),
                (10, 310, 0.031), (11, 1120, 0.026), (12, 640, 0.040),
                (13, 705, 0.033), (22, 415, 0.055), (23, 128, 0.070),
                (25, 96, 0.045),
            ]
        ],
    ]

    effects = [
        Effect("WinSec-4688-ProcessCreation", 0.0),   # removed outright
        Effect("WinSec-4776-NtlmAuth", 0.30),          # cut to 30 percent
        Effect("WinSec-5156-NetworkConnect", 0.986),   # 1.4 percent, inside its noise
    ]
    return Scenario(specs, seed=seed), effects

"""The noise floor, measured from control runs.

Control runs execute the identical stimulus against the identical restored
snapshot with no configuration change at all. Whatever variation remains is the
laboratory's own noise. Every later comparison is judged against it.

Two quantities are taken per event-type key.

coefficient of variation (CoV) = standard deviation / mean
    A plain relative spread. Used as the effect-size guard: a drop smaller than
    the key's own natural swing is not reported, whatever the p value says.

dispersion (index of dispersion) = variance / mean
    Poisson counts have dispersion 1, because a Poisson variance equals its mean.
    Real security telemetry is usually overdispersed, dispersion above 1. The
    rate-ratio test uses this to widen its confidence interval.

    Measuring the variance and then using a test that assumes it away would be
    inconsistent, which is why the analyser does not use a plain Poisson test.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import Phase


@dataclass
class KeyVariance:
    key: str
    mean: float
    std: float
    cov: float
    dispersion: float
    n_runs: int


class VarianceModel:
    """Per-key noise measured once per monitored environment."""

    def __init__(self, stats: dict[str, KeyVariance], default_dispersion: float = 1.0):
        self._stats = stats
        self.default_dispersion = default_dispersion

    @classmethod
    def from_control(cls, control: Phase, min_runs: int = 3) -> "VarianceModel":
        control.validate()
        if control.n_runs < min_runs:
            raise ValueError(
                f"variance model needs at least {min_runs} control runs, got {control.n_runs}"
            )

        stats: dict[str, KeyVariance] = {}
        for key, counts in control.counts.items():
            arr = np.asarray(counts, dtype=float)
            mean = float(arr.mean())
            # sample standard deviation, ddof=1: we are estimating from a sample,
            # not describing a population.
            std = float(arr.std(ddof=1)) if arr.size > 1 else 0.0

            if mean > 0:
                cov = std / mean
                dispersion = (std**2) / mean
            else:
                # A key never seen in the control runs has no measurable noise.
                cov = 0.0
                dispersion = 1.0

            # Never claim less variance than Poisson. Underestimating dispersion
            # would narrow the confidence interval and manufacture significance.
            dispersion = max(dispersion, 1.0)

            stats[key] = KeyVariance(
                key=key, mean=mean, std=std, cov=cov,
                dispersion=dispersion, n_runs=control.n_runs,
            )
        return cls(stats)

    def get(self, key: str) -> KeyVariance | None:
        return self._stats.get(key)

    def cov(self, key: str) -> float:
        s = self._stats.get(key)
        return s.cov if s else 0.0

    def dispersion(self, key: str) -> float:
        """Dispersion for a key. Keys unseen in control get the Poisson default."""
        s = self._stats.get(key)
        return s.dispersion if s else self.default_dispersion

    def keys(self) -> set[str]:
        return set(self._stats)

    def summary(self) -> dict[str, float]:
        """Headline numbers for the report and for the feasibility spike.

        median_cov answers the spike's question Q1: is there a noise floor at
        all? If it is near zero, the statistical layer buys nothing inside the
        laboratory, and the study must say so.
        """
        if not self._stats:
            return {"n_keys": 0, "median_cov": 0.0, "median_dispersion": 1.0, "share_cov_over_5pct": 0.0}
        covs = np.array([s.cov for s in self._stats.values()])
        disps = np.array([s.dispersion for s in self._stats.values()])
        return {
            "n_keys": float(len(self._stats)),
            "median_cov": float(np.median(covs)),
            "max_cov": float(covs.max()),
            "median_dispersion": float(np.median(disps)),
            "share_cov_over_5pct": float((covs > 0.05).mean()),
        }

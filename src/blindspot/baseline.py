"""The naive baseline the study is measured against.

An engineer with no tooling compares the two counts and reports anything that
went down. No variance model, no significance test, no correction. That is the
whole method, and it is what the proposed system has to beat.

It is implemented here honestly and given the best possible conditions, because
a baseline that has been quietly handicapped proves nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Phase


@dataclass
class BaselineFinding:
    key: str
    pre_rate: float
    post_rate: float

    @property
    def drop(self) -> float:
        if self.pre_rate == 0:
            return 0.0
        return 1.0 - (self.post_rate / self.pre_rate)


def naive_differencing(pre: Phase, post: Phase) -> list[BaselineFinding]:
    """Report every key whose mean count fell, by any amount at all."""
    keys = sorted(pre.keys() | post.keys())
    out: list[BaselineFinding] = []
    for k in keys:
        a, b = pre.mean(k), post.mean(k)
        if a > 0 and b < a:
            out.append(BaselineFinding(key=k, pre_rate=a, post_rate=b))
    return sorted(out, key=lambda f: -f.drop)

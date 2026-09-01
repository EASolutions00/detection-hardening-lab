"""Hardening-induced detection blind-spot analyser.

Thesis: Detecting Security Blind Spots Through Differential Analysis of
Pre- and Post-Hardening Events.

Stage 1 (acquisition from live VMs) is not implemented. It needs the lab.
Stages 2 to 5 are implemented and run on any counts, real or synthetic.
"""

from .model import AnalysisResult, Classification, Finding, Phase
from .variance import VarianceModel
from .differential import analyse
from .baseline import naive_differencing

__all__ = [
    "Phase",
    "Finding",
    "Classification",
    "AnalysisResult",
    "VarianceModel",
    "analyse",
    "naive_differencing",
]

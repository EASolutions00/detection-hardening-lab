"""End-to-end demonstration on synthetic data.

    .venv/Scripts/python.exe src/demo.py

Every number printed is generated, not measured. This exercises the analysis
code and shows the behaviour the system is designed to produce.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telos import VarianceModel, analyse, naive_differencing
from telos.report import render_analysis, render_comparison, render_variance
from telos.synth import demo_scenario

N_CONTROL = 5   # control runs, per the study design
N_REPEAT = 3    # repetitions per phase


def main() -> int:
    scenario, effects = demo_scenario(seed=7)
    effect_map = {e.key: e.factor for e in effects}

    print()
    print("SYNTHETIC DEMONSTRATION")
    print("All numbers are generated. No measurement, no benchmark control claimed.")
    print()

    # Phase 0. Measure the noise floor. Once per environment.
    control = scenario.phase("control", N_CONTROL)
    vm = VarianceModel.from_control(control)
    print(render_variance(vm))

    # Phases 1 and 3. Two capture phases under identical stimulus.
    pre = scenario.phase("pre-change", N_REPEAT)
    post = scenario.phase("post-change", N_REPEAT, effects=effect_map)

    # Stages B, C. The comparison.
    result = analyse(pre, post, vm)
    print(render_analysis(result))

    # Stage D. Head to head against the method an engineer would use by hand.
    naive = naive_differencing(pre, post)

    # Ground truth: we caused these, so we know them. This is the positive class
    # of the two-tier labelling. Everything else is the negative class.
    truth = {k for k, factor in effect_map.items() if factor <= 0.5}
    print(render_comparison(result, naive, truth))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

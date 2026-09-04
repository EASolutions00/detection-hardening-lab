"""End-to-end demonstration on synthetic data.

    .venv/Scripts/python.exe src/demo.py

Every number printed is generated, not measured. This exercises the analysis
code and shows the behaviour the system is designed to produce.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from telos import Classification, VarianceModel, analyse, naive_differencing
from telos.eventkey import field_loss_pairs
from telos.report import render_analysis, render_comparison, render_variance
from telos.synth import demo_scenario

N_CONTROL = 5   # control runs, per the study design
N_REPEAT = 3    # repetitions per phase


def ground_truth(scenario, effects) -> set[str]:
    """Keys the change really removed or reduced.

    This is the positive class of the two-tier labelling: event keys whose loss
    was deliberately caused, so it is known rather than inferred. Everything
    else in the pre-change profile is the negative class.
    """
    truth: set[str] = set()
    for eff in effects:
        spec = scenario.specs[eff.event_type]
        if eff.drop_fields:
            # The full-field key is genuinely lost; the reduced key replacing it
            # is a NEW, not a loss, so it is not part of the positive class.
            truth.add(spec.key())
        elif eff.factor <= 0.5:
            truth.add(spec.key())
    return truth


def render_field_losses(result) -> str:
    """Pair each LOST key with the NEW key that replaced it, minus fields.

    Without this a reader sees an unexplained LOST beside an unexplained NEW and
    has to work out the relationship by hand.
    """
    lost = [f.key for f in result.by_class(Classification.LOST)]
    new = [f.key for f in result.by_class(Classification.NEW)]
    pairs = field_loss_pairs(lost, new)
    if not pairs:
        return ""

    out = ["=" * 78, "FIELD-LEVEL LOSS", "=" * 78, ""]
    out.append("  The event still fires at its normal rate. A field inside it stopped")
    out.append("  being populated, so any detection rule matching on that field is blind.")
    out.append("  A profile keyed on event type alone cannot see this.")
    out.append("")
    for lost_key, new_key, dropped in pairs:
        out.append(f"  was  {lost_key}")
        out.append(f"  now  {new_key}")
        out.append(f"  lost field(s): {', '.join(dropped)}")
        out.append("")
    return "\n".join(out)


def main() -> int:
    scenario, effects = demo_scenario(seed=7)

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
    post = scenario.phase("post-change", N_REPEAT, effects=effects)

    # Stages B and C. The comparison.
    result = analyse(pre, post, vm)
    print(render_analysis(result))

    # The field-level case, stated explicitly.
    field_report = render_field_losses(result)
    if field_report:
        print(field_report)

    # Stage D. Head to head against the method an engineer would use by hand.
    naive = naive_differencing(pre, post)
    print(render_comparison(result, naive, ground_truth(scenario, effects)))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

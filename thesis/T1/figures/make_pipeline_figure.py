"""Generate the analysis pipeline figure.

Run:  .venv/Scripts/python.exe thesis/T1/figures/make_pipeline_figure.py

The figure shows the whole analysis on one page: three capture streams in, one
ranked report out, with every statistical step named.

What was wrong with the 2026-08-28 version, checked against src/telos/ on
2026-09-09:

  1. "Normalize every raw record to an event-type key e = ( source, event ID,
     discriminating fields )". The unit of analysis is the event key: source,
     event ID, and which tracked fields were actually POPULATED
     (DECISIONS.md 2026-09-04, eventkey.py). "Discriminating fields" was vague
     and predated that decision.

  2. "λ₀(e) = count / window". differential.py:115 computes `a / n1`, the count
     divided by the NUMBER OF RUNS, not by the window length. Because analyse()
     rejects phases whose windows differ (differential.py:266), the two are
     proportional and the rate ratio is identical either way, so no result
     changes. The formula shown was still not the one that runs.

  3. The global gate was missing entirely. analyse() runs one chi-square test of
     homogeneity over the whole 2-by-K profile BEFORE any key is tested, and
     returns with no findings when it does not pass (differential.py:273-281).
     A figure that omits it implies every key is always tested.

  4. The decision-rule box did not say what makes a key INCONCLUSIVE. That is
     MIN_PRE_COUNT = 30 (differential.py:138), and it is the classification a
     reader is most likely to be asked about.

  5. field_loss_pairs() (eventkey.py:159) had no step. It is what turns an
     unexplained LOST beside an unexplained NEW into a single field-level
     finding.

What changed on 2026-09-14, after an outside review and the gate fix of the
same date (DECISIONS.md, OPEN-QUESTIONS 16):

  6. The gate box now starts with the capture check. A repetition that recorded
     no events makes the run NOT TESTABLE (capture_problem(), differential.py).
     Before, an empty post-change phase passed the gate and was reported LOST.
  7. The gate box names its three outcomes, the alpha it compares against, and
     the single-key case, which skips chi-square and is tested directly.
  8. "a key is only a finding if it clears q, effect size, and the noise floor
     together" applied to every class. In classify() it applies to REDUCED
     only. LOST needs zero after and a corrected q at or below alpha.
  9. The post-change stream says the change is applied by script (D2). There is
     no post-change snapshot.
"""

from pathlib import Path

from svgkit import (DEFS, MUTED, action_box, arrow, edge_label, rect, svg,
                    system_box, text)

W, H = 1020, 878

STREAM_X = [30.0, 360.0, 690.0]
STREAM_CX = [180.0, 510.0, 840.0]
STREAM_W = 300.0
MID = 510.0


def build() -> str:
    body = [rect(0, 0, W, H, "#FFFFFF"), DEFS]

    # --- three capture streams -------------------------------------------
    heads = ["CONTROL  ·  5 RUNS", "PRE-CHANGE  ·  3 RUNS",
             "POST-CHANGE  ·  3 RUNS"]
    # CHANGED 2026-09-14 (D2): no post-change snapshot. The same snapshot is
    # restored and the change is applied by script inside each run.
    subs = ["no configuration change", "before the change",
            "change applied by script"]
    for x, cx, head, sub in zip(STREAM_X, STREAM_CX, heads, subs):
        body.append(text(cx, 22, head, size=11, weight=600, fill=MUTED,
                         mono=True, spacing="0.08em"))
        body += action_box(x, 38, STREAM_W, 58,
                           ["Same snapshot, same stimulus,", sub], size=13)
        body.append(arrow(f"M{cx} 96.0 V128.0"))

    # --- the unit of analysis --------------------------------------------
    # CHANGED: was "an event-type key e = ( source, event ID, discriminating
    # fields )". The key is the event type plus the tracked fields that were
    # populated. See eventkey.py.
    body += action_box(30, 130, 960, 56, [
        "Reduce every raw record to an event key    "
        "e = ( source, event ID, populated tracked fields )"], size=13)
    for cx in STREAM_CX:
        body.append(arrow(f"M{cx} 186.0 V218.0"))

    # --- per-stream products ---------------------------------------------
    body += system_box(30, 220, STREAM_W, 62, [
        "Dispersion φ(e) and coefficient",
        "of variation per key, the noise floor"], size=13)
    # CHANGED: count / window -> count / runs. differential.py:115.
    body += action_box(360, 220, STREAM_W, 62, [
        "Pre-change rate", "λ₀(e)  =  count / runs"], size=13)
    body += action_box(690, 220, STREAM_W, 62, [
        "Post-change rate", "λ₁(e)  =  count / runs"], size=13)

    # --- NEW: the global gate --------------------------------------------
    body.append(arrow("M510.0 282.0 V320.0"))
    body.append(arrow("M840.0 282.0 V301.0 H630.0 V320.0"))
    # CHANGED 2026-09-14: the capture check, the three outcomes, alpha, and the
    # single-key case. Everything below this box moved down 18.
    body += system_box(230, 322, 560, 80, [
        "Capture check:  any repetition with zero events  →  NOT TESTABLE, stop",
        "Global gate:  one χ² test on the whole 2 × K profile, at α",
        "no change  →  UNCHANGED, no key tested   ·   one key only  →  test it "
        "directly"], size=12)
    body.append(arrow("M510.0 402.0 V430.0"))

    # The noise floor bypasses the gate: it is measured once and feeds the
    # per-key test directly.
    body.append(arrow("M180.0 282.0 V421.0 H390.0 V430.0", dashed=True))
    # Sits above the gate box, not beside it: at y=340 the label ran into the
    # gate's left edge.
    body += edge_label(188, 302, "noise floor", bg="#FFFFFF")

    # --- per-key test -----------------------------------------------------
    body += action_box(30, 432, 960, 74, [
        "For every key in the union of both profiles:    rate ratio  "
        "RR(e) = λ₁(e) / λ₀(e)  with a confidence interval,",
        "and  p(e)  from a rate test that uses the measured dispersion φ(e) "
        "instead of assuming none"], size=13)
    body.append(arrow("M510.0 506.0 V534.0"))

    body += action_box(230, 536, 560, 50, [
        "Benjamini-Hochberg across all K keys  →  q(e), the "
        "false-discovery-corrected value"], size=13)
    body.append(arrow("M510.0 586.0 V614.0"))

    # --- decision rule ----------------------------------------------------
    # CHANGED 2026-09-09: added the INCONCLUSIVE rule.
    # CHANGED 2026-09-14: "clears q, effect size and the noise floor together"
    # is the rule for REDUCED only. classify(), differential.py.
    body += system_box(140, 616, 740, 80, [
        "Decision rule  →  LOST  ·  REDUCED  ·  UNCHANGED  ·  NEW  ·  "
        "INCONCLUSIVE",
        "REDUCED needs q, effect size and the noise floor together   ·   "
        "LOST needs zero after and q ≤ α",
        "fewer than 30 events before the change  →  INCONCLUSIVE, never "
        "tested"], size=13)
    body.append(arrow("M510.0 696.0 V724.0"))

    # --- NEW: field-level loss -------------------------------------------
    body += system_box(140, 726, 740, 50, [
        "Pair LOST and NEW keys of one event type differing only by dropped "
        "fields  →  field-level loss"], size=13)
    body.append(arrow("M510.0 776.0 V804.0"))

    body += action_box(140, 806, 740, 50, [
        "Graph traversal  e → detection rules → ATT&CK techniques  →  "
        "impact score  →  ranked report"], size=13)

    aria = ("Three capture streams feed the comparison. Control runs build the "
            "noise model; pre-change and post-change runs build the two "
            "profiles. One chi-square gate asks whether the profile changed at "
            "all, then each event key is tested against the measured noise, "
            "corrected for multiple comparisons, classified, paired for "
            "field-level loss, and traversed to the detection rules it affects.")
    return svg(W, H, aria, body)


def main() -> None:
    path = Path(__file__).resolve().parent / "T1_Figure_Analysis_Pipeline.svg"
    path.write_text(build(), encoding="utf-8")
    print(f"wrote {path}  ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

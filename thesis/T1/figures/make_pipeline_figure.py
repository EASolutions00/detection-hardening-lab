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

What changed on 2026-09-28:

 10. "fewer than 30 events before -> INCONCLUSIVE" also covered NEW keys, which
     have 0 before. _test_key() tests NEW first. The line now says "1 to 29
     before" and "0 before -> NEW".
 11. Later the same day (DECISIONS.md 2026-09-28): the gate box said "no change
     -> UNCHANGED, no key tested". The chi-square is now reported as a summary
     and never stops a key being tested. And a key the control runs never saw
     is INCONCLUSIVE, because it has no noise measurement.

What changed on 2026-09-29 (DECISIONS.md 2026-09-29, OPEN-QUESTIONS 18):

 12. The key box said "e = ( source, event ID, populated tracked fields )". For a
     short list of fields the key now also records the value, grouped into a few
     classes. Designed, not built yet.

WHAT CHANGED ON 2026-11-28 (fix 9 of the outside review; the revised proposal,
proposal-form-SIMPLIFIED.md, says "Figure 1 ... must be redrawn: Myers' step in the
pipeline")

 13. The figure is drawn as the proposal's five steps, numbered and named as its
     "Algorithms to be Used" section names them: import, normalize, compare, check
     against normal variation, link to detections.
 14. Myers' difference algorithm is step 3 (DECISIONS 2026-11-26; myers.py). It
     lists every deleted and inserted event and decides no key. Step 4 tests every
     key, so every key Myers found deleted is tested there.
 15. The decision rule. LOST is decided by the exact test at any count,
     p = exp(-λ₀·n₂/φ) (DECISIONS 2026-11-26), and a loss with q > α is
     INCONCLUSIVE (DECISIONS 2026-11-27). The old line, "1 to 29 before ->
     INCONCLUSIVE", is now true only of a partial drop.
 16. "impact score" was wrong since 2026-11-13: impact is a ranking by three
     measured numbers, not a score (impact.py). Step 5 also names the techniques no
     longer detected and the recommendations.
 17. The noise model box names the check on the control runs: a control run with
     no events stops the analysis (VarianceModel.from_control()).
 18. The aria text said "One chi-square gate asks whether the profile changed at
     all". The chi-square is a summary only, since 2026-09-28.
 19. The tint now means one thing, as in the activity diagram (D3): a tinted box is
     a step the system performs; the white boxes are the run records that come in.
     The artifact box is the report that goes out. The old figure mixed the two.
 20. Positions are computed from the box above, so inserting a step moves
     everything below it. The size went from 1020 × 878 to 1020 × 1174.
"""

from pathlib import Path

from svgkit import (DEFS, MUTED, action_box, arrow, datastore, edge_label, rect,
                    svg, system_box, text)

W = 1020

STREAM_X = [30.0, 360.0, 690.0]
STREAM_CX = [180.0, 510.0, 840.0]
STREAM_W = 300.0
MID = 510.0
GAP = 2.0           # an arrowhead stops this far short of its target
LABEL_GAP = 12.0    # from a step's label to its box
LABEL_X = STREAM_CX[0] + 16.0


def step_label(x: float, y: float, s: str) -> str:
    return text(x, y, s, size=11, weight=600, anchor="start", fill=MUTED,
                mono=True, spacing="0.08em")


def build() -> str:
    body: list[str] = []

    # --- the run records, from the study's lab tool ----------------------
    heads = ["CONTROL  ·  5 RUNS", "BEFORE THE CHANGE  ·  3 RUNS",
             "AFTER THE CHANGE  ·  3 RUNS"]
    # D2: no post-change snapshot. The same snapshot is restored and the change
    # is applied by script inside each run.
    subs = ["no configuration change", "before the change",
            "change applied by script"]
    for x, cx, head, sub in zip(STREAM_X, STREAM_CX, heads, subs):
        body.append(text(cx, 22, head, size=11, weight=600, fill=MUTED,
                         mono=True, spacing="0.08em"))
        body += action_box(x, 38, STREAM_W, 58,
                           ["Same snapshot, same attack tests,", sub], size=13)
    y = 38 + 58

    # --- step 1: import ---------------------------------------------------
    y1 = y + 50
    for cx in STREAM_CX:
        body.append(arrow(f"M{cx} {y} V{y1 - GAP}"))
    # The labels of steps 1 to 3 start right of the arrow at x = 180: at x = 30
    # "STEP 2  ·  NORMALIZE" ran into it.
    body.append(step_label(LABEL_X, y1 - LABEL_GAP, "STEP 1  ·  IMPORT"))
    body += system_box(30, y1, 960, 58, [
        "Read the run records and the rule files exported from the SIEM; leave out "
        "the voided runs and name them",
        "at least 3 valid runs per phase; one settings hash (SHA-256) and one change "
        "for all runs; the rule files' hash"], size=13)
    y = y1 + 58

    # --- step 2: normalize ------------------------------------------------
    y2 = y + 50
    for cx in STREAM_CX:
        body.append(arrow(f"M{cx} {y} V{y2 - GAP}"))
    body.append(step_label(LABEL_X, y2 - LABEL_GAP, "STEP 2  ·  NORMALIZE"))
    # The key: eventkey.py. A few fields are keyed by value (DECISIONS 2026-09-29).
    body += system_box(30, y2, 960, 58, [
        "Each event becomes an event key    e = ( source, event ID, populated "
        "tracked fields, value class of a few )",
        "each phase's runs joined into one list, sorted by merge sort; a hash map "
        "counts the events of each key"], size=13)
    y = y2 + 58

    # --- step 3: compare, and the noise model for step 4 ------------------
    y3 = y + 50
    for cx in STREAM_CX:
        body.append(arrow(f"M{cx} {y} V{y3 - GAP}"))
    body.append(step_label(LABEL_X, y3 - LABEL_GAP, "FOR STEP 4"))
    # Right of the arrow at x = 510, for the same reason.
    body.append(step_label(MID + 12, y3 - LABEL_GAP, "STEP 3  ·  COMPARE"))
    # VarianceModel.from_control(): it refuses a control run with no events.
    body += system_box(30, y3, STREAM_W, 80, [
        "Noise model from the 5 control runs:",
        "dispersion φ(e) and the coefficient",
        "of variation CoV(e) of every key",
        ("a control run with no events: stop, with an error", 11)], size=13)
    # myers.py, DECISIONS 2026-11-26.
    body += system_box(360, y3, 630, 80, [
        "Myers' difference algorithm: the before list against the after list",
        "→  deleted events (losses), inserted events (new), edit distance D",
        ("normal noise is included, so it decides no key: step 4 tests every key", 11)],
        size=13)
    y = y3 + 80
    myers_cx = 360 + 630 / 2

    # --- step 4: check against normal variation ---------------------------
    y4 = y + 50
    body.append(arrow(f"M{myers_cx} {y} V{y4 - GAP}"))
    body.append(step_label(230, y4 - LABEL_GAP,
                           "STEP 4  ·  CHECK AGAINST NORMAL VARIATION"))
    # capture_problem() and global_gate(), differential.py. The chi-square has
    # been a summary only since 2026-09-28.
    body += system_box(230, y4, 560, 58, [
        "Capture check: a run before or after with no events  →  NOT TESTABLE, stop",
        "Whole-profile χ²: one test on the 2 × K profile, reported as a summary only"],
        size=12.5)
    gate_bot = y4 + 58

    y4b = gate_bot + 28
    body.append(arrow(f"M{MID} {gate_bot} V{y4b - GAP}"))
    # _test_key() and _complete_loss(): the exact test for a key that fell to 0
    # (DECISIONS 2026-11-26), the rate ratio for a drop. Rates are count / runs.
    body += system_box(30, y4b, 960, 74, [
        "For every key, rates  λ₀(e), λ₁(e) = count / runs.    Fell to 0: the exact "
        "test,  p = exp( −λ₀ · n₂ / φ(e) ),  n₂ runs after",
        "Dropped: the rate ratio  RR(e) = λ₁ / λ₀,  with p from a rate test that "
        "uses the measured dispersion φ(e)"], size=13)
    # The noise model passes the capture check and the summary: it feeds the
    # per-key test directly.
    body.append(arrow(f"M{STREAM_CX[0]} {y3 + 80} V{y4b - GAP}", dashed=True))
    # Between the two boxes: higher up, the label ran into the capture check's
    # left edge.
    body += edge_label(188, gate_bot + 14, "noise floor", bg="#FFFFFF")
    y = y4b + 74

    y4c = y + 28
    body.append(arrow(f"M{MID} {y} V{y4c - GAP}"))
    body += system_box(230, y4c, 560, 50, [
        "Benjamini-Hochberg across all K keys  →  q(e), the "
        "false-discovery-corrected value"], size=13)
    y = y4c + 50

    # classify(), differential.py. LOST at any count since DECISIONS 2026-11-26;
    # a loss that fails the correction is INCONCLUSIVE since 2026-11-27.
    y4d = y + 28
    body.append(arrow(f"M{MID} {y} V{y4d - GAP}"))
    body += system_box(140, y4d, 740, 98, [
        "Decision rule  →  LOST  ·  REDUCED  ·  UNCHANGED  ·  NEW  ·  INCONCLUSIVE",
        "LOST: none after and q ≤ α, at any count    ·    none after but q > α  →  "
        "INCONCLUSIVE",
        "REDUCED needs all three: q ≤ α, ratio ≤ 0.5, drop > 3 × CoV    ·    "
        "0 before  →  NEW",
        "a partial drop with fewer than 30 before, or a key the control runs never "
        "saw  →  INCONCLUSIVE"], size=13)
    y = y4d + 98

    # field_loss_pairs(), eventkey.py.
    y4e = y + 28
    body.append(arrow(f"M{MID} {y} V{y4e - GAP}"))
    body += system_box(140, y4e, 740, 50, [
        "Pair LOST and NEW keys of one event type differing only by dropped "
        "fields  →  field-level loss"], size=13)
    y = y4e + 50

    # --- step 5: link to detections ---------------------------------------
    # impact.py: a ranking by three measured numbers, not a score (DECISIONS
    # 2026-11-13). report.coverage_change(); remediation levels 1 and 2.
    y5 = y + 50
    body.append(arrow(f"M{MID} {y} V{y5 - GAP}"))
    body.append(step_label(140, y5 - LABEL_GAP, "STEP 5  ·  LINK TO DETECTIONS"))
    body += system_box(140, y5, 740, 76, [
        "Event key  →  the rules that read it  →  their ATT&CK techniques;  "
        "the techniques no longer detected",
        "Rank by three measured numbers, not a score: blind techniques, highest "
        "level, number of rules",
        "Recommend: rules that still read events seen after the change, and known "
        "compensating controls"], size=13)
    y = y5 + 76

    yr = y + 28
    body.append(arrow(f"M{MID} {y} V{yr - GAP}"))
    body += datastore(140, yr, 740, 56, [
        "« artifact »  Report: the verdict with the undecided keys, Myers, the noise "
        "floor, the ranked findings,",
        "the coverage change, the recommendations, the reproducibility record   ·   "
        "CSV  ·  JSON  ·  ATT&CK Navigator layer"])
    height = yr + 56 + 30

    aria = ("The analysis in the five steps of the proposal. The run records of 5 "
            "control runs, 3 runs before and 3 after the change are imported and "
            "checked, and each event becomes an event key. Myers' difference algorithm "
            "compares the before list with the after list and lists every deleted and "
            "inserted event. Every key is then tested against the noise measured in "
            "the control runs, corrected for multiple comparisons, classified, and "
            "paired for field-level loss. Lost and reduced keys are linked to the "
            "detection rules and ATT&CK techniques that read them, ranked by three "
            "measured numbers, and written to the report with recommendations.")
    return svg(W, height, aria, [rect(0, 0, W, height, "#FFFFFF"), DEFS] + body)


def main() -> None:
    path = Path(__file__).resolve().parent / "T1_Figure_Analysis_Pipeline.svg"
    path.write_text(build(), encoding="utf-8")
    print(f"wrote {path}  ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

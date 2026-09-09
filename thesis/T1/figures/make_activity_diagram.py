"""Generate the T1 activity diagram, both sheets, as SVG.

Run:  .venv/Scripts/python.exe thesis/T1/figures/make_activity_diagram.py

Why this file exists. The 2026-08-28 hand-drawn version described the analysis
as keyed on event type alone. The unit of analysis changed on 2026-09-04 to
event type plus populated tracked fields (DECISIONS.md). The figure was never
updated, because it had no source to update: it existed only as SVG text with
hand-computed absolute coordinates. Patching those by hand a second time would
recreate the same failure. Now the figure is generated, so a design change is a
string edit and a re-run.

What changed from the 2026-08-28 version, and why each change was made:

  1. "per event type"        -> "per event key"          (Sheet 1, Phase 0)
  2. "normalize to
      event-type keys"       -> "keyed by event type +
                                populated tracked fields" (Sheet 1, Phase 1)
  3. "union of
      event-type keys"       -> "union of event keys"     (Sheet 2, Phase 4)
  4. "event-type -> rule"    -> "event key -> rule"       (Sheet 1, Phase 0)
  5. decision "Any LOST or REDUCED key below the noise floor?"
                             -> "Any key classified LOST or REDUCED?"
     The noise floor is not a separate later test. It is one of the three
     conditions inside classify() (differential.py:229). The old label also
     inverted the comparison: reporting requires the drop to EXCEED the noise
     band, not fall below it. The three conditions now appear inside the
     classification box, where the code puts them.
  6. New activity: matching LOST and NEW keys of the same event type that
     differ only by dropped fields. This is field_loss_pairs() in
     eventkey.py:159. It was a real step of the method with no box.

Deliberately NOT changed, and this is a decision rather than an oversight.
The "no" branch still reads "Record no significant change". global_gate()
returns not-passed for three different situations, and only one of them is
"nothing changed" (differential.py:74, :84, :91). The other two are "could not
test". Relabelling the box would put the diagram ahead of the code and create a
new mismatch of exactly the kind this rewrite is fixing. Tracked as
OPEN-QUESTIONS 16 instead, so the result model is changed first and the figure
follows.
"""

from pathlib import Path

from svgkit import (
    DEFS, DIVIDER, HEADER, HEADER_SUB, LANE_A, LANE_B,
    action_box, arrow, connector, datastore, decision, edge_label, end_node,
    line, loop_frame, phase_band, rect, start_node, svg, system_box, text,
)

# Lane geometry, shared by both sheets.
LANES = [(0, 330), (330, 450), (780, 320), (1100, 440)]
CX = [165.0, 555.0, 940.0, 1320.0]
SHEET_W = 1690
BOARD_W = 1540
HEAD_H = 66


def chrome(height):
    """Background, marker definitions and lane bands."""
    out = [rect(0, 0, SHEET_W, height, "#FFFFFF"), DEFS]
    band_h = height - HEAD_H
    for i, (x, w) in enumerate(LANES):
        out.append(rect(x, HEAD_H, w, band_h, LANE_A if i % 2 == 0 else LANE_B))
    return out


def header(height):
    out = []
    for x, _w in LANES[1:]:
        out.append(line(x, HEAD_H, x, height, DIVIDER, 1))
    out.append(rect(0, 0, BOARD_W, HEAD_H, HEADER))
    out.append(text(CX[0], 33, "Security / Systems Engineer", size=14,
                    weight=600, fill="#FFFFFF"))
    out.append(text(CX[1], 33, "Proposed System", size=14, weight=600,
                    fill="#FFFFFF"))
    out.append(text(CX[2], 25, "Monitored Environment", size=14, weight=600,
                    fill="#FFFFFF"))
    out.append(text(CX[2], 44, "SIEM · Endpoints · Hypervisor", size=11,
                    weight=400, fill=HEADER_SUB, mono=True))
    out.append(text(CX[3], 33, "Security Detection Engineer", size=14,
                    weight=600, fill="#FFFFFF"))
    return out


# ---------------------------------------------------------------- sheet 1

def sheet1() -> str:
    H = 2086
    body = chrome(H)

    body += phase_band(76, "PHASE 0  ·  ENVIRONMENT SETUP  ·  runs once "
                           "per environment, not per change", BOARD_W)
    body += phase_band(758, "PHASE 1  ·  PRE-CHANGE CAPTURE", BOARD_W)
    body += phase_band(1370, "PHASE 2  ·  APPLY THE HARDENING CHANGE", BOARD_W)
    body += phase_band(1620, "PHASE 3  ·  POST-CHANGE CAPTURE  ·  identical "
                             "manifest, nothing else varied", BOARD_W)
    body += header(H)

    body += loop_frame(340, 374, 750, 186, "loop  [ 5 control runs ]")
    body += loop_frame(340, 986, 750, 276, "loop  [ 3 runs ]")
    body += loop_frame(340, 1668, 750, 256, "loop  [ 3 runs ]")

    for d in ["M165.0 186.0 V214.0",
              "M165.0 276.0 V291.0 H555.0 V304.0",
              "M555.0 366.0 V394.0",
              "M555.0 456.0 V471.0 H940.0 V484.0",
              "M940.0 546.0 V561.0 H555.0 V574.0",
              "M555.0 636.0 V664.0",
              "M555.0 728.0 V810.0 H165.0 V826.0",
              "M165.0 888.0 V903.0 H555.0 V916.0",
              "M555.0 978.0 V1006.0",
              "M555.0 1068.0 V1083.0 H940.0 V1096.0",
              "M940.0 1158.0 V1173.0 H555.0 V1186.0",
              "M555.0 1248.0 V1276.0",
              "M555.0 1340.0 V1422.0 H165.0 V1438.0",
              "M165.0 1500.0 V1515.0 H940.0 V1528.0",
              "M940.0 1590.0 V1672.0 H555.0 V1688.0",
              "M555.0 1750.0 V1765.0 H940.0 V1778.0",
              "M940.0 1830.0 V1845.0 H555.0 V1858.0",
              "M555.0 1910.0 V1938.0",
              "M555.0 1990.0 V2018.0"]:
        body.append(arrow(d))

    body += start_node(165, 166)

    body += system_box(22, 216, 286, 60, [
        "Register the environment: SIEM endpoint,",
        "target hosts, snapshot IDs, rule export"])

    # CHANGED: the dependency index is keyed by event key, not event type,
    # because a field-level loss has to resolve to the rules that read that
    # field. See eventkey.py, DEFAULT_TRACKED_FIELDS.
    body += system_box(352, 306, 406, 60, [
        "Import detection rules; build the",
        "event key → rule → ATT&CK index"])

    body += system_box(352, 396, 406, 60, [
        "Run 5 control captures:",
        "same stimulus, no change applied"])

    body += system_box(802, 486, 276, 60, [
        "Restore snapshot, run the stimulus,",
        "forward events to the SIEM"])

    # CHANGED: "per event type" -> "per event key".
    body += system_box(352, 576, 406, 60, [
        "Fit the noise model per event key:",
        "mean rate, variability, dispersion"])

    body += datastore(352, 666, 406, 62, [
        "« datastore »  Noise baseline",
        "+ dependency index          →  A"])

    body += action_box(22, 828, 286, 60, [
        "Define the hardening change and scope:",
        "CIS / STIG ID, hosts, atomic test IDs"])

    body += system_box(352, 918, 406, 60, [
        "Freeze and hash the run manifest: snapshot,",
        "tests, window, rule set, thresholds"])

    body += action_box(352, 1008, 406, 60, [
        "Restore snapshot, open the capture window,",
        "run the adversary simulation suite"])

    body += action_box(802, 1098, 276, 60, [
        "Endpoints emit pre-change security",
        "events; the SIEM indexes them"])

    # CHANGED: this is the box that defined the unit of analysis, and it named
    # the wrong one.
    body += action_box(352, 1188, 406, 60, [
        "Pull via the SIEM API; build the pre-change profile",
        "keyed by event type + populated tracked fields"])

    body += datastore(352, 1278, 406, 62, [
        "« datastore »  Pre-change profile",
        "(3 runs)                              →  B"])

    body += action_box(22, 1440, 286, 60, [
        "Apply the hardening change;",
        "record the change metadata"])

    body += system_box(802, 1530, 276, 60, [
        "Configuration state changes",
        "on the target hosts"])

    body += action_box(352, 1690, 406, 60, [
        "Re-run the identical manifest from",
        "the post-change snapshot"])

    body += action_box(802, 1780, 276, 50, ["Endpoints emit post-change events"])
    body += action_box(352, 1860, 406, 50, ["Build the post-change frequency profile"])
    body += datastore(352, 1940, 406, 50,
                      ["« datastore »  Post-change profile (3 runs)"])
    body += connector(555, 2040, "C")

    aria = ("Revised activity diagram, phases 0 to 3: environment setup, "
            "pre-change capture, change application, post-change capture. "
            "Events are keyed by event type plus the tracked fields that were "
            "populated.")
    return svg(SHEET_W, H, aria, body)


# ---------------------------------------------------------------- sheet 2

def sheet2() -> str:
    H = 2154
    body = chrome(H)

    body += phase_band(76, "PHASE 4  ·  DIFFERENTIAL ANALYSIS AND IMPACT "
                           "SCORING", BOARD_W)
    body += phase_band(1222, "PHASE 5  ·  REVIEW, REMEDIATE, RE-VALIDATE  ·  "
                             "a finding closes only after a passing re-run",
                       BOARD_W)
    body += header(H)

    # --- phase 4 flow -----------------------------------------------------
    for d in ["M555.0 186.0 V214.0",
              "M555.0 276.0 V304.0",
              "M555.0 402.0 V430.0",
              "M555.0 492.0 V520.0",
              "M555.0 598.0 V626.0",
              "M555.0 724.0 V752.0",
              "M555.0 830.0 V858.0",
              "M555.0 920.0 V948.0",
              "M555.0 1010.0 V1038.0",
              "M555.0 1100.0 V1128.0",
              # both "no" branches converge on the archive box
              "M758.0 354.0 H940.0 V752.0",
              "M758.0 676.0 H940.0 V752.0",
              "M940.0 814.0 V852.0"]:
        body.append(arrow(d))

    body += edge_label(570, 417, "yes")
    body += edge_label(779, 343, "no")
    body += edge_label(570, 739, "yes")
    body += edge_label(779, 665, "no")

    body += connector(555, 166, "C")

    # CHANGED: "union of event-type keys" -> "union of event keys".
    body += action_box(352, 216, 406, 60, [
        "Align the two profiles over the",
        "union of event keys"])

    body += decision(555, 354, 203, 48, [
        "Did the profile change at all?",
        "χ² on the full 2 × K table"])

    body += connector(165, 462, "A")
    body.append(arrow("M185.0 462.0 H350.0", dashed=True))
    body += edge_label(268.5, 450, "noise model + index", anchor="middle")

    body += action_box(352, 432, 406, 60, [
        "Per-key rate-ratio test against the noise model,",
        "then Benjamini-Hochberg FDR correction"])

    # CHANGED: the three conditions now sit inside the classification box,
    # where classify() applies them (differential.py:231).
    body += system_box(352, 522, 406, 76, [
        "Classify each key:  LOST · REDUCED ·",
        "UNCHANGED · NEW · INCONCLUSIVE",
        ("all three needed:  q ≤ α,  ratio ≤ 0.5,  drop > 3 × CoV", 12)])

    # CHANGED: was "Any LOST or REDUCED key below the noise floor?". The noise
    # floor is not tested here, and "below" inverted the comparison.
    body += decision(555, 676, 203, 48, [
        "Any key classified",
        "LOST or REDUCED?"])

    # NEW: field_loss_pairs(), eventkey.py:159. A real step with no box.
    body += system_box(352, 754, 406, 76, [
        "Pair LOST and NEW keys of one event type",
        "that differ only by dropped fields",
        "(field-level loss, not a stopped event)"])

    # Left as-is on purpose. See the module docstring: global_gate() returns
    # not-passed for "no change" and for "could not test" alike, and the
    # diagram must not claim a distinction the code does not make.
    body += action_box(802, 754, 276, 60, [
        "Record “no significant change”;",
        "archive the run and its manifest"])
    body += end_node(940, 874)

    body += action_box(352, 860, 406, 60, [
        "Traverse the index to the affected",
        "detection rules and ATT&CK techniques"])

    body += action_box(352, 950, 406, 60, [
        "Compute the impact score",
        "and rank the findings"])

    body += system_box(352, 1040, 406, 60, [
        "Generate remediation candidates: surviving",
        "sources, templates, draft Sigma rule"])

    body += datastore(352, 1130, 406, 62, [
        "« artifact »  Ranked blind-spot report · ATT&CK",
        "Navigator layer · CSV / JSON · run manifest"])

    # --- phase 5 flow -----------------------------------------------------
    for d in ["M555.0 1192.0 V1274.0 H1320.0 V1290.0",
              "M1320.0 1352.0 V1380.0",
              "M1195.0 1423.0 H1217.0 V1492.0",
              "M1445.0 1423.0 H1423.0 V1510.0",
              "M1423.0 1572.0 V1628.0",
              "M1217.0 1590.0 V1618.0",
              "M1122.0 1542.0 H165.0 V1618.0",
              "M1217.0 1680.0 V1730.0 H660.5 V1778.0",
              "M165.0 1680.0 V1730.0 H449.5 V1778.0",
              "M660.5 1856.0 V1871.0 H555.0 V1884.0",
              "M449.5 1856.0 V1871.0 H555.0 V1884.0",
              "M555.0 1968.0 V1996.0",
              "M705.0 1927.0 H1572.0 V1322.0 H1520.0"]:
        body.append(arrow(d))

    body += edge_label(1181, 1412, "yes", anchor="end")
    body += edge_label(1466, 1412, "no")
    body += edge_label(1232, 1605, "detection rule")
    body += edge_label(1108, 1531, "telemetry", anchor="end")
    body += edge_label(1587, 1616.5, "no · re-review")
    body += edge_label(570, 1975, "yes")

    body += action_box(1122, 1292, 396, 60, [
        "Review the ranked report and",
        "the remediation candidates"])

    body += decision(1320, 1423, 125, 41, ["Remediation required?"])
    body += decision(1217, 1542, 95, 48, ["What kind", "of fix?"])

    body += action_box(1328, 1512, 190, 60, [
        "Document and accept the",
        "residual visibility risk"])
    body += end_node(1423, 1650)

    body += system_box(22, 1620, 286, 60, [
        "Restore telemetry: audit subcategory",
        "or Sysmon configuration change"])

    body += action_box(1122, 1620, 190, 60, [
        "Author and deploy a",
        "compensating detection rule"])

    body += connector(165, 1730, "B")
    body.append(arrow("M185.0 1730.0 H350.0", dashed=True))
    body += edge_label(268.5, 1718, "pre-change profile", anchor="middle")

    body += system_box(352, 1778, 195, 76, [
        "Re-validate telemetry:",
        "new capture, re-diff against",
        "the stored pre-change profile"])

    body += system_box(563, 1778, 195, 76, [
        "Re-validate the rule:",
        "replay the same manifest,",
        "confirm the rule now fires"])

    body += decision(555, 1927, 150, 41, ["Coverage restored?"])

    body += system_box(352, 1998, 406, 60, [
        "Close the finding as FIXED; promote the",
        "profile to the accepted baseline"])
    body += end_node(555, 2108)

    aria = ("Revised activity diagram, phases 4 and 5: differential analysis, "
            "field-level loss pairing, impact scoring, review, remediation and "
            "re-validation.")
    return svg(SHEET_W, H, aria, body)


# ---------------------------------------------------------------- main

def main() -> None:
    here = Path(__file__).resolve().parent
    for name, builder in (("T1_Activity_Diagram_Revised_Sheet1", sheet1),
                          ("T1_Activity_Diagram_Revised_Sheet2", sheet2)):
        path = here / f"{name}.svg"
        path.write_text(builder(), encoding="utf-8")
        print(f"wrote {path}  ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

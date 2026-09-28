"""Generate the T1 activity diagram, both sheets, as SVG.

Run:  .venv/Scripts/python.exe thesis/T1/figures/make_activity_diagram.py

Why this file exists. The 2026-08-28 hand-drawn version described the analysis
as keyed on event type alone. The unit of analysis changed on 2026-09-04 to
event type plus populated tracked fields (DECISIONS.md). The figure was never
updated, because it had no source to update: it existed only as SVG text with
hand-computed absolute coordinates. Patching those by hand a second time would
recreate the same failure. Now the figure is generated, so a design change is a
string edit and a re-run.

WHAT CHANGED ON 2026-09-29 (DECISIONS.md 2026-09-29, OPEN-QUESTIONS 18)

  11. The pre-change profile box said "keyed by event type + populated tracked
      fields". For a short list of fields the key now also records the value,
      grouped into a few classes, so it reads "populated fields, a few by value".
      Designed, not built yet.

WHAT CHANGED LATER ON 2026-09-28: FOUR DECISIONS (DECISIONS.md, OPEN-QUESTIONS 29)

   7. The gate is no longer a decision. It was "Did the profile change at all?",
      and its "no" ended at "no blind spot found" with no key tested. 299 steady
      keys and one key falling from 198 events to 0 went down that branch. It
      is now a step: one chi-square, reported as a summary, never a filter.
   8. One attack-test list is pinned in Phase 0, with the window and repeats.
      Phase 1 no longer chooses tests, the hashed parameters must equal the
      control runs', and a key the control runs never saw is not tested.
   9. Remediation candidates are two levels: surviving sources and known
      compensating controls. Ranked discriminating fields needed captures with
      no attack suite, and the study has none.
  10. Phase 5 applies fixes by script. The telemetry fix is supplied as a
      script, and re-validation restores the snapshot and applies the change
      and the fix before capturing. The accepted baseline is the snapshot plus
      the scripts applied on top.

WHAT CHANGED ON 2026-09-28, AND WHY

A sweep of this figure against the records (WORKLOG 2026-09-28) found steps the
design requires but the figure did not draw. Sheet 1 grew by about 430 px.

   1. Phase 0 has a check on the control runs, with its own end: CONTROL RUNS
      NOT USABLE. Phase 4 checked every repetition, the control runs were never
      checked, and an empty control run hides real losses (OPEN-QUESTIONS 24).
      Designed, not built: VarianceModel.from_control() does not check yet.
   2. Phases 1 and 3 check every run after it: did every attack test complete,
      and is the stimulus fingerprint within the spread the control runs
      measured (OPEN-QUESTIONS 22; runbook Phase 6, harness requirement 3). A
      failed run is voided, recorded in the manifest, and captured again, so the
      loops read "3 valid runs". The voided path ends in a UML flow final
      (circle with an X): that path stops, the loop goes on.
   3. Phase 3 confirms inside the host that the change took effect, before the
      window opens (harness requirement 11; OPEN-QUESTIONS 28: boot-time proof
      such as Wininit event 12 never reaches the SIEM). Its run check also
      voids a run where the change was not confirmed.
   4. The hashed-parameters box follows runbook Phase 6 step 11: repeats, the
      Sysmon config hash and the versions were missing.
   5. Sheet 1 says "manifest's parameters" and "manifest's record part", the
      two parts D2 defines, where it said "run parameters" and "run record".
      Sheet 2 already said "manifest".
   6. The classify box says "1 to 29 before: INCONCLUSIVE". "Under 30" also
      covered NEW keys, which have 0 before and are tested first in _test_key().

WHAT CHANGED ON 2026-09-14, AND WHY

An outside review of this figure was checked against the code and against the
original 2026-08-15 image. DECISIONS.md 2026-09-14 records D1, D2, D3 and the
NOT_TESTABLE decision that this revision draws.

   1. The tint means one thing (D3). A tinted box is a step the proposed system
      performs, and every such step is tinted. Before, four tinted boxes sat
      outside the system lane and the per-key rate-ratio test was white: the
      tint really marked "new since 2026-08-15". Sheet.step() now refuses to
      draw a tinted box outside the Proposed System lane, or a white box inside
      it, so the meaning cannot drift again.
   2. A capture check comes before the gate, with its own end: NOT TESTABLE.
      This is capture_problem() in differential.py. Before 2026-09-14 a dead
      agent passed the gate and was reported as blind spots.
   3. The "no" branches no longer say "no significant change", which had also
      covered runs that could not be tested. Both now end at "no blind spot
      found", and that box moved from the Monitored Environment lane, where the
      2026-08-15 original put it, into the system lane.
   4. The gate states that a single key skips chi-square and is tested
      directly (global_gate(), differential.py).
   5. The classify box states LOST's conditions separately. "All three needed"
      read as applying to every class. In classify() it applies to REDUCED only.
   6. Remediation candidates end in ranked discriminating fields, not a draft
      Sigma rule (D1).
   7. Phases 2 and 3 follow D2. There is no post-change snapshot. The engineer
      supplies the change script, and each post-change run restores the
      configuration snapshot, applies the change, reboots if needed, settles,
      and only then opens the capture window.
   8. "Pull via the SIEM API" is now "Export the archived events". The lab reads
      archives.json on SIEM-01, not the indexer (lab/blueprint.md:120-121).
   9. "Close the finding as FIXED" had no arrow to its end node.
  10. The path out of "Restore telemetry" ran straight through connector B. The
      control flow and the data connector are now separate.
  11. Arrows are computed from box positions instead of typed as coordinate
      strings. The 2026-09-09 note below said adding a step is one function
      call. For boxes it was. For arrows it was not.
  12. Risk acceptance no longer ends the flow by itself. It closes the finding
      and promotes the current profile to the accepted baseline, the same as a
      passing re-validation (DECISIONS.md 2026-09-14, promotion on both).

NOT DRAWN, ON PURPOSE

  - A single-key profile whose key has fewer than 30 events is NOT_TESTABLE
    (analyse(), differential.py). A box for that corner case would crowd the
    gate, and item 4's label already says single keys are tested directly.
  - Harness housekeeping that is not a step of the method: checking the path to
    the SIEM before a run, counting the harness's own guest calls, backups
    (runbook Phase 6, harness requirements 8 to 10).

HISTORY: WHAT CHANGED ON 2026-09-09

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
     conditions inside classify(). The old label also inverted the comparison:
     reporting requires the drop to EXCEED the noise band, not fall below it.
  6. New activity: matching LOST and NEW keys of the same event type that
     differ only by dropped fields. This is field_loss_pairs() in eventkey.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from svgkit import (
    DEFS, DIVIDER, HEADER, HEADER_SUB, LANE_A, LANE_B,
    action_box, arrow, connector, datastore, decision, edge_label, end_node,
    flow_final, line, loop_frame, phase_band, rect, start_node, svg, system_box,
    text,
)

# ----------------------------------------------------------------- geometry

# Lane geometry, shared by both sheets. Widened 2026-09-14 so the Proposed
# System lane holds a second column for the outcomes that end Phase 4.
LANES = [(0, 300), (300, 660), (960, 280), (1240, 420)]
LANE_NAMES = ["Security / Systems Engineer", "Proposed System",
              "Monitored Environment", "Security Detection Engineer"]
SYSTEM_LANE = 1

ENG, ENV, DET = 150.0, 1100.0, 1450.0    # column centres in lanes 0, 2, 3
MAIN, SUB = 520.0, 845.0                 # the two columns in the system lane
MAIN_W, SUB_W, ENG_W, ENV_W = 406.0, 200.0, 264.0, 256.0

BOARD_W = 1660
SHEET_W = 1800        # room right of the board for the re-review loop
HEAD_H = 66
GAP = 2.0             # an arrowhead stops this far short of its target


@dataclass(frozen=True)
class Box:
    """Where something was drawn. Arrows are computed from these."""

    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def bot(self) -> float:
        return self.y + self.h

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.w


def lane_of(box: Box) -> int:
    """The lane a box sits in. A box across a lane boundary is a layout error."""
    for i, (x, w) in enumerate(LANES):
        if x <= box.left and box.right <= x + w:
            return i
    raise ValueError(f"box at x={box.left}..{box.right} crosses a lane boundary")


class Sheet:
    """Collects the drawing in layers, so arrows sit above frames and below boxes."""

    def __init__(self) -> None:
        self.bands: list[str] = []
        self.frames: list[str] = []
        self.arrows: list[str] = []
        self.nodes: list[str] = []

    # --- shapes -----------------------------------------------------------

    def band(self, y: float, label: str) -> None:
        self.bands += phase_band(y, label, BOARD_W)

    def frame(self, y: float, bottom: float, label: str) -> None:
        """A loop frame spanning the system and environment lanes."""
        self.frames += loop_frame(310, y, 922, bottom - y, label)

    def step(self, cx, y, w, h, rows, system: bool, size=13.5) -> Box:
        """A step. Tinted if and only if the proposed system performs it.

        D3, DECISIONS.md 2026-09-14. A tinted box must sit in the Proposed
        System lane, and a box in that lane must be tinted. Checked here
        because the tint had drifted to a third meaning by 2026-09-14 and
        nobody noticed for a month.
        """
        box = Box(cx - w / 2, y, w, h)
        in_system_lane = lane_of(box) == SYSTEM_LANE
        if system and not in_system_lane:
            raise ValueError(f"tinted step outside the Proposed System lane: {rows[0]!r}")
        if not system and in_system_lane:
            raise ValueError(f"white step inside the Proposed System lane: {rows[0]!r}")
        draw = system_box if system else action_box
        self.nodes += draw(box.x, box.y, w, h, rows, size)
        return box

    def store(self, cx, y, w, h, rows) -> Box:
        box = Box(cx - w / 2, y, w, h)
        lane_of(box)
        self.nodes += datastore(box.x, box.y, w, h, rows)
        return box

    def ask(self, cx, cy, hw, hh, rows) -> Box:
        self.nodes += decision(cx, cy, hw, hh, rows)
        return Box(cx - hw, cy - hh, 2 * hw, 2 * hh)

    def start(self, cx, cy) -> Box:
        self.nodes += start_node(cx, cy)
        return Box(cx - 13, cy - 13, 26, 26)

    def end(self, cx, cy) -> Box:
        self.nodes += end_node(cx, cy)
        return Box(cx - 14, cy - 14, 28, 28)

    def flow_end(self, cx, cy) -> Box:
        """This path ends; a surrounding loop carries on."""
        self.nodes += flow_final(cx, cy)
        return Box(cx - 11, cy - 11, 22, 22)

    def connect(self, cx, cy, letter) -> Box:
        self.nodes += connector(cx, cy, letter)
        return Box(cx - 17, cy - 17, 34, 34)

    def label(self, x, y, s, anchor="start") -> None:
        # The plate behind a label matches the lane it sits in.
        bg = "#FFFFFF"
        for i, (lx, lw) in enumerate(LANES):
            if lx <= x < lx + lw:
                bg = LANE_A if i % 2 == 0 else LANE_B
        self.nodes += edge_label(x, y, s, anchor=anchor, bg=bg)

    # --- arrows -----------------------------------------------------------

    def down(self, a: Box, b: Box) -> None:
        """Straight down from a to b. Both must share a centre line."""
        self.arrows.append(arrow(f"M{a.cx} {a.bot} V{b.y - GAP}"))

    def hop(self, a: Box, b: Box) -> None:
        """Down out of a, across to b's centre line, and down into b."""
        mid = a.bot + 15
        self.arrows.append(arrow(f"M{a.cx} {a.bot} V{mid} H{b.cx} V{b.y - GAP}"))

    def path(self, d: str, dashed: bool = False) -> None:
        self.arrows.append(arrow(d, dashed=dashed))

    # --- output -----------------------------------------------------------

    def render(self, height: float, aria: str) -> str:
        body = [rect(0, 0, SHEET_W, height, "#FFFFFF"), DEFS]
        for i, (x, w) in enumerate(LANES):
            body.append(rect(x, HEAD_H, w, height - HEAD_H,
                             LANE_A if i % 2 == 0 else LANE_B))
        body += self.bands
        body += header(height)
        body += self.frames + self.arrows + self.nodes
        return svg(SHEET_W, height, aria, body)


def header(height) -> list[str]:
    out = []
    for x, _w in LANES[1:]:
        out.append(line(x, HEAD_H, x, height, DIVIDER, 1))
    out.append(rect(0, 0, BOARD_W, HEAD_H, HEADER))
    for (x, w), name in zip(LANES, LANE_NAMES):
        cx = x + w / 2
        if name == "Monitored Environment":
            out.append(text(cx, 25, name, size=14, weight=600, fill="#FFFFFF"))
            out.append(text(cx, 44, "SIEM · Endpoints · Hypervisor", size=11,
                            weight=400, fill=HEADER_SUB, mono=True))
        else:
            out.append(text(cx, 33, name, size=14, weight=600, fill="#FFFFFF"))
    return out


# ---------------------------------------------------------------- sheet 1

def sheet1() -> str:
    s = Sheet()

    # --- phase 0 ----------------------------------------------------------
    s.band(76, "PHASE 0  ·  ENVIRONMENT SETUP  ·  runs once per environment, "
               "not per change")

    start = s.start(ENG, 150)
    # CHANGED 2026-09-28 (DECISIONS, one pinned attack-test list): the tests,
    # window and repeats are fixed here, once, so the control runs and every
    # compared run share one stimulus.
    register = s.step(ENG, 176, ENG_W, 60, [
        "Register the environment: SIEM, hosts,",
        "snapshot, rule export; pin the attack",
        "tests, window and repeats"], system=False, size=12.5)
    s.down(start, register)

    index = s.step(MAIN, 266, MAIN_W, 60, [
        "Import detection rules; build the",
        "event key → rule → ATT&CK index"], system=True)
    s.hop(register, index)

    capture0 = s.step(MAIN, 372, MAIN_W, 60, [
        "Control capture, no change applied: restore and",
        "settle, open the window, run the pinned attack tests"], system=True)
    s.down(index, capture0)

    emit0 = s.step(ENV, 462, ENV_W, 60, [
        "Endpoints emit events;",
        "the SIEM archives every one"], system=False)
    s.hop(capture0, emit0)
    s.frame(346, emit0.bot + 18, "loop  [ 5 control runs ]")

    # NEW 2026-09-28: the control runs get the same capture check as Phase 4,
    # plus a check that every attack test completed. OPEN-QUESTIONS 22 and 24.
    ctl_check = s.ask(MAIN, 600, 203, 48, [
        "Did every control run record events",
        "and complete all its attack tests?"])
    s.hop(emit0, ctl_check)

    ctl_bad = s.step(SUB, ctl_check.cy + 24, SUB_W, 76, [
        "Control runs NOT",
        "USABLE: investigate,",
        "then capture again"], system=True, size=13)
    s.path(f"M{ctl_check.right} {ctl_check.cy} H{SUB} V{ctl_bad.y - GAP}")
    s.label(ctl_check.right + 21, ctl_check.cy - 11, "no")
    s.down(ctl_bad, s.end(SUB, ctl_bad.bot + 40))

    # CHANGED 2026-09-28: also measures the spread of the stimulus fingerprint,
    # which is the tolerance the run checks in Phases 1 and 3 compare against.
    fit = s.step(MAIN, 676, MAIN_W, 76, [
        "Fit the noise model per event key: mean",
        "rate, variability, dispersion; and the spread",
        "of the stimulus fingerprint across the runs"], system=True)
    s.down(ctl_check, fit)
    s.label(MAIN + 15, ctl_check.bot + 14, "yes")

    baseline = s.store(MAIN, 782, MAIN_W, 62, [
        "« datastore »  Noise baseline + stimulus",
        "tolerance + dependency index      →  A"])
    s.down(fit, baseline)

    # --- phase 1 ----------------------------------------------------------
    s.band(882, "PHASE 1  ·  PRE-CHANGE CAPTURE")

    define = s.step(ENG, 944, ENG_W, 60, [
        "Define the run: target hosts; the",
        "tests, window and repeats as pinned"], system=False, size=13)
    s.path(f"M{MAIN} {baseline.bot} V928 H{ENG} V{define.y - GAP}")

    # D2: the hashed parameters part of the manifest. The change is not among
    # them, so the pre- and post-change runs can hash equal.
    # CHANGED 2026-09-28: the list now follows runbook Phase 6 step 11, and the
    # name follows D2's "manifest", as Sheet 2 already did.
    freeze = s.step(MAIN, 1034, MAIN_W, 76, [
        "Freeze and hash the manifest's parameters (must",
        "equal the control runs'): snapshot, tests, window,",
        "repeats, rule set, thresholds, Sysmon hash, versions"], system=True, size=13)
    s.hop(define, freeze)

    capture1 = s.step(MAIN, 1156, MAIN_W, 60, [
        "Restore the configuration snapshot and settle;",
        "open the window, run the adversary simulation suite"], system=True)
    s.down(freeze, capture1)

    emit1 = s.step(ENV, 1246, ENV_W, 60, [
        "Endpoints emit pre-change",
        "events; the SIEM archives them"], system=False)
    s.hop(capture1, emit1)

    # NEW 2026-09-28: the per-run stimulus check. OPEN-QUESTIONS 22.
    check1 = s.ask(MAIN, 1384, 203, 48, [
        "Valid run? Every attack test completed,",
        "fingerprint within the control spread"])
    s.hop(emit1, check1)
    void1 = s.step(SUB, check1.cy + 24, SUB_W, 76, [
        "VOID the run: record",
        "why in the manifest;",
        "it is captured again"], system=True, size=13)
    s.path(f"M{check1.right} {check1.cy} H{SUB} V{void1.y - GAP}")
    s.label(check1.right + 21, check1.cy - 11, "no")
    void1_end = s.flow_end(SUB, void1.bot + 36)
    s.down(void1, void1_end)

    # CHANGED 2026-09-29 (DECISIONS, item 18): a few fields are keyed by value.
    profile1 = s.step(MAIN, 1462, MAIN_W, 60, [
        "Export the archived events; build the pre-change",
        "profile: event type + populated fields, a few by value"], system=True)
    s.down(check1, profile1)
    s.label(MAIN + 15, check1.bot + 14, "yes")
    # The label stays short: a longer one ran under the arrow at x = MAIN.
    s.frame(1130, max(profile1.bot, void1_end.bot) + 14, "loop  [ 3 valid runs ]")

    pre = s.store(MAIN, 1565, MAIN_W, 62, [
        "« datastore »  Pre-change profile",
        "(3 runs)                              →  B"])
    s.down(profile1, pre)

    # --- phase 2 ----------------------------------------------------------
    # D2: the engineer supplies the change once. The system applies it inside
    # every post-change run, below.
    s.band(1665, "PHASE 2  ·  SUPPLY THE HARDENING CHANGE")

    supply = s.step(ENG, 1727, ENG_W, 60, [
        "Supply the hardening change: CIS /",
        "STIG ID and the script that applies it"], system=False, size=13)
    s.path(f"M{MAIN} {pre.bot} V1711 H{ENG} V{supply.y - GAP}")

    record = s.step(MAIN, 1817, MAIN_W, 60, [
        "Record the change ID and script hash in the",
        "manifest's record part, outside the hashed parameters"], system=True)
    s.hop(supply, record)

    # --- phase 3 ----------------------------------------------------------
    # Kept short: a longer label ran under the arrow at x = MAIN.
    s.band(1915, "PHASE 3  ·  POST-CHANGE CAPTURE  ·  change applied inside each run")

    # D2: the change and its reboot come BEFORE the window opens. The blueprint
    # and runbook had them after the start fence, inside post-change windows
    # only, which was a second difference between the phases.
    # CHANGED 2026-09-28: the change is confirmed inside the host before the
    # window opens. Runbook Phase 6, harness requirement 11; OPEN-QUESTIONS 28.
    capture2 = s.step(MAIN, 2001, MAIN_W, 94, [
        "Restore the configuration snapshot; apply the",
        "change by script, reboot if needed, and settle;",
        "confirm inside the host that it took effect;",
        "then open the window, run the identical suite"], system=True)
    s.down(record, capture2)

    emit2 = s.step(ENV, 2125, ENV_W, 60, [
        "Endpoints emit post-change",
        "events; the SIEM archives them"], system=False)
    s.hop(capture2, emit2)

    # NEW 2026-09-28: the same run check, plus the change confirmation.
    check2 = s.ask(MAIN, 2263, 203, 48, [
        "Valid run? Tests completed, fingerprint",
        "in spread, change confirmed in the host"])
    s.hop(emit2, check2)
    void2 = s.step(SUB, check2.cy + 24, SUB_W, 76, [
        "VOID the run: record",
        "why in the manifest;",
        "it is captured again"], system=True, size=13)
    s.path(f"M{check2.right} {check2.cy} H{SUB} V{void2.y - GAP}")
    s.label(check2.right + 21, check2.cy - 11, "no")
    void2_end = s.flow_end(SUB, void2.bot + 36)
    s.down(void2, void2_end)

    profile2 = s.step(MAIN, 2341, MAIN_W, 60, [
        "Export the archived events;",
        "build the post-change profile"], system=True)
    s.down(check2, profile2)
    s.label(MAIN + 15, check2.bot + 14, "yes")
    s.frame(1975, max(profile2.bot, void2_end.bot) + 14, "loop  [ 3 valid runs ]")

    post = s.store(MAIN, 2444, MAIN_W, 50, [
        "« datastore »  Post-change profile (3 runs)"])
    s.down(profile2, post)

    to_c = s.connect(MAIN, 2534, "C")
    s.down(post, to_c)

    aria = ("Revised activity diagram, phases 0 to 3: environment setup with a "
            "check on the control runs, pre-change capture, supplying the hardening "
            "change, and post-change capture in which the change is applied by script "
            "and confirmed inside each run. Each capture run is checked and a failed "
            "run is voided and captured again. Events are keyed by event type plus "
            "the tracked fields that were populated, and for a few fields their "
            "value, grouped into classes.")
    return s.render(to_c.bot + 37, aria)


# ---------------------------------------------------------------- sheet 2

def sheet2() -> str:
    s = Sheet()

    # --- phase 4 ----------------------------------------------------------
    s.band(76, "PHASE 4  ·  DIFFERENTIAL ANALYSIS AND IMPACT SCORING")

    from_c = s.connect(MAIN, 150, "C")
    align = s.step(MAIN, 190, MAIN_W, 60, [
        "Align the two profiles over the",
        "union of event keys"], system=True)
    s.down(from_c, align)

    # NEW 2026-09-14: capture_problem(), differential.py.
    check = s.ask(MAIN, 326, 203, 48, [
        "Did every repetition in both",
        "phases record any events?"])
    s.down(align, check)

    untestable = s.step(SUB, 350, SUB_W, 76, [
        "Run is NOT TESTABLE:",
        "investigate the capture,",
        "then re-run"], system=True, size=13)
    s.path(f"M{check.right} {check.cy} H{SUB} V{untestable.y - GAP}")
    s.label(check.right + 21, check.cy - 11, "no")
    s.down(untestable, s.end(SUB, 466))

    # CHANGED 2026-09-28 (DECISIONS): was the decision "Did the profile change
    # at all?", whose "no" ended at "no blind spot found" with no key tested.
    # One key lost among many steady ones passed straight through it. The
    # chi-square is now a reported summary and every key is tested.
    gate = s.step(MAIN, 466, MAIN_W, 70, [
        "Compute one χ² over the whole 2 × K profile:",
        "reported as a summary, never a filter",
        ("one key only: no χ², the key is tested directly", 11)], system=True)
    s.down(check, gate)
    s.label(MAIN + 15, check.bot + 16, "yes")

    # CHANGED 2026-09-28 (DECISIONS, one pinned attack-test list): a key the
    # control runs never saw has no noise measurement and is not tested.
    test = s.step(MAIN, 556, MAIN_W, 76, [
        "Per-key rate-ratio test against the noise model,",
        "then Benjamini-Hochberg FDR correction",
        ("a key the control runs never saw is not tested: INCONCLUSIVE", 11)],
        system=True)
    s.down(gate, test)

    s.connect(170, test.cy, "A")
    s.path(f"M187.0 {test.cy} H{test.left - GAP}", dashed=True)
    s.label(250, test.cy - 12, "noise model + index", anchor="middle")

    # CHANGED 2026-09-14: "all three needed" applies to REDUCED only.
    # classify(), differential.py.
    classify = s.step(MAIN, 670, MAIN_W, 92, [
        "Classify each key:  LOST · REDUCED ·",
        "UNCHANGED · NEW · INCONCLUSIVE",
        ("LOST: 30 or more before, 0 after, q ≤ α   ·   1 to 29 before: INCONCLUSIVE", 11),
        ("REDUCED needs all three:  q ≤ α,  ratio ≤ 0.5,  drop > 3 × CoV", 11)],
        system=True)
    s.down(test, classify)

    found = s.ask(MAIN, 838, 203, 48, [
        "Any key classified",
        "LOST or REDUCED?"])
    s.down(classify, found)

    # CHANGED 2026-09-14: was "Record no significant change" in the Monitored
    # Environment lane. The system records it, and a run that could not be
    # tested no longer arrives here.
    nothing = s.step(SUB, 872, SUB_W, 80, [
        "Record “no blind spot",
        "found” and the profile",
        "outcome; archive the",
        "run and its record"], system=True, size=13)
    s.path(f"M{found.right} {found.cy} H{SUB} V{nothing.y - GAP}")
    s.label(found.right + 21, found.cy - 11, "no")
    s.down(nothing, s.end(SUB, nothing.bot + 40))

    pair = s.step(MAIN, 914, MAIN_W, 76, [
        "Pair LOST and NEW keys of one event type",
        "that differ only by dropped fields",
        "(field-level loss, not a stopped event)"], system=True)
    s.down(found, pair)
    s.label(MAIN + 15, found.bot + 14, "yes")

    traverse = s.step(MAIN, 1018, MAIN_W, 60, [
        "Traverse the index to the affected",
        "detection rules and ATT&CK techniques"], system=True)
    s.down(pair, traverse)

    score = s.step(MAIN, 1106, MAIN_W, 60, [
        "Compute the impact score",
        "and rank the findings"], system=True)
    s.down(traverse, score)

    # CHANGED 2026-09-14 (D1): was "draft Sigma rule".
    # CHANGED 2026-09-28 (DECISIONS): ranked discriminating fields are dropped.
    # They need captures without the attack suite, and the study has none.
    remediate = s.step(MAIN, 1194, MAIN_W, 76, [
        "Generate remediation candidates:",
        "surviving sources and known",
        "compensating controls"], system=True)
    s.down(score, remediate)

    report = s.store(MAIN, 1298, MAIN_W, 62, [
        "« artifact »  Ranked blind-spot report · ATT&CK",
        "Navigator layer · CSV / JSON · run manifest"])
    s.down(remediate, report)

    # --- phase 5 ----------------------------------------------------------
    # CHANGED 2026-09-14: was "a finding closes only after a passing re-run",
    # which stopped being true when acceptance began to close findings too.
    s.band(1390, "PHASE 5  ·  REVIEW, REMEDIATE, RE-VALIDATE  ·  "
                 "a fix closes only after a passing re-run")

    review = s.step(DET, 1452, 380, 60, [
        "Review the ranked report and",
        "the remediation candidates"], system=False)
    # Turns above the phase band rather than below it, so the arrow crosses the
    # band at DET, where there is no label text.
    s.path(f"M{MAIN} {report.bot} V1374 H{DET} V{review.y - GAP}")

    need = s.ask(DET, 1580, 110, 40, ["Remediation required?"])
    s.down(review, need)

    left, right = 1330.0, 1570.0

    kind = s.ask(left, 1706, 90, 46, ["What kind", "of fix?"])
    s.path(f"M{need.left} {need.cy} H{left} V{kind.y - GAP}")
    s.label(need.left - 12, need.cy - 13, "yes", anchor="end")

    accept = s.step(right, 1660, 160, 76, [
        "Document and accept",
        "the residual",
        "visibility risk"], system=False, size=13)
    s.path(f"M{need.right} {need.cy} H{right} V{accept.y - GAP}")
    s.label(need.right + 12, need.cy - 13, "no")
    # CHANGED 2026-09-14: acceptance used to end here. It now closes the finding
    # and promotes the baseline too (DECISIONS.md 2026-09-14). The path is drawn
    # below, once the closing box exists.

    rule = s.step(left, 1780, 170, 76, [
        "Author and deploy a",
        "compensating",
        "detection rule"], system=False, size=13)
    s.down(kind, rule)
    s.label(left + 15, kind.bot + 14, "detection rule")

    # CHANGED 2026-09-28 (DECISIONS, D2 extended to Phase 5): the fix is a
    # script, like the change. A fix made once by hand was erased by the
    # snapshot restore that starts every capture, so the re-validation measured
    # the original machine and could report "restored" for a fix never tested.
    restore = s.step(ENG, 1740, ENG_W, 60, [
        "Restore telemetry: supply the fix as a",
        "script (audit or Sysmon setting)"], system=False, size=12.5)
    s.path(f"M{kind.left} {kind.cy} H{ENG} V{restore.y - GAP}")
    s.label(kind.left - 14, kind.cy - 12, "telemetry", anchor="end")

    recheck_t = s.step(MAIN - 106, 1900, 195, 110, [
        "Re-validate telemetry:",
        "restore, apply change",
        "and fix by script, confirm,",
        "capture, re-diff against",
        "the pre-change profile"], system=True, size=13)
    recheck_r = s.step(MAIN + 106, 1900, 195, 110, [
        "Re-validate the rule:",
        "replay the manifest:",
        "restore, apply the change,",
        "run the same suite, confirm",
        "the rule now fires"], system=True, size=13)

    # CHANGED 2026-09-14: this path used to run through connector B.
    s.path(f"M{ENG} {restore.bot} V1850 H{recheck_t.cx} V{recheck_t.y - GAP}")
    s.path(f"M{left} {rule.bot} V1878 H{recheck_r.cx} V{recheck_r.y - GAP}")

    s.connect(170, recheck_t.cy, "B")
    s.path(f"M187.0 {recheck_t.cy} H{recheck_t.left - GAP}", dashed=True)
    s.label(250, recheck_t.cy - 12, "pre-change profile", anchor="middle")

    restored = s.ask(MAIN, recheck_t.bot + 65, 150, 41, ["Coverage restored?"])
    join = recheck_t.bot + 14
    s.path(f"M{recheck_t.cx} {recheck_t.bot} V{join} H{MAIN} V{restored.y - GAP}")
    s.path(f"M{recheck_r.cx} {recheck_r.bot} V{join} H{MAIN} V{restored.y - GAP}")

    s.path(f"M{restored.right} {restored.cy} H1685 V{review.cy} "
           f"H{review.right + GAP}")
    # Left of the loop, because the acceptance path runs further right.
    s.label(1673, 1900, "no · re-review", anchor="end")

    # CHANGED 2026-09-14: promotes after FIXED or ACCEPTED, not FIXED only.
    # CHANGED 2026-09-28: the accepted baseline is the snapshot plus the scripts
    # applied on top, so a later run can rebuild it the same way D2 rebuilds a
    # post-change host.
    close = s.step(MAIN, restored.bot + 28, MAIN_W, 76, [
        "Close the finding as FIXED or ACCEPTED;",
        "accepted baseline = the snapshot plus the",
        "change and fix scripts applied on top"], system=True)
    s.down(restored, close)
    s.label(MAIN + 15, restored.bot + 14, "yes")

    # The acceptance path runs right of the re-review loop and below it, so the
    # two never cross.
    s.path(f"M{accept.right} {accept.cy} H1720 V{close.cy} H{close.right + GAP}")
    s.label(1100, close.cy - 12, "risk accepted", anchor="middle")

    # CHANGED 2026-09-14: this arrow was missing.
    finish = s.end(MAIN, close.bot + 40)
    s.down(close, finish)

    aria = ("Revised activity diagram, phases 4 and 5: a capture check that ends "
            "untestable runs, a whole-profile chi-square reported as a summary, "
            "per-key testing of every key and classification, field-level loss "
            "pairing, impact scoring, review, remediation by script, and "
            "re-validation.")
    return s.render(finish.bot + 30, aria)


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

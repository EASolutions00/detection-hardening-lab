"""Generate the activity diagram of the proposed system: one sheet, as SVG.

Run:  .venv/Scripts/python.exe thesis/T1/figures/make_system_activity_diagram.py

Writes T1_Activity_Diagram_Proposed_System.svg next to this file. It is Figure 2 of
the revised proposal (proposal-form-SIMPLIFIED.md, in the thesis folder).

WRITTEN 2026-11-28 (fix 9 of the outside review, docs/WORKLOG.md 2026-11-27)

It replaces the two sheets of make_activity_diagram.py. Those stay in the repo as the
FINAL diagram, marked HISTORICAL. DO NOT PRESENT. They were not relabelled, because
the revised proposal changed what the system is, not only the words:

  1. The system starts at the upload. "The capture tool is no longer a module": the
     5 modules start at the upload, and the capture script is the study's lab tool,
     described in chapter 3 (SIMPLIFIED, note 3). The old sheets drew the system
     restoring the snapshot and running the attack tests (Phases 0 to 3).
  2. One user, the Security Engineer (DECISIONS 2026-11-23, point 7). The old sheets
     had two human lanes.
  3. "The system recommends. It does not apply fixes or write detection rules"
     (SIMPLIFIED, limitation 5). The old Phase 5 had the system apply the fix by
     script and capture again.
  4. Giving a copy of the report to the SOC is shown outside the system
     (DECISIONS 2026-11-23, point 7). The old sheets did not show it.
  5. Myers' difference algorithm is step 3 (DECISIONS 2026-11-26). The old sheets did
     not show it.
  6. The review's point 9: sheet 2 said "no blind spot found", and its LOST rule
     still needed 30 events before (DECISIONS 2026-11-26 and 2026-11-27).

The proposal describes this figure: "The diagram has one user, the Security Engineer.
The engineer exports the files from the SIEM, uploads them, runs the analysis and
reads the report. Giving a copy of the report to the Security Operations Center (SOC)
is shown outside the system."

THE RULES OF THE DRAWING, KEPT FROM THE OLD SHEETS

  - D3 (DECISIONS 2026-09-14): a tinted box is a step the proposed system performs,
    and every such step is tinted. Sheet.step() refuses a tinted box outside the
    Proposed System lane and a white box inside it.
  - Arrows are computed from box positions. Sheet.render() refuses two boxes that
    overlap.
  - Solid arrows are control flow. Dashed arrows are data: here, only the copy of the
    report that leaves the system.

WHERE EACH STEP IS IN THE CODE

  Capture and export   src/capture.py (the lab tool) with telos/harness.py; the run
                       record is counts.json and run_manifest.json.
  Module 1             pipeline.compare(): voided runs left out, at least 3 valid
                       runs per phase, each stored settings hash recomputed, one hash
                       and one change for all runs, the rule files hashed by
                       rulehash.rule_folder_sha256(). A failure is a PipelineError:
                       no report is written.
  Module 2             eventkey.py (the key), myers.event_list() (merge sort) and
                       myers.joined() (a hash map of counts).
  Module 3             myers.compare_phases() (step 3); VarianceModel.from_control(),
                       which first refuses a control run with no events; then
                       differential.analyse(): capture_problem(), the chi-square
                       summary, _test_key(), classify() with Benjamini-Hochberg,
                       field_loss_pairs(). The figure draws them in this order.
  Module 4             impact.rank_impact(); report.coverage_change();
                       remediation level 1 in render_impact(), level 2 in
                       remediation_level2().
  Module 5             report.py and the four files pipeline.compare() writes.

DESIGNED, NOT BUILT (docs/LIMITATIONS.md, limit 17)

  - The window with Upload and Run Analysis (module 5). Today the analysis is a
    command, src/run.py, which calls pipeline.compare().
  - The percentage of techniques no longer detected. The report gives the techniques
    before, after and no longer detected (report.render_coverage()); the box says
    "count", not "percentage", for that reason.
  - The re-test is the same method run again on new runs. A telemetry fix is a
    script applied with the change in each new after run (D2, DECISIONS 2026-09-28),
    so the new after runs can be compared with the old control and before runs. A new
    detection rule changes the rule files, which are part of the hashed settings, so
    all the runs are captured again.

DRAWN DIFFERENTLY FROM THE PROPOSAL'S WORDS, ON PURPOSE

  - The proposal puts "checks that each run recorded events" in module 1. The code
    runs that check later, in two places, and the figure follows the code: a
    control run with no events stops the analysis with an error when the noise
    model is fitted; a run before or after the change with no events gives a report
    with the verdict NOT TESTABLE (capture_problem()). Both come after Myers.
  - Two steps the student chose to keep on 2026-09-29 stay drawn: the check on the
    control runs and the pairing of LOST and NEW keys (DECISIONS 2026-09-29).
  - The proposal puts the event key in module 2. The key is built when the lab tool
    writes the run record, by the system's own code (archive.py with eventkey.py).
    The figure keeps it in module 2, where the proposal and the system's code put it.

NOT DRAWN, ON PURPOSE

  - A profile in which no key could be tested is also NOT TESTABLE (analyse(), when
    n_tested is 0). One more branch would crowd module 3; the NOT TESTABLE box covers
    both, and its report gives the reason.
  - The verdict "KEYS LOST OR REDUCED, BUT NO TECHNIQUE THAT ALERTED BEFORE LOST ITS
    ALERTS" (report.render_verdict()). It takes the same path as BLIND SPOTS FOUND;
    only the report's first line differs.
  - Closing a finding and promoting a baseline (the old Phase 5). The system keeps no
    record between two comparisons.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from svgkit import (
    DEFS, DIVIDER, HEADER, HEADER_SUB, LANE_A, LANE_B, STROKE,
    action_box, arrow, connector, datastore, decision, edge_label, end_node,
    line, loop_frame, phase_band, rect, stack, start_node, svg, system_box, text,
)

# ----------------------------------------------------------------- geometry

LANES = [(0, 480), (480, 660), (1140, 260), (1400, 240)]
LANE_NAMES = ["Security Engineer", "Proposed System", "Monitored Environment",
              "SOC (indirect users)"]
LANE_SUBS = ["the one user: detection and systems engineers", "modules 1 to 5",
             "SIEM · Endpoints · Hypervisor", "outside the system"]
SYSTEM_LANE = 1

ENG = 240.0                    # the engineer lane's centre
ENG_L, ENG_R = 95.0, 375.0     # its left and right columns, for the response
MAIN, SUB = 700.0, 1025.0      # the two columns of the system lane
ENV = 1270.0
SOC = 1520.0
MAIN_W, SUB_W, ENG_W, ENV_W, SOC_W = 406.0, 200.0, 360.0, 230.0, 200.0

BOARD_W = 1640
SHEET_W = 1640
HEAD_H = 66
GAP = 2.0          # an arrowhead stops this far short of its target
STEP = 28.0        # the space between two stacked steps

# The capture loop spans the engineer, system and environment lanes.
FRAME_X0 = 50.0
FRAME_X1 = LANES[2][0] + LANES[2][1] - 8.0


@dataclass(frozen=True)
class Box:
    """Where something was drawn. Arrows are computed from these."""

    x: float
    y: float
    w: float
    h: float
    name: str = ""

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

    def overlaps(self, other: "Box") -> bool:
        return (self.left < other.right and other.left < self.right
                and self.y < other.bot and other.y < self.bot)


def lane_of(box: Box) -> int:
    """The lane a box sits in. A box across a lane boundary is a layout error."""
    for i, (x, w) in enumerate(LANES):
        if x <= box.left and box.right <= x + w:
            return i
    raise ValueError(f"box at x={box.left}..{box.right} crosses a lane boundary: {box.name!r}")


def object_node(x, y, w, h, rows, size=12.5):
    """A UML object node outside the system: a plain rectangle, white."""
    return [rect(x, y, w, h, "#FFFFFF", STROKE, sw=1.5, rx=2)] + \
        stack(x + w / 2, y + h / 2, rows, size)


class Sheet:
    """Collects the drawing in layers, so arrows sit above frames and below boxes."""

    def __init__(self) -> None:
        self.bands: list[str] = []
        self.frames: list[str] = []
        self.arrows: list[str] = []
        self.nodes: list[str] = []
        self.placed: list[Box] = []

    def _place(self, box: Box) -> Box:
        self.placed.append(box)
        return box

    # --- shapes -----------------------------------------------------------

    def band(self, y: float, label: str) -> None:
        self.bands += phase_band(y, label, BOARD_W)

    def frame(self, y: float, bottom: float, label: str) -> None:
        self.frames += loop_frame(FRAME_X0, y, FRAME_X1 - FRAME_X0, bottom - y, label)

    def step(self, cx, y, w, h, rows, system: bool, size=13.5) -> Box:
        """A step. Tinted if and only if the proposed system performs it (D3)."""
        first = rows[0] if isinstance(rows[0], str) else rows[0][0]
        box = Box(cx - w / 2, y, w, h, first)
        in_system_lane = lane_of(box) == SYSTEM_LANE
        if system and not in_system_lane:
            raise ValueError(f"tinted step outside the Proposed System lane: {first!r}")
        if not system and in_system_lane:
            raise ValueError(f"white step inside the Proposed System lane: {first!r}")
        draw = system_box if system else action_box
        self.nodes += draw(box.x, box.y, w, h, rows, size)
        return self._place(box)

    def store(self, cx, y, w, h, rows) -> Box:
        box = Box(cx - w / 2, y, w, h, rows[0])
        lane_of(box)
        self.nodes += datastore(box.x, box.y, w, h, rows)
        return self._place(box)

    def outside(self, cx, y, w, h, rows) -> Box:
        """An object outside the system, for example the copy the SOC receives."""
        box = Box(cx - w / 2, y, w, h, rows[-1])
        if lane_of(box) == SYSTEM_LANE:
            raise ValueError(f"an object outside the system drawn in the system lane: {rows!r}")
        self.nodes += object_node(box.x, box.y, w, h, rows)
        return self._place(box)

    def ask(self, cx, cy, hw, hh, rows) -> Box:
        self.nodes += decision(cx, cy, hw, hh, rows)
        return self._place(Box(cx - hw, cy - hh, 2 * hw, 2 * hh, rows[0]))

    def start(self, cx, cy) -> Box:
        self.nodes += start_node(cx, cy)
        return self._place(Box(cx - 13, cy - 13, 26, 26, "start"))

    def end(self, cx, cy) -> Box:
        self.nodes += end_node(cx, cy)
        return self._place(Box(cx - 14, cy - 14, 28, 28, "end"))

    def connect(self, cx, cy, letter) -> Box:
        self.nodes += connector(cx, cy, letter)
        return self._place(Box(cx - 17, cy - 17, 34, 34, f"connector {letter}"))

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
        if abs(a.cx - b.cx) > 1e-6:
            raise ValueError(f"down() needs one centre line: {a.name!r} -> {b.name!r}")
        self.arrows.append(arrow(f"M{a.cx} {a.bot} V{b.y - GAP}"))

    def hop(self, a: Box, b: Box) -> None:
        """Down out of a, across to b's centre line, and down into b."""
        mid = a.bot + 15
        self.arrows.append(arrow(f"M{a.cx} {a.bot} V{mid} H{b.cx} V{b.y - GAP}"))

    def path(self, d: str, dashed: bool = False) -> None:
        self.arrows.append(arrow(d, dashed=dashed))

    # --- output -----------------------------------------------------------

    def render(self, height: float, aria: str) -> str:
        for a, b in combinations(self.placed, 2):
            if a.overlaps(b):
                raise ValueError(f"two boxes overlap: {a.name!r} and {b.name!r}")
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
    for (x, w), name, sub in zip(LANES, LANE_NAMES, LANE_SUBS):
        cx = x + w / 2
        out.append(text(cx, 25, name, size=14, weight=600, fill="#FFFFFF"))
        out.append(text(cx, 44, sub, size=11, weight=400, fill=HEADER_SUB, mono=True))
    return out


# ---------------------------------------------------------------- the sheet

def build() -> str:
    s = Sheet()

    # --- capture and export, outside the system ---------------------------
    s.band(76, "CAPTURE AND EXPORT  ·  the engineer, with the study's lab tool  ·  "
               "outside the system")

    start = s.start(ENG, 140)
    cap = s.step(ENG, 200, ENG_W, 92, [
        "Capture a run with the study's lab tool:",
        "restore the snapshot; in an after run, apply",
        "the change by script; run the pinned attack tests",
        ("5 control runs, 3 before the change, 3 after it", 11)], system=False)
    s.down(start, cap)

    emit = s.step(ENV, cap.bot + 32, ENV_W, 60, [
        "Endpoints emit events;",
        "the SIEM archives every one"], system=False)
    s.hop(cap, emit)

    record = s.step(ENG, emit.bot + 32, ENG_W, 76, [
        "The lab tool cuts the run's window out of the",
        "exported SIEM archive and writes the run record:",
        "events, settings, test results, valid or voided"], system=False)
    s.hop(emit, record)
    # The label stays short: a longer one ran under the arrow from the start node.
    s.frame(cap.y - 24, record.bot + 18, "loop  [ 11 runs ]")

    # The re-test, at the bottom of the sheet, comes back here.
    back = s.connect(25, cap.cy, "R")
    s.path(f"M{back.right} {cap.cy} H{cap.left - GAP}")

    upload = s.step(ENG, record.bot + 48, ENG_W, 60, [
        "Upload the 11 run records and the rule files",
        "exported from the SIEM; press Run Analysis"], system=False)
    s.down(record, upload)

    # --- the analysis: modules 1 to 5 -------------------------------------
    band_b = upload.bot + 34
    s.band(band_b, "ANALYSIS  ·  the proposed system, modules 1 to 5")

    m1 = s.step(MAIN, band_b + 62, MAIN_W, 76, [
        "Module 1 · Import and run check: leave out the",
        "voided runs and name them; recompute each run's",
        "settings hash (SHA-256); hash the rule files"], system=True)
    # Turns above the band and crosses it at MAIN, clear of the band's label.
    s.path(f"M{ENG} {upload.bot} V{band_b - 14} H{MAIN} V{m1.y - GAP}")

    ok = s.ask(MAIN, m1.bot + STEP + 48, 203, 48, [
        "At least 3 valid runs per phase, one settings",
        "hash, one change, the rule files the runs used?"])
    s.down(m1, ok)

    refuse = s.step(SUB, ok.cy + 24, SUB_W, 76, [
        "Stop with an error that",
        "names the runs left out",
        "or the settings that differ"], system=True, size=13)
    s.path(f"M{ok.right} {ok.cy} H{SUB} V{refuse.y - GAP}")
    s.label(ok.right + 21, ok.cy - 11, "no")
    s.down(refuse, s.end(SUB, refuse.bot + 40))

    m2 = s.step(MAIN, ok.bot + STEP, MAIN_W, 76, [
        "Module 2 · Event keys: event type + populated",
        "fields, a few by value; each phase's runs joined",
        "into one list, sorted by merge sort"], system=True)
    s.down(ok, m2)
    s.label(MAIN + 15, ok.bot + 14, "yes")

    # Step 3 of the proposal. It lists every difference and decides nothing.
    m3 = s.step(MAIN, m2.bot + STEP, MAIN_W, 76, [
        "Module 3 · Myers' difference algorithm: the",
        "deleted and inserted events, before against after",
        ("edit distance D, noise included; it decides no key", 11)], system=True)
    s.down(m2, m3)

    # Step 4 of the proposal, the check against normal variation, starts here.
    # VarianceModel.from_control() refuses a control run with no events before it
    # fits the model (OPEN-QUESTIONS 24). The student kept this check as a step of
    # the diagram (DECISIONS 2026-09-29).
    controls = s.ask(MAIN, m3.bot + STEP + 48, 203, 48, [
        "Did every control run",
        "record any events?"])
    s.down(m3, controls)

    unusable = s.step(SUB, controls.cy + 24, SUB_W, 76, [
        "Control runs NOT",
        "USABLE: stop with an",
        "error; capture again"], system=True, size=13)
    s.path(f"M{controls.right} {controls.cy} H{SUB} V{unusable.y - GAP}")
    s.label(controls.right + 21, controls.cy - 11, "no")
    s.down(unusable, s.end(SUB, unusable.bot + 40))

    noise = s.step(MAIN, controls.bot + STEP, MAIN_W, 60, [
        "Noise model from the 5 control runs: the mean",
        "rate, dispersion and CoV of each event key"], system=True)
    s.down(controls, noise)
    s.label(MAIN + 15, controls.bot + 14, "yes")

    # capture_problem(), differential.py: the first check inside analyse(), so after
    # Myers and the noise model, as in pipeline.compare().
    events = s.ask(MAIN, noise.bot + STEP + 48, 203, 48, [
        "Did every run before and after",
        "the change record any events?"])
    s.down(noise, events)

    untestable = s.step(SUB, events.cy + 24, SUB_W, 76, [
        "Verdict NOT TESTABLE,",
        "with the reason, in",
        "the report"], system=True, size=13)
    s.path(f"M{events.right} {events.cy} H{SUB} V{untestable.y - GAP}")
    s.label(events.right + 21, events.cy - 11, "no")
    s.down(untestable, s.end(SUB, untestable.bot + 40))

    test = s.step(MAIN, events.bot + STEP, MAIN_W, 110, [
        "Test each key against the noise model: the exact",
        "test if it fell to 0, the rate-ratio test if it",
        "dropped; then the Benjamini-Hochberg correction",
        ("one χ² over the whole profile, reported as a summary only", 11),
        ("a key the control runs never saw is not tested: INCONCLUSIVE", 11)], system=True)
    s.down(events, test)
    s.label(MAIN + 15, events.bot + 14, "yes")

    # CHANGED 2026-11-28: LOST at any count (DECISIONS 2026-11-26), and a loss that
    # fails the correction is INCONCLUSIVE, not UNCHANGED (DECISIONS 2026-11-27).
    # "Needs all three" is kept from the old sheet 2: it applies to REDUCED only.
    classify = s.step(MAIN, test.bot + STEP, MAIN_W, 110, [
        "Classify each key:  LOST · REDUCED ·",
        "UNCHANGED · NEW · INCONCLUSIVE",
        ("LOST: none after, q ≤ α, at any count  ·  if q > α: INCONCLUSIVE", 11),
        ("REDUCED needs all three:  q ≤ α,  ratio ≤ 0.5,  drop > 3 × CoV", 11),
        ("a partial drop with fewer than 30 before: INCONCLUSIVE", 11)], system=True)
    s.down(test, classify)

    found = s.ask(MAIN, classify.bot + STEP + 48, 203, 48, [
        "Any key classified",
        "LOST or REDUCED?"])
    s.down(classify, found)

    # CHANGED 2026-11-28 (review point 9): was "Record no blind spot found". The
    # report never says that: an undecided key is not shown safe (DECISIONS 2026-11-27).
    nothing = s.step(SUB, found.cy + 24, SUB_W, 80, [
        "Verdict NO KEY LOST",
        "OR REDUCED, with the",
        "number of undecided",
        "keys, in the report"], system=True, size=13)
    s.path(f"M{found.right} {found.cy} H{SUB} V{nothing.y - GAP}")
    s.label(found.right + 21, found.cy - 11, "no")
    s.down(nothing, s.end(SUB, nothing.bot + 40))

    pair = s.step(MAIN, found.bot + STEP, MAIN_W, 60, [
        "Pair LOST and NEW keys of one event type that",
        "differ only by dropped fields: a field-level loss"], system=True)
    s.down(found, pair)
    s.label(MAIN + 15, found.bot + 14, "yes")

    link = s.step(MAIN, pair.bot + STEP, MAIN_W, 76, [
        "Module 4 · Link each key to the rules that read",
        "it and to their ATT&CK techniques; count the",
        "techniques no longer detected"], system=True)
    s.down(pair, link)

    # DECISIONS 2026-11-13: a ranking by three measured numbers, not a weighted
    # score. Seen or potential: DECISIONS 2026-11-27.
    rank = s.step(MAIN, link.bot + STEP, MAIN_W, 76, [
        "Rank the keys by three measured numbers, not a",
        "score: blind techniques, highest level, rules",
        ("a blind technique is seen if it alerted before, else potential", 11)],
        system=True)
    s.down(link, rank)

    recommend = s.step(MAIN, rank.bot + STEP, MAIN_W, 60, [
        "Recommend: rules that still read events seen after",
        "the change, and known compensating controls"], system=True)
    s.down(rank, recommend)

    report = s.step(MAIN, recommend.bot + STEP, MAIN_W, 76, [
        "Module 5 · Write the report: the verdict with the",
        "undecided keys, Myers, the ranked findings, the",
        "coverage change and the reproducibility record"], system=True)
    s.down(recommend, report)

    shown = s.store(MAIN, report.bot + STEP, MAIN_W, 62, [
        "« artifact »  Report on screen,",
        "CSV, JSON and ATT&CK Navigator layer"])
    s.down(report, shown)

    # --- review and response, by the engineer -----------------------------
    band_c = shown.bot + 30
    s.band(band_c, "REVIEW AND RESPONSE  ·  the engineer  ·  "
                   "the system recommends, it does not fix")

    read = s.step(ENG, band_c + 72, ENG_W, 60, [
        "Read the report: the verdict, the ranked",
        "findings and the recommendations"], system=False)
    # Crosses the band at MAIN, clear of the band's label, and turns below it.
    s.path(f"M{MAIN} {shown.bot} V{band_c + 48} H{ENG} V{read.y - GAP}")

    # DECISIONS 2026-11-23, point 7: the SOC receives a copy, outside the system.
    copy = s.step(ENG, read.bot + STEP, ENG_W, 60, [
        "Give a copy of the report to the SOC",
        "analysts and manager, outside the system"], system=False)
    s.down(read, copy)
    soc = s.outside(SOC, copy.y, SOC_W, 60, ["« artifact »", "Copy of the report"])
    s.path(f"M{copy.right} {copy.cy} H{soc.left - GAP}", dashed=True)
    s.label(ENV, copy.cy - 12, "a copy, outside the system", anchor="middle")

    need = s.ask(ENG, copy.bot + STEP + 40, 110, 40, ["Remediation required?"])
    s.down(copy, need)

    accept = s.step(ENG_L, need.bot, 150, 76, [
        "Document and accept",
        "the residual",
        "visibility risk"], system=False, size=13)
    s.path(f"M{need.left} {need.cy} H{ENG_L} V{accept.y - GAP}")
    s.label(need.left - 12, need.cy - 13, "no", anchor="end")
    s.down(accept, s.end(ENG_L, accept.bot + 40))

    kind = s.ask(ENG_R, need.bot + 86, 90, 46, ["What kind", "of fix?"])
    s.path(f"M{need.right} {need.cy} H{ENG_R} V{kind.y - GAP}")
    s.label(need.right + 12, need.cy - 13, "yes")

    # The system does not apply fixes (limitation 5): both fixes are the engineer's.
    rule = s.step(ENG_R, kind.bot + 30, 150, 76, [
        "Write and deploy a",
        "compensating",
        "detection rule"], system=False, size=13)
    s.down(kind, rule)
    s.label(ENG_R + 15, kind.bot + 14, "detection rule")

    restore = s.step(210.0, kind.cy + 34, 150, 92, [
        "Restore the",
        "telemetry: a script",
        "for the audit or",
        "Sysmon setting"], system=False, size=13)
    s.path(f"M{kind.left} {kind.cy} H{restore.cx} V{restore.y - GAP}")
    s.label(kind.left - 14, kind.cy - 12, "telemetry", anchor="end")

    retest = s.step(290.0, max(rule.bot, restore.bot) + 34, 300, 76, [
        "Re-test: capture the runs again",
        "with the fix, upload them and",
        "run the analysis again"], system=False, size=13)
    s.path(f"M{restore.cx} {restore.bot} V{retest.y - GAP}")
    s.path(f"M{rule.cx} {rule.bot} V{retest.y - GAP}")

    to_r = s.connect(retest.cx, retest.bot + 40, "R")
    s.down(retest, to_r)

    aria = ("Activity diagram of the proposed system, one user. The security engineer "
            "captures 11 runs with the study's lab tool, outside the system, while the "
            "SIEM archives the events, and uploads the run records and the rule files. "
            "The system checks the runs, builds the event keys, compares the runs "
            "before and after the change with Myers' difference algorithm, fits the "
            "noise model from the control runs, tests each key against it, classifies "
            "it, pairs keys that lost a field, links lost keys "
            "to rules and ATT&CK techniques, ranks them, recommends, and writes the "
            "report. The engineer reads it, gives a copy to the SOC outside the system, "
            "and accepts the risk or fixes the rule or the telemetry and tests again.")
    return s.render(to_r.bot + 30, aria)


# ---------------------------------------------------------------- main

def main() -> None:
    path = Path(__file__).resolve().parent / "T1_Activity_Diagram_Proposed_System.svg"
    path.write_text(build(), encoding="utf-8")
    print(f"wrote {path}  ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

"""Generate the noise floor figure.

Run:  .venv/Scripts/python.exe thesis/T1/figures/make_noise_floor_figure.py

The figure answers one question: why is a drop in event volume not automatically
a finding? Because every event key has its own run-to-run wobble, measured from
the control runs, and a drop inside that wobble proves nothing.

What was wrong with the 2026-08-28 version, checked against src/telos/ on
2026-09-09:

  1. The third row was labelled "WinSec 4104". Event 4104 is not in the Windows
     Security log. Script block logging writes to
     Microsoft-Windows-PowerShell/Operational, which is what eventkey.py:48
     says: "PowerShell-4104". A wrong log channel is worse than wrong wording,
     because it suggests the log sources were never checked.

  2. It explained INCONCLUSIVE with the wrong rule. The old figure said 4104 was
     inconclusive because it is "so rare its band spans almost everything", and
     drew a very wide band to show it. The code does not decide it that way.
     differential.py:138 reports INCONCLUSIVE when fewer than MIN_PRE_COUNT (30)
     events were seen before the change, so the test has no power. The key is
     never tested and its band never enters the decision. The row now shows the
     pre-change count, draws no band, and dashes the track to say "not measured".

  3. Rows were labelled by event type. The unit of analysis is the event key
     (DECISIONS.md 2026-09-04). All three rows now carry real keys, in exactly
     the form KeyBuilder produces, with the fields sorted.

  4. The LOST row drew its marker at roughly 4 percent of the pre-change rate.
     differential.py:146 classifies LOST only when the post-change count is
     exactly zero. The marker now sits on zero.

Caption 2 is new. The old figure showed the noise band alone, which invited the
reader to think the band is the whole decision rule. It is one of three
conditions (differential.py:231).
"""

from pathlib import Path

from svgkit import (ARROW, BAD, BAND_FILL, DEFS, DIVIDER, GOOD, INK, MUTED,
                    WARN, arrow, circle, line, rect, svg, text)

W, H = 1060, 400

LABEL_R = 360.0        # labels are right-aligned here
X0, X1 = 380.0, 820.0  # zero, and the pre-change rate
SPAN = X1 - X0
VERDICT_X = 852.0
ROW_Y = [100.0, 188.0, 276.0]


def at(ratio: float) -> float:
    """Map a post/pre rate ratio onto the track."""
    return X0 + SPAN * ratio


# Each row is one event key. The keys are written exactly as KeyBuilder emits
# them: source-eventID[fields], fields sorted, taken from DEFAULT_TRACKED_FIELDS
# in eventkey.py. Counts and ratios are illustrative.
ROWS = [
    dict(key="Sysmon-11[Image,TargetFilename]",
         sub="file create  ·  1,240 events before",
         cov=0.09, ratio=0.88, tested=True,
         verdict="no finding", colour=GOOD,
         reason="drop is inside the noise band"),
    dict(key="Sysmon-10[GrantedAccess,SourceImage,TargetImage]",
         sub="lsass handle open  ·  318 events before",
         cov=0.07, ratio=0.0, tested=True,
         verdict="LOST", colour=BAD,
         reason="zero events after the change"),
    dict(key="PowerShell-4104[Path,ScriptBlockText]",
         sub="script block  ·  12 events before",
         cov=None, ratio=0.42, tested=False,
         verdict="INCONCLUSIVE", colour=WARN,
         reason="12 is below the minimum of 30"),
]


def build() -> str:
    body = [rect(0, 0, W, H, "#FFFFFF"), DEFS]

    body.append(text(X0, 34, "OBSERVED RATE AFTER THE CHANGE, AS A SHARE OF "
                             "THE RATE BEFORE", size=11, weight=600,
                     anchor="start", fill=MUTED, mono=True, spacing="0.08em"))
    body.append(text(X0, 58, "ZERO", size=11, weight=600, anchor="start",
                     fill=MUTED, mono=True, spacing="0.08em"))
    body.append(text(X1, 58, "RATE BEFORE", size=11, weight=600,
                     fill=INK, mono=True, spacing="0.08em"))

    for row, y in zip(ROWS, ROW_Y):
        body.append(text(LABEL_R, y - 8, row["key"], size=11.5, weight=600,
                         anchor="end", fill=INK, mono=True))
        body.append(text(LABEL_R, y + 9, row["sub"], size=11, anchor="end",
                         fill=MUTED))

        # A dashed track says the key was never tested.
        body.append(line(X0, y, X1, y, DIVIDER, 1,
                         dash=None if row["tested"] else "4 4"))

        if row["tested"]:
            # The band is 3 x the key's own coefficient of variation, matching
            # NOISE_SIGMAS = 3.0 in differential.py.
            low = at(1.0 - 3.0 * row["cov"])
            body.append(rect(round(low, 1), y - 15, round(X1 - low, 1), 30,
                             BAND_FILL, rx=3))

        body.append(circle(X1, y, 6, "none", INK))
        marker = row["colour"] if row["tested"] else MUTED
        body.append(circle(round(at(row["ratio"]), 1), y, 7, marker))

        body.append(text(VERDICT_X, y - 8, row["verdict"], size=12.5,
                         weight=700, anchor="start", fill=row["colour"],
                         mono=True))
        body.append(text(VERDICT_X, y + 9, row["reason"], size=11,
                         anchor="start", fill=MUTED))

    body.append(line(X1, 70, X1, 316, INK, 1.4, dash="4 4"))
    body.append(arrow(f"M{X1} 336 H{X0 + 4}"))

    body.append(text(600, 356, "shaded band = 3 × the run-to-run variation "
                               "measured from the 5 control runs, where "
                               "nothing was changed", size=11.5, fill=MUTED))
    body.append(text(600, 374, "a drop is reported only when all three hold:  "
                               "q ≤ 0.05,   ratio ≤ 0.5,   and the drop "
                               "exceeds the band", size=11.5, fill=MUTED))

    aria = ("Three event keys compared against their measured noise band. One "
            "drop falls inside the band and is not a finding. One is zero after "
            "the change and is reported LOST. One had only 12 events before the "
            "change, below the minimum of 30, so it is never tested and is "
            "reported INCONCLUSIVE.")
    return svg(W, H, aria, body)


def main() -> None:
    path = Path(__file__).resolve().parent / "T1_Figure_Noise_Floor.svg"
    path.write_text(build(), encoding="utf-8")
    print(f"wrote {path}  ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

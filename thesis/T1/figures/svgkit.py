"""Shared drawing primitives for the T1 figures.

Every figure in this thesis is generated, never hand-authored. The reason is
recorded in DECISIONS.md 2026-09-09: a hand-drawn SVG has no source, so keeping
it in step with the code costs more than anyone will pay, and it drifts.

This module holds only the drawing parts. Each figure keeps its own layout in
its own make_*.py, because layout is the part a reader needs to see.

Coordinates are absolute and in user units. Text is centred vertically on the
value passed as y, because every box in these figures centres its label.
"""

from __future__ import annotations

# ------------------------------------------------------------------ palette

INK = "#12202E"          # body text and terminators
MUTED = "#4A5C72"        # captions and secondary labels
LANE_A = "#FBFCFD"       # odd swimlane background
LANE_B = "#F1F5F9"       # even swimlane background
BAND = "#E2E9F0"         # phase band
BAND_INK = "#4A5C72"
HEADER = "#1D3A56"       # swimlane header bar
HEADER_SUB = "#A8C2DB"
STROKE = "#7E93AC"       # ordinary box border
ACCENT = "#1D4E79"       # the proposed system's colour
SYS_FILL = "#EAF2F9"     # a step the system performs
STORE_FILL = "#F2F7FC"   # datastore and artifact
DEC_FILL = "#FBF0D6"     # decision diamond
DEC_STROKE = "#B58A2A"
ARROW = "#5A6E86"
FRAME = "#9AAABE"        # dashed loop frame
DIVIDER = "#CBD6E1"
EDGE_INK = "#3E4E63"
FRAME_INK = "#42536A"

# Verdict colours, used by the noise floor figure.
GOOD = "#2A6A50"         # not a finding
BAD = "#A03A28"          # LOST or REDUCED
WARN = "#9C6A05"         # INCONCLUSIVE
BAND_FILL = "#DEE6EF"    # the measured noise band

SANS = "'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, monospace"

LINE_H = 17.5            # vertical gap between text lines inside a box
SYS_TEXT_NUDGE = 3.0     # tinted boxes carry a left accent bar; text shifts right

DEFS = (
    '<defs>'
    '<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
    'markerHeight="7" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{ARROW}"/></marker>'
    '<marker id="ard" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
    'markerHeight="7" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>'
    '</defs>'
)


# ------------------------------------------------------------------ atoms

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13.5, weight=400, anchor="middle", fill=INK,
         mono=False, spacing=None):
    fam = MONO if mono else SANS
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}" font-family="{fam}"{ls} '
            f'dominant-baseline="middle">{esc(s)}</text>')


def rect(x, y, w, h, fill, stroke=None, sw=1.5, rx=None):
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}"']
    if rx is not None:
        parts.append(f'rx="{rx}"')
    parts.append(f'fill="{fill}"')
    if stroke:
        parts.append(f'stroke="{stroke}" stroke-width="{sw}"')
    return " ".join(parts) + "/>"


def line(x1, y1, x2, y2, stroke=DIVIDER, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


def circle(cx, cy, r, fill="none", stroke=None, sw=1.8):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s}/>'


def stack(cx, cy, rows, size):
    """Centre a stack of text rows on cy.

    A row is either a string, or (string, size) when one line needs to be
    smaller than the rest.
    """
    out = []
    top = cy - (len(rows) - 1) * LINE_H / 2
    for i, row in enumerate(rows):
        body, row_size = row if isinstance(row, tuple) else (row, size)
        out.append(text(cx, top + i * LINE_H, body, size=row_size))
    return out


# ------------------------------------------------------------------ shapes

def action_box(x, y, w, h, rows, size=13.5):
    """A plain step. White fill."""
    return [rect(x, y, w, h, "#FFFFFF", STROKE, rx=7)] + \
        stack(x + w / 2, y + h / 2, rows, size)


def system_box(x, y, w, h, rows, size=13.5):
    """A step the proposed system performs. Tinted, with an accent bar."""
    return [rect(x, y, w, h, SYS_FILL, STROKE, rx=7),
            rect(x + 1.5, y + 8, 4.5, h - 16, ACCENT, rx=2.2)] + \
        stack(x + w / 2 + SYS_TEXT_NUDGE, y + h / 2, rows, size)


def datastore(x, y, w, h, rows, size=12.5):
    return [rect(x, y, w, h, STORE_FILL, ACCENT, sw=1.6, rx=3),
            rect(x, y, 5, h, ACCENT)] + \
        stack(x + w / 2 + 2, y + h / 2, rows, size)


def decision(cx, cy, hw, hh, rows, size=12.5):
    pts = f"M{cx} {cy - hh} L{cx + hw} {cy} L{cx} {cy + hh} L{cx - hw} {cy} Z"
    return [f'<path d="{pts}" fill="{DEC_FILL}" stroke="{DEC_STROKE}" '
            f'stroke-width="1.6"/>'] + stack(cx, cy, rows, size)


def arrow(d, dashed=False):
    marker = "ard" if dashed else "ar"
    colour = ACCENT if dashed else ARROW
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.6"'
            f'{dash} marker-end="url(#{marker})"/>')


def edge_label(x, y, s, anchor="start", bg=LANE_A):
    """Small caption sitting on a connector, with a plate behind it."""
    w = 3.9 * len(s) + 14.0
    rx = x - 7 if anchor == "start" else x - w + 7 if anchor == "end" else x - w / 2
    return [rect(rx, y - 8, round(w, 1), 16, bg, rx=3),
            text(x, y, s, size=10.5, weight=600, anchor=anchor,
                 fill=EDGE_INK, mono=True)]


def loop_frame(x, y, w, h, label):
    lw = 7.2 * len(label) + 18.0
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" '
            f'stroke="{FRAME}" stroke-width="1.4" stroke-dasharray="7 5"/>',
            rect(x, y - 9.5, round(lw, 1), 19, "#DDE5EE", rx=4),
            text(x + 9, y, label, size=10.5, weight=600, anchor="start",
                 fill=FRAME_INK, mono=True, spacing="0.06em")]


def phase_band(y, label, width):
    return [rect(0, y, width, 32, BAND),
            text(14, y + 16, label, size=11.5, weight=600, anchor="start",
                 fill=BAND_INK, mono=True, spacing="0.09em")]


def connector(cx, cy, letter):
    return [circle(cx, cy, 17, "#FFFFFF", ACCENT),
            text(cx, cy, letter, size=14, weight=700, fill=ACCENT, mono=True)]


def start_node(cx, cy):
    return [circle(cx, cy, 13, INK)]


def end_node(cx, cy):
    return [circle(cx, cy, 14, "none", INK), circle(cx, cy, 8.5, INK)]


def svg(width, height, aria, body):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" xmlns="http://www.w3.org/2000/svg" '
            f'aria-label="{esc(aria)}" class="dg">'
            + "".join(body) + "</svg>\n")

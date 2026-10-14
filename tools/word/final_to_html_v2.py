"""Convert proposal-form-FINAL.md into an HTML page for copying into Word.

Reads FINAL, writes one HTML file beside it, changes nothing else.
Handles only the Markdown that FINAL uses: headings, paragraphs, pipe tables,
numbered and bulleted lists, bold, italic, code spans, horizontal rules.
Then checks that every word of FINAL's text appears in the HTML, in order.

Version 2, chat 27d2595d, 2026-10-12: FINAL now carries its own figure markers,
one "[INSERT FIGURE: <file>]" line per figure, each followed by an italic
caption. Each marker becomes a bold paragraph. The old built-in pair of markers
for the activity diagram is gone. Exactly four markers are required.
"""

import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

FOLDER = Path(r"E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)")
SRC = FOLDER / "proposal-form-FINAL.md"
OUT = FOLDER / "proposal-form-FINAL-for-Word.html"

MARKER = "[INSERT FIGURE:"
EXPECTED_FIGURES = 4


def inline(text: str) -> str:
    """Escape, then bold and italic. Code spans become plain text."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    return text


def cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


LIST_ITEM = re.compile(r"^(\d+)\.\s+(.*)$|^[-*]\s+(.*)$")


def convert(lines: list[str]) -> tuple[str, dict]:
    out, counts = [], {"headings": 0, "paragraphs": 0, "tables": 0, "lists": 0, "figures": 0}
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        if not line.strip() or line.strip() == "---" or line.startswith(">"):
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            counts["headings"] += 1
            i += 1
            continue
        if line.startswith(MARKER):
            out.append(f"<p><b>{html.escape(line.strip(), quote=False)}</b></p>")
            counts["figures"] += 1
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            header, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c) for c in r)]
            t = ["<table>"]
            if any(header):
                t.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr>")
            for r in body:
                if len(r) != len(header):
                    sys.exit(f"Table row has {len(r)} cells, header has {len(header)}: {r}")
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</table>")
            out.append("\n".join(t))
            counts["tables"] += 1
            continue
        m = LIST_ITEM.match(line)
        if m:
            ordered = m.group(1) is not None
            tag = "ol" if ordered else "ul"
            start = int(m.group(1)) if ordered else 1
            items = []
            while i < n:
                cur = lines[i].rstrip()
                lm = LIST_ITEM.match(cur)
                if lm and (lm.group(1) is not None) == ordered:
                    items.append(lm.group(2) if ordered else lm.group(3))
                    i += 1
                elif cur.startswith("  ") and cur.strip() and items:
                    items[-1] += " " + cur.strip()
                    i += 1
                elif not cur.strip():
                    j = i
                    while j < n and not lines[j].strip():
                        j += 1
                    nxt = LIST_ITEM.match(lines[j].rstrip()) if j < n else None
                    if nxt and (nxt.group(1) is not None) == ordered:
                        i = j
                    else:
                        break
                else:
                    break
            attr = f' start="{start}"' if ordered and start != 1 else ""
            out.append(f"<{tag}{attr}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            counts["lists"] += 1
            continue
        para = []
        while i < n and lines[i].strip() and not lines[i].startswith(("|", "#", ">", MARKER)) \
                and lines[i].strip() != "---" and not LIST_ITEM.match(lines[i].rstrip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
        counts["paragraphs"] += 1
    return "\n".join(out), counts


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag not in ("b", "i"):
            self.parts.append(" ")

    def handle_data(self, data):
        self.parts.append(data)


def words_md(lines: list[str]) -> list[str]:
    kept = []
    for line in lines:
        s = line.strip()
        if s.startswith(">") or s == "---" or re.fullmatch(r"\|?(\s*:?-+:?\s*\|)+\s*", s):
            continue
        s = re.sub(r"^#{1,6}\s+", "", s)
        s = re.sub(r"^(\d+\.|[-*])\s+", "", s)
        s = s.replace("**", "").replace("`", "").replace("|", " ")
        kept.append(s)
    joined = " ".join(kept)
    joined = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", joined)
    return joined.split()


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    body, counts = convert(lines)
    if counts["figures"] != EXPECTED_FIGURES:
        sys.exit(f"Found {counts['figures']} figure markers, expected {EXPECTED_FIGURES}. Nothing written.")
    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Research Topic Proposal Form</title>
<style>
body {{ max-width: 52em; margin: 2em auto; padding: 0 1em; line-height: 1.4; }}
table {{ border-collapse: collapse; margin: 0.6em 0; }}
th, td {{ border: 1px solid #000; padding: 4px 6px; vertical-align: top; text-align: left; }}
th {{ font-weight: bold; }}
</style></head><body>
{body}
</body></html>
"""
    OUT.write_text(page, encoding="utf-8")

    p = Text()
    p.feed(body)
    got_wo_fig = "".join(p.parts).split()
    want = words_md(lines)
    print(f"Wrote {OUT.name}: {counts['headings']} headings, {counts['paragraphs']} paragraphs, "
          f"{counts['tables']} tables, {counts['lists']} lists, {counts['figures']} figure markers")
    if got_wo_fig == want:
        print(f"Word check: PASS, all {len(want)} words of FINAL are in the HTML, in the same order")
    else:
        k = next((j for j, (a, b) in enumerate(zip(want, got_wo_fig)) if a != b), min(len(want), len(got_wo_fig)))
        print(f"Word check: FAIL at word {k}: FINAL has {want[k-3:k+5]}, HTML has {got_wo_fig[k-3:k+5]}")
        print(f"FINAL {len(want)} words, HTML {len(got_wo_fig)} words")


if __name__ == "__main__":
    main()

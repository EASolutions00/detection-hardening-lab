"""Convert T1-REVISIONS-LIST.md into an HTML page for copying into Word.

Reads the revisions list, writes one HTML file beside it, changes nothing else.
Adapted from chat 5e235b74's final_to_html.py (2026-10-07), which made FINAL's copy.
Handles the Markdown the list uses: headings, paragraphs, numbered and bulleted
lists, bold, italic, code spans, horizontal rules. The header block of
"**Label:** value" lines stays one line each. Then checks that every word of the
list appears in the HTML, in order.
"""

import html
import re
from html.parser import HTMLParser
from pathlib import Path

FOLDER = Path(r"E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)")
SRC = FOLDER / "T1-REVISIONS-LIST.md"
OUT = FOLDER / "T1-REVISIONS-LIST-for-Word.html"

LABEL_LINE = re.compile(r"^\*\*[^*]+:\*\* ")
LIST_ITEM = re.compile(r"^(\d+)\.\s+(.*)$|^[-*]\s+(.*)$")


def inline(text: str) -> str:
    """Escape, then bold and italic. Code spans become plain text."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    return text


def convert(lines: list[str]) -> tuple[str, dict]:
    out, counts = [], {"headings": 0, "paragraphs": 0, "lists": 0}
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        if not line.strip() or line.strip() == "---":
            i += 1
            continue
        if line.startswith(("|", ">")):
            raise SystemExit(f"Unexpected table or quote at line {i + 1}. Nothing written.")
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            counts["headings"] += 1
            i += 1
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
        while i < n and lines[i].strip() and not lines[i].startswith(("|", "#", ">")) \
                and lines[i].strip() != "---" and not LIST_ITEM.match(lines[i].rstrip()):
            para.append(lines[i].strip())
            i += 1
        if len(para) > 1 and all(LABEL_LINE.match(p) for p in para):
            for p in para:
                out.append(f"<p>{inline(p)}</p>")
                counts["paragraphs"] += 1
        else:
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
        if s == "---":
            continue
        s = re.sub(r"^#{1,6}\s+", "", s)
        s = re.sub(r"^(\d+\.|[-*])\s+", "", s)
        s = s.replace("**", "").replace("`", "")
        kept.append(s)
    joined = " ".join(kept)
    joined = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", joined)
    return joined.split()


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    body, counts = convert(lines)
    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>T1 Proposal: List of Revisions</title>
<style>
body {{ max-width: 52em; margin: 2em auto; padding: 0 1em; line-height: 1.4; }}
</style></head><body>
{body}
</body></html>
"""
    OUT.write_text(page, encoding="utf-8")

    p = Text()
    p.feed(body)
    got = "".join(p.parts).split()
    want = words_md(lines)
    print(f"Wrote {OUT.name}: {counts['headings']} headings, {counts['paragraphs']} paragraphs, "
          f"{counts['lists']} lists")
    if got == want:
        print(f"Word check: PASS, all {len(want)} words of the list are in the HTML, in the same order")
    else:
        k = next((j for j, (a, b) in enumerate(zip(want, got)) if a != b), min(len(want), len(got)))
        print(f"Word check: FAIL at word {k}: list has {want[k-3:k+5]}, HTML has {got[k-3:k+5]}")
        print(f"List {len(want)} words, HTML {len(got)} words")


if __name__ == "__main__":
    main()

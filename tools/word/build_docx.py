"""Build the updated Word file of the T1 proposal.

Starts from a COPY of the student's formatted Word file (the template filled in) and brings its
text up to proposal-form-FINAL.md, keeping the student's formatting. The original file is only read.

1. Changed sentences are replaced inside their paragraphs (runs merged first, formatting kept).
2. Missing blocks are copied from FINAL and written in the student's paragraph format:
   the two "Why" paragraphs and Figure 1 after the algorithms table; Figure 2 in the variance-floor
   section; the Activity Diagram section with Figures 3 and 4, and Scope and Limitations, in
   Project Context; the Importance paragraphs; the note on build order after the Gantt chart.
3. Figures are embedded as SVG with a PNG fallback.
Kept as the student formatted them: uppercase study titles without field labels, "(year)" after
the authors, full month names, green Gantt cells instead of X, lettered A/B/C lists, the template's
"Function/Role" label.
"""

import html
import re
import shutil
import sys
import zipfile
from pathlib import Path

DOCS = Path(r"E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)")
SRC = DOCS / "FINAL Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential Analysis Algorithm.docx"
OUT = DOCS / "FINAL Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential Analysis Algorithm (updated 2026-10-12).docx"
MD = DOCS / "proposal-form-FINAL.md"
BUILD = Path(__file__).resolve().parent / "docx_build"

EMU = 914400
FIG_W_IN = 5.3  # the content column is 7925 twips (5.5 in) wide, less cell margins

FIGURES = {  # file stem -> (pixel width, pixel height)
    "T1_Figure_Analysis_Pipeline": (1020, 878),
    "T1_Figure_Noise_Floor": (1060, 400),
    "T1_Activity_Diagram_Revised_Sheet1": (1800, 2588),
    "T1_Activity_Diagram_Revised_Sheet2": (1800, 2304),
}

PPR = '<w:pPr><w:spacing w:before="60" w:after="60"/><w:ind w:left="0" w:firstLine="0"/><w:jc w:val="both"/></w:pPr>'
PPR_CENTER = '<w:pPr><w:spacing w:before="60" w:after="60"/><w:ind w:left="0" w:firstLine="0"/><w:jc w:val="center"/></w:pPr>'
INDENT_RUNS = '<w:r><w:t xml:space="preserve">          </w:t></w:r><w:r><w:t xml:space="preserve"> </w:t></w:r>'
LIMITS_NUMID = "12"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def run(text: str, bold=False, italic=False) -> str:
    rpr = ""
    if bold or italic:
        rpr = "<w:rPr>" + ("<w:b/><w:bCs/>" if bold else "") + ("<w:i/><w:iCs/>" if italic else "") + "</w:rPr>"
    return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


TOKEN = re.compile(r"\*\*(.+?)\*\*|(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])|`([^`]+)`")


def md_runs(text: str, italic_all=False) -> str:
    out, pos = [], 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            out.append(run(text[pos:m.start()], italic=italic_all))
        if m.group(1) is not None:
            out.append(run(m.group(1), bold=True, italic=italic_all))
        elif m.group(2) is not None:
            out.append(run(m.group(2), italic=True))
        else:
            out.append(run(m.group(3), italic=italic_all))
        pos = m.end()
    if pos < len(text):
        out.append(run(text[pos:], italic=italic_all))
    return "".join(out)


def p_empty() -> str:
    return f"<w:p>{PPR}</w:p>"


def p_text(text: str, indent: bool) -> str:
    return f"<w:p>{PPR}{INDENT_RUNS if indent else ''}{md_runs(text)}</w:p>"


def p_heading(text: str) -> str:
    ppr = PPR.replace("</w:pPr>", "<w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>")
    return f"<w:p>{ppr}{run(text, bold=True)}</w:p>"


def p_numbered(text: str) -> str:
    ppr = (f'<w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="{LIMITS_NUMID}"/>'
           f'</w:numPr><w:spacing w:before="60" w:after="60"/><w:jc w:val="both"/></w:pPr>')
    return f"<w:p>{ppr}{md_runs(text)}</w:p>"


def p_caption(text: str) -> str:
    return f"<w:p>{PPR_CENTER}{run(text, italic=True)}</w:p>"


class Figures:
    def __init__(self):
        self.next_rid, self.next_docpr, self.rels, self.media = 100, 101, [], {}

    def paragraph(self, stem: str) -> str:
        pw, ph = FIGURES[stem]
        cx = int(FIG_W_IN * EMU)
        cy = int(cx * ph / pw)
        rid_png, rid_svg = f"rId{self.next_rid}", f"rId{self.next_rid + 1}"
        self.next_rid += 2
        self.rels.append((rid_png, f"media/{stem}.png", "image"))
        self.rels.append((rid_svg, f"media/{stem}.svg", "image"))
        self.media[f"word/media/{stem}.png"] = (BUILD / f"{stem}.png").read_bytes()
        self.media[f"word/media/{stem}.svg"] = (BUILD / f"{stem}.svg").read_bytes()
        did = self.next_docpr
        self.next_docpr += 1
        drawing = (
            f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{did}" name="{stem}"/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{did}" name="{stem}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid_png}"><a:extLst><a:ext uri="{{96DAC541-7B7A-43D3-8B79-37D633B846F1}}">'
            f'<asvg:svgBlip xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main" r:embed="{rid_svg}"/>'
            f'</a:ext></a:extLst></a:blip><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            f'</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
        return f"<w:p>{PPR_CENTER}{drawing}</w:p>"


FIGS = Figures()

# ------------------------------------------------------------------ FINAL.md blocks


def md_blocks(lines):
    """Blocks separated by blank lines: heading, marker, caption, numbered, para."""
    blocks, buf = [], []

    def flush():
        if not buf:
            return
        first = buf[0].strip()
        if first.startswith("### "):
            blocks.append(("heading", first[4:]))
        elif first.startswith("[INSERT FIGURE:"):
            blocks.append(("marker", re.search(r"\[INSERT FIGURE: ([^.\]]+)\.svg\]", first).group(1)))
        elif first.startswith("*Figure"):
            blocks.append(("caption", " ".join(x.strip() for x in buf).strip("*")))
        elif re.match(r"^\d+\.\s", first):
            items, cur = [], None
            for x in buf:
                m = re.match(r"^\d+\.\s+(.*)$", x.strip())
                if m and not x.startswith(" "):
                    cur = [m.group(1)]
                    items.append(cur)
                else:
                    cur.append(x.strip())
            for it in items:
                blocks.append(("numbered", " ".join(it)))
        elif first == "---" or first.startswith("|"):
            pass
        else:
            blocks.append(("para", " ".join(x.strip() for x in buf)))
        buf.clear()

    for line in lines:
        if line.strip():
            buf.append(line.rstrip())
        else:
            flush()
    flush()
    return blocks


md = MD.read_text(encoding="utf8").splitlines()


def between(start_pred, end_pred):
    s = next(i for i, l in enumerate(md) if start_pred(l))
    e = next(i for i in range(s + 1, len(md)) if end_pred(md[i]))
    return md[s:e]


def render(blocks, first_unindented=True) -> str:
    out, since_heading = [], 0 if first_unindented else 1
    for kind, text in blocks:
        out.append(p_empty())
        if kind == "heading":
            out.append(p_heading(text))
            since_heading = 0
        elif kind == "para":
            out.append(p_text(text, indent=since_heading > 0))
            since_heading += 1
        elif kind == "numbered":
            out.append(p_numbered(text))
        elif kind == "marker":
            out.append(FIGS.paragraph(text))
        elif kind == "caption":
            out.pop()  # caption sits directly under its figure
            out.append(p_caption(text))
    return "".join(out)


# after the algorithms table: from the first line after the table to the section rule
alg = between(lambda l: l.startswith("### Algorithms to be Used"), lambda l: l.startswith("## Reasons for Choice"))
last_row = max(i for i, l in enumerate(alg) if l.startswith("|"))
ALG_AFTER = render(md_blocks(alg[last_row + 1:]), first_unindented=False)

var = between(lambda l: l.startswith("### The Variance Floor"), lambda l: l.startswith("### Features"))
var_blocks = md_blocks(var)
fig2_sentence = re.search(r"Figure 2 shows how it is used:[^.]*\.", " ".join(var)).group(0)
i_marker = next(i for i, b in enumerate(var_blocks) if b[0] == "marker")
FIG2 = render(var_blocks[i_marker:i_marker + 2])

ACTIVITY = render(md_blocks(between(lambda l: l.startswith("### Activity Diagram of the Proposed System"),
                                    lambda l: l.startswith("## Importance of the Study"))))
IMPORTANCE = render(md_blocks(between(lambda l: l.startswith("## Importance of the Study"),
                                      lambda l: l.startswith("## Target Users"))[1:]))
NOTE_LINES = between(lambda l: l.startswith("**Note on build order.**"), lambda l: not l.strip())
NOTE = render([("para", " ".join(x.strip() for x in NOTE_LINES))])

# ------------------------------------------------------------------ the document

z = zipfile.ZipFile(SRC)
parts = {n: z.read(n) for n in z.namelist()}
doc = parts["word/document.xml"].decode("utf8")

PARA = re.compile(r"<w:p(?: [^>]*)?>(?:(?!</w:p>).)*?</w:p>|<w:p/>", re.S)
RUN = re.compile(r"<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>", re.S)


def ptext(p: str) -> str:
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))


def merge_runs(p: str) -> str:
    """Merge adjacent runs that hold only text and carry identical run properties."""
    p = re.sub(r"<w:proofErr [^>]*/>", "", p)
    pieces, pos = [], 0
    for m in RUN.finditer(p):
        pieces.append(("x", p[pos:m.start()]))
        r = m.group(0)
        rpr = re.search(r"<w:rPr>.*?</w:rPr>", r, re.S)
        rpr = rpr.group(0) if rpr else ""
        body = re.sub(r"^<w:r(?: [^>]*)?>", "", r)[:-6].replace(rpr, "", 1)
        t = re.fullmatch(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", body)
        pieces.append(("t", rpr, t.group(1)) if t else ("r", r))
        pos = m.end()
    pieces.append(("x", p[pos:]))
    out, i = [], 0
    while i < len(pieces):
        pc = pieces[i]
        if pc[0] == "t":
            rpr, text, j = pc[1], pc[2], i + 1
            while j + 1 < len(pieces) and pieces[j] == ("x", "") and pieces[j + 1][0] == "t" and pieces[j + 1][1] == rpr:
                text += pieces[j + 1][2]
                j += 2
            out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{text}</w:t></w:r>')
            i = j
        else:
            out.append(pc[1])
            i += 1
    return "".join(out)


def replace(old: str, new: str, expect: int = 1):
    """Replace text inside paragraphs; old must sit inside runs of one formatting after merging."""
    global doc
    old_x, new_x, done = esc(old), esc(new), 0

    def fix(m):
        nonlocal done
        p = m.group(0)
        if old_x not in ptext(p):
            return p
        p2 = merge_runs(p)
        if old_x not in p2:
            sys.exit(f"Spans different formatting, not replaced: {old!r}")
        done += p2.count(old_x)
        return p2.replace(old_x, new_x)

    doc = PARA.sub(fix, doc)
    if done != expect:
        sys.exit(f"Expected {expect} replacement(s) of {old!r}, made {done}. Nothing written.")


def insert_after_para(containing: str, xml: str):
    global doc
    hits = [m for m in PARA.finditer(doc) if esc(containing) in ptext(m.group(0))]
    if len(hits) != 1:
        sys.exit(f"Anchor paragraph found {len(hits)} times: {containing!r}")
    doc = doc[:hits[0].end()] + xml + doc[hits[0].end():]


def insert_after_table_containing(containing: str, xml: str):
    global doc
    i = doc.find(esc(containing))
    start = doc.rfind("<w:tbl>", 0, i)
    end = doc.find("</w:tbl>", i) + len("</w:tbl>")
    if "<w:tbl>" in doc[start + 7:end]:
        sys.exit(f"Nested table inside the anchor table: {containing!r}")
    doc = doc[:end] + xml + doc[end:]


# 1. changed sentences ------------------------------------------------------------
replace("Engineers describe attacker behaviour using MITRE ATT&CK, a public catalogue of techniques",
        "Engineers describe attacker behavior using MITRE ATT&CK, a public catalog of techniques")
replace("such as the CIS Benchmarks and the DISA Security Technical Implementation Guides.",
        "such as the Center for Internet Security (CIS) Benchmarks and the Defense Information Systems Agency "
        "(DISA) Security Technical Implementation Guides (STIGs).")
replace("known attacker behaviour", "known attacker behavior")
replace("so that the activity before and after a change is the same.",
        "so that the activity before and after a change is the same. The activity diagram calls these "
        "adversary emulation tests the attack tests.")
replace("Enable LSA Protection", "Enable Local Security Authority (LSA) Protection")
replace("Reads the memory of the Windows process that holds",
        "Reads the memory of the Local Security Authority Subsystem Service (LSASS), the Windows process that holds")
replace("For the last two rows, that the change alters the logon events the rule reads is the stated effect of "
        "the change, and the first capture confirms it (unverified).",
        "For the last two rows, the change is expected to alter the logon events the rule reads; this is not yet "
        "measured, and the first laboratory capture checks it.")
replace("such as SQL injection", "such as Structured Query Language (SQL) injection")
replace("rather than to different behaviour.", "rather than to different behavior.")
replace("guarantee the same behaviour,", "guarantee the same behavior,")
replace("Sigma rules in YAML, or Wazuh rules in XML",
        "Sigma rules in YAML, a plain-text data format, or Wazuh rules in Extensible Markup Language (XML)")
replace("MIT licence", "MIT License")
replace("a CSV of the comparison, a JSON of findings",
        "a comma-separated values (CSV) file of the comparison, a JavaScript Object Notation (JSON) file of findings")
replace("change in the catalogue where", "change in the catalog where")  # bold starts at "change" here
replace("Several changes in the catalogue act", "Several changes in the catalog act")
replace("the run-to-run variance floor of the laboratory, and it is reported with the results.",
        "the run-to-run variance floor of the laboratory, and it is reported with the results. " + fig2_sentence)
replace("dispersion modelling", "dispersion modeling")
replace("representation the system analyses.", "representation the system analyzes.")
replace("SOC Analyst (Tier 1 and 2)", "Security Operations Center (SOC) Analyst (Tier 1 and 2)")
replace("Both centre on", "Both center on")
replace("Random Forest and DBSCAN into",
        "Random Forest and DBSCAN (Density-Based Spatial Clustering of Applications with Noise) into")
replace("interviews with IT experts", "interviews with information technology (IT) experts")
replace("Open-access journal; indexing status not confirmed (unverified).",
        "Open-access journal; its indexing status could not be confirmed.")

# the template's "(This is just an example.)" spans a bold and a plain run
old_caption = ('<w:t>Gantt Chart of the system documentation and development (</w:t></w:r>')
i = doc.find(old_caption)
if i < 0:
    sys.exit("Gantt caption not found. Nothing written.")
r_end = doc.find("</w:r>", i + len(old_caption)) + len("</w:r>")
if "This is just an example.)" not in doc[i:r_end]:
    sys.exit("Gantt caption second run not where expected. Nothing written.")
doc = doc[:i] + "<w:t>Gantt Chart of the system documentation and development.</w:t></w:r>" + doc[r_end:]

# 2. missing blocks ---------------------------------------------------------------
insert_after_table_containing("Algorithm / Technique", ALG_AFTER)
insert_after_para("the run-to-run variance floor of the laboratory, and it is reported with the results.", FIG2)
insert_after_para("For evaluation, the module provides a ground-truth injection facility", ACTIVITY)
insert_after_table_containing("Data Gathering: Laboratory Build", NOTE)

# Importance: the content cell of that row holds one empty paragraph; fill it
i = doc.find(">Importance of the Study<")
row_end = doc.find("</w:tr>", i)
cell2 = doc.rfind("<w:tc>", i, row_end)
seg = doc[cell2:row_end]
paras = PARA.findall(seg)
if len(paras) != 1 or ptext(paras[0]).strip():
    sys.exit("Importance content cell is not the single empty paragraph expected. Nothing written.")
seg2 = seg.replace(paras[0], IMPORTANCE.replace(p_empty(), "", 1), 1)
doc = doc[:cell2] + seg2 + doc[row_end:]

parts["word/document.xml"] = doc.encode("utf8")

# 3. relationships, content types, numbering --------------------------------------
rels = parts["word/_rels/document.xml.rels"].decode("utf8")
add = "".join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{t}"/>'
              for rid, t, _ in FIGS.rels)
parts["word/_rels/document.xml.rels"] = rels.replace("</Relationships>", add + "</Relationships>").encode("utf8")
ct = parts["[Content_Types].xml"].decode("utf8")
if 'Extension="svg"' not in ct:
    ct = ct.replace("<Default Extension=\"png\"", '<Default Extension="svg" ContentType="image/svg+xml"/><Default Extension="png"', 1)
parts["[Content_Types].xml"] = ct.encode("utf8")
num = parts["word/numbering.xml"].decode("utf8")
if f'w:numId="{LIMITS_NUMID}"' in num:
    sys.exit("numId for the limits list already exists. Nothing written.")
num = num.replace("</w:numbering>",
                  f'<w:num w:numId="{LIMITS_NUMID}"><w:abstractNumId w:val="5"/><w:lvlOverride w:ilvl="0">'
                  f'<w:startOverride w:val="1"/></w:lvlOverride></w:num></w:numbering>')
parts["word/numbering.xml"] = num.encode("utf8")
parts.update(FIGS.media)

# well-formedness check before writing
import xml.dom.minidom
for name in ["word/document.xml", "word/numbering.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"]:
    xml.dom.minidom.parseString(parts[name])

if OUT.exists():
    sys.exit(f"{OUT.name} already exists. Nothing written.")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    for name in z.namelist():
        zo.writestr(name, parts[name])
    for name, data in FIGS.media.items():
        zo.writestr(name, data)
print(f"Wrote {OUT.name}: {len(FIGS.rels) // 2} figures, document.xml {len(doc):,} characters")

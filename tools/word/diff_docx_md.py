"""Read-only: compare the words of a .docx with the words of FINAL.md and print every difference."""
import difflib
import html
import re
import sys
import zipfile

DOCX, MD = sys.argv[1], sys.argv[2]

xml = zipfile.ZipFile(DOCX).read("word/document.xml").decode("utf8")
paras = re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S)
docx_text = []
for p in paras:
    t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
    t = html.unescape(t)
    if "<w:tab/>" in p and not t.strip():
        continue
    if t.strip():
        docx_text.append(t)
dw = " ".join(docx_text).split()

lines = open(MD, encoding="utf8").read().splitlines()
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
mw = joined.split()


def norm(w):
    return w.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"') \
            .replace("–", "-").replace("—", "-").replace(" ", " ").lower()


a, b = [norm(w) for w in dw], [norm(w) for w in mw]
sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
print(f"docx words {len(dw)}, FINAL words {len(mw)}, similarity {sm.ratio():.3f}")
n = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    n += 1
    ctx = " ".join(dw[max(0, i1 - 6):i1])
    print(f"\n#{n} {tag}  ...{ctx}")
    print(f"   DOCX : {' '.join(dw[i1:i2])[:400]}")
    print(f"   FINAL: {' '.join(mw[j1:j2])[:400]}")
print(f"\n{n} differences")

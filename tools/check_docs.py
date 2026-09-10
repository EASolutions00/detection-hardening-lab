"""Flag statements in the thesis documents that contradict the code.

Run:
    .venv/Scripts/python.exe tools/check_docs.py
    .venv/Scripts/python.exe tools/check_docs.py "path/to/other/folder"

Folders are given as arguments so no personal path is committed to a public
repository. With no arguments it scans docs/ and thesis/ inside the repo.

WHY THIS EXISTS
The design changed on 2026-09-04: the unit of analysis became the event type
plus the tracked fields that were POPULATED, not the event type alone. Documents
written before that date describe a system that cannot see a field-level blind
spot, which is the case this thesis is named after. Four figures had already
drifted the same way and were only caught by reading them one at a time.

Reading nine documents by hand catches whatever the reader happens to remember.
This catches the same patterns every time.

WHAT IT IS NOT
It flags, it does not judge. A regex cannot tell a defect from a quotation of a
defect. Every hit needs a human decision, which is why each check carries the
code reference that settles it.

FILE STATUS DECIDES WHETHER A HIT MATTERS
  FROZEN      the version the panel actually read, and its exports. Old wording
              is CORRECT here. Changing it would falsify the record.
  SUPERSEDED  drafts replaced by a later file. Low priority; fix only if reused.
  LIVE        will be submitted, sent, or read by the adviser. A hit here is a
              defect.
  RECORD      the project's own logs. Old wording is correct inside a quoted
              history; new claims must match the code.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

FROZEN = {
    "proposal-form.md", "proposal.txt", "proposalll.txt",
    "proposal(ongoing verification).txt",
}
SUPERSEDED = {
    "proposal-form-REVISED.md", "T1-REVISION-DRAFT.md",
    "T1-PROPOSAL-REVISION.md",
}
LIVE = {
    "proposal-form-FINAL.md", "T1-REVISIONS-LIST.md", "T1-PANEL-RESPONSE.md",
}


def status(name: str) -> str:
    if name in FROZEN:
        return "FROZEN"
    if name in SUPERSEDED:
        return "SUPERSEDED"
    if name in LIVE:
        return "LIVE"
    return "RECORD"


# Each check: (id, regex, one-line problem, the code or record that settles it)
CHECKS = [
    ("key-values",
     r"discriminating field values|field values that detection rules|"
     r"triple of telemetry source",
     "Key defined by field VALUES.",
     "eventkey.py:113 KeySpec.present holds field NAMES. Keyed on values, "
     "every distinct command line is its own key, counts fall to 1, and "
     "MIN_PRE_COUNT=30 is never met."),

    ("key-eventtype",
     r"event-type key|event type key|keyed by event type(?! \+)|"
     r"union of event-type keys|per event type\b",
     "Says 'event type' where the unit is the event key.",
     "DECISIONS.md 2026-09-04. eventkey.py:3."),

    ("rate-window",
     r"count ?/ ?window|per minute|per min\b|/ window",
     "Rate stated per unit time.",
     "differential.py:115 computes a / n1, count per RUN. Windows are "
     "validated equal so the ratio is unaffected, but the formula differs."),

    ("lost-nonzero",
     r"LOST.{0,80}RR[= ]?0\.[0-9]|RR[= ]?0\.[0-9].{0,80}LOST",
     "A non-zero rate ratio labelled LOST.",
     "differential.py:146 classifies LOST only when the post-change count is "
     "exactly zero. A non-zero ratio is REDUCED."),

    ("inconclusive-band",
     r"band spans|too rare.{0,40}band|inconclusive.{0,60}noise band|"
     r"noise band.{0,60}inconclusive",
     "INCONCLUSIVE explained by band width.",
     "differential.py:138 reports INCONCLUSIVE when the pre-change count is "
     "below MIN_PRE_COUNT=30. The band never enters it."),

    ("channel-4104",
     r"WinSec.{0,12}4104|Security.{0,12}4104|4104.{0,30}Security log",
     "Event 4104 placed in the Security log.",
     "4104 is script block logging in Microsoft-Windows-PowerShell/"
     "Operational. eventkey.py:48 says PowerShell-4104."),

    ("field-4688",
     r"4688.{0,40}ParentImage|ParentImage.{0,40}4688",
     "ParentImage used for event 4688.",
     "4688 carries ParentProcessName. ParentImage is a Sysmon field. "
     "eventkey.py:42."),

    ("scope-ids",
     r"Suricata|network intrusion detection alert|IDS alert",
     "Network IDS content, which is out of scope.",
     "T1-REVISIONS-LIST.md Revision 14 states network IDS alerts are out of "
     "scope. No IDS source exists in DEFAULT_TRACKED_FIELDS."),

    ("noise-direction",
     r"RR\(e\) ?< ?noise_floor|below the noise floor|under the noise floor",
     "Noise floor comparison stated as 'below'.",
     "differential.py:229 requires drop > band, that is 1 - RR > 3 x CoV. "
     "Reporting needs the drop to EXCEED the band."),

    ("web-app",
     r"server-side web application|web-based application|is a web application",
     "Deployment stated as settled.",
     "Not in DECISIONS.md and not in OPEN-QUESTIONS.md. It was marked "
     "ASSUMPTION in a draft and never confirmed."),

    ("title-old",
     r"Identifying Hardening-Induced|Differential Sequence Alignment|"
     r"Using Differential Analysis Algorithm(?!\w)",
     "An older title wording.",
     "Current wording is in proposal-form-FINAL.md:16, with the article 'a'."),

    ("figure-png",
     r"T1_(Activity_Diagram_Revised_Sheet[12]|Figure_[A-Za-z_]+)\.png",
     "References a PNG render.",
     "The PNGs are renders of the superseded SVGs. The SVGs were regenerated "
     "2026-09-09; the PNGs were not."),
]

# Steps that exist in the code and should appear somewhere in a document that
# describes the method. Absence is reported per LIVE file, not per line.
EXPECTED = [
    ("field-pairing", r"pair(ing|ed)? LOST|LOST and NEW|field-level loss",
     "field_loss_pairs(), eventkey.py:159"),
    ("global-gate", r"global gate|chi-square|chi square|χ²",
     "global_gate(), differential.py:56"),
]

SUFFIXES = {".md", ".txt"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "figures"}


def disp(path: Path, repo: Path) -> str:
    """A short path that still identifies the file.

    Printing only the basename is not enough: README.md exists five times in
    this repository, and proposal-form-REVISED.md exists both here and in the
    external documents folder. Two different files must never print the same.
    """
    try:
        return str(path.relative_to(repo)).replace("\\", "/")
    except ValueError:
        return f"[ext] {path.parent.name}/{path.name}"


def gather(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            print(f"  ! missing folder, skipped: {root}")
            continue
        for p in sorted(root.rglob("*")):
            if p.suffix.lower() not in SUFFIXES or not p.is_file():
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            out.append(p)
    return out


def main() -> int:
    args = sys.argv[1:]
    repo = Path(__file__).resolve().parent.parent
    roots = [Path(a) for a in args] if args else [repo / "docs", repo / "thesis"]
    if args:
        roots = [repo / "docs", repo / "thesis"] + roots

    files = gather(roots)
    print(f"Scanned {len(files)} files in {len(roots)} folders.\n")

    compiled = [(cid, re.compile(rx, re.I), problem, ref)
                for cid, rx, problem, ref in CHECKS]

    # bucket[status][check_id] = list of (path, lineno, text)
    buckets: dict[str, dict[str, list]] = {}
    seen_expected: dict[Path, set[str]] = {}

    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            print(f"  ! unreadable: {path} ({exc})")
            continue

        st = status(path.name)
        body = "\n".join(lines)
        seen_expected[path] = {
            eid for eid, rx, _ in EXPECTED if re.search(rx, body, re.I)
        }

        for cid, rx, _problem, _ref in compiled:
            for n, line in enumerate(lines, 1):
                if rx.search(line):
                    buckets.setdefault(st, {}).setdefault(cid, []).append(
                        (path, n, line.strip()))

    order = ["LIVE", "RECORD", "SUPERSEDED", "FROZEN"]
    note = {
        "LIVE": "Will be submitted or read by the adviser. A hit here is a defect.",
        "RECORD": "Project logs. Fine inside a quoted history; check new claims.",
        "SUPERSEDED": "Replaced by a later file. Fix only if reused.",
        "FROZEN": "The version the panel read. Old wording is CORRECT here.",
    }
    lookup = {cid: (problem, ref) for cid, _rx, problem, ref in CHECKS}

    total = 0
    for st in order:
        hits = buckets.get(st)
        if not hits:
            continue
        count = sum(len(v) for v in hits.values())
        total += count
        print("=" * 78)
        print(f"{st}  ({count} hits)   {note[st]}")
        print("=" * 78)
        for cid in sorted(hits):
            problem, ref = lookup[cid]
            print(f"\n[{cid}] {problem}")
            print(f"    settled by: {ref}")
            for path, n, text in hits[cid]:
                snippet = text if len(text) <= 120 else text[:117] + "..."
                print(f"    {disp(path, repo)}:{n}")
                print(f"        {snippet}")
        print()

    print("=" * 78)
    print("MISSING STEPS in LIVE documents")
    print("=" * 78)
    for path in files:
        if status(path.name) != "LIVE":
            continue
        missing = [(eid, ref) for eid, _rx, ref in EXPECTED
                   if eid not in seen_expected.get(path, set())]
        if missing:
            print(f"\n  {disp(path, repo)}")
            for eid, ref in missing:
                print(f"      no mention of {eid}  ({ref})")
        else:
            print(f"\n  {disp(path, repo)}: all expected steps mentioned")

    print(f"\n{total} pattern hits total.")
    print("A hit is a question, not a verdict. Check each against the "
          "reference shown.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

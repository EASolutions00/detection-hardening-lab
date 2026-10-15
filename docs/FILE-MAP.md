# FILE MAP

Every place that holds work for the TeLoS T1 thesis, inside and outside this repository: what each
place holds, which files are the source and which are copies, how to make a copy again, and what
must never be committed.

Checked 2026-10-15 by listing every folder below (chat 27d2595d). Folders change. List the folder
again before trusting a line here. Private files are named, never quoted.

Status words used below:

- **SOURCE**: the original. Edit this one.
- **COPY**: made from a SOURCE. Make it again; do not edit it.
- **LIVE**: will be submitted, or read by the panel or the adviser (same meaning as in
  `tools/check_docs.py`).
- **FROZEN**: the version the panel already read. Do not change it.
- **SUPERSEDED**: replaced by a later file. Kept as a record only.
- **PRIVATE**: never goes into this public repository.

---

## 1. All locations

| # | Location | Holds | Version control | Copy elsewhere |
|---|---|---|---|---|
| 1 | REPO = `E:\Claude general` | Code, tests, records, lab configs, figure generators | git | GitHub (public) |
| 2 | DOCS = `E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)` | The submission files: FINAL, revisions list, Word file, PDF, figures | none | `claude-backups\thesis-folder-2026-10-15-sent` (full, after the submission) |
| 3 | `DOCS\prep-local` | Re-presentation scripts, study guide, title-defense transcript. PRIVATE | none | same as DOCS |
| 4 | Course folder `E:\Elijah MASTER COPY DO NOT DELETE\Documents\AMA\MAY 2025\RSCH400_CS` | The professor's lectures, the template, old drafts, reference studies | none | none found |
| 5 | `F:\TeLoS Homelab` | The lab VMs SIEM-01 and WIN-EP-01 | none (too big) | snapshots only, on the same disk |
| 6 | `C:\Users\Elijah\.telos` | Guest password files and the SSH key for SIEM-01. PRIVATE | none | none found |
| 7 | `C:\Users\Elijah\claude-backups` | Backups of documents and settings; the archive of every thesis chat | none | it is the backup |
| 8 | `C:\Users\Elijah\.claude` | Global reply rules, hooks, skills, memory, chat transcripts. PRIVATE | none | rules and settings in `claude-backups\2026-09-26` |
| 9 | github.com/EASolutions00/detection-hardening-lab | Public copy of REPO | git | |

REPO, DOCS, prep-local and the course folder are all on E:, one hard disk. C: is a different
physical drive (WORKLOG 2026-09-28, sixth), which is why the backups go there.

---

## 2. REPO, file by file (tracked in git)

| Path | What it holds | Status |
|---|---|---|
| `CLAUDE.md` | Index every chat reads first. Points at the detail | SOURCE |
| `README.md` | Public front page | SOURCE |
| `LICENSE`, `.gitignore`, `.gitattributes` | Licence; what git leaves out; line-ending rules | SOURCE |
| `requirements.txt` | Pinned Python packages. Do not upgrade mid-experiment | SOURCE |
| `.claude/settings.json` | Shared Claude Code settings for this repo | SOURCE |
| `.claude/skills/phase-closeout/SKILL.md` | Closes a runbook phase: records, commit, push | SOURCE |
| `docs/STATUS.md` | Current blockers and dates | RECORD |
| `docs/OPEN-QUESTIONS.md` | Unverified things that can change the plan, ranked | RECORD |
| `docs/DECISIONS.md` | Why choices were made; pinned versions. Never delete an entry | RECORD |
| `docs/WORKLOG.md` | What happened each session, newest first | RECORD |
| `docs/COMMANDS.md` | Every command run on this machine and its correct result. Part 5 is the pre-flight check | RECORD |
| `docs/RUNBOOK-homelab.md` | Build the lab, Phases 0 to 8 | SOURCE |
| `docs/PROMPT-new-chat.md` | Paste into a new chat to load the project | SOURCE |
| `docs/PROMPT-uwf-test.md` | Prompt for the UWF test chat. Item 19 is answered, so it is no longer used | SUPERSEDED |
| `docs/T1-PROPOSAL-REVISION.md` | First revision draft. Replaced by FINAL in DOCS | SUPERSEDED |
| `docs/T1-WALKTHROUGH.md` | Worked example of the method. Its C4 example was overtaken 2026-10-01 (banner at the top) | SOURCE |
| `docs/demo-output.txt` | Output of `src/demo.py` (COMMANDS Part 4 says how to make it) | COPY |
| `docs/FILE-MAP.md` | This file | SOURCE |
| `lab/blueprint.md` | Lab design, resource budget, the change catalogue (section 8) | SOURCE |
| `lab/configs/` | `sysmonconfig.xml`, `wazuh-agent-ossec.conf`, README. Pinned; hash them | SOURCE |
| `lab/scripts/README.md` | Rules for the hardening-change scripts. **No change script exists yet** | SOURCE |
| `lab/scripts/telos-archive` | Helper on SIEM-01 that reads and exports the Wazuh archive (never writes to it), run as root through one sudoers rule | SOURCE |
| `lab/scripts/telos-fence.cs` | Makes one process, so Sysmon marks the edge of a capture window | SOURCE |
| `src/demo.py` | Runs the whole analysis on synthetic data | SOURCE |
| `src/telos/` | The analysis package: `eventkey`, `differential`, `variance`, `baseline`, `model`, `report`, `synth`, `__init__` | SOURCE |
| `tests/` | `test_eventkey.py`, `test_differential.py`. 58 passed on 2026-10-15 | SOURCE |
| `thesis/README.md` | Proposal template and numbering rules | SOURCE |
| `thesis/T1/README.md` | The thesis summary | SOURCE |
| `thesis/T1/proposal-form.md` | The version the title panel read (also in DOCS, identical) | FROZEN |
| `thesis/T1/proposal.txt` | Early plain-text proposal | FROZEN |
| `thesis/T1/proposal-form-REVISED.md` | Earlier revision (also in DOCS, identical) | SUPERSEDED |
| `thesis/T1/figures/make_*.py`, `svgkit.py` | Generators of the four figures. `make_activity_diagram.py` **is** the diagram | SOURCE |
| `thesis/T1/figures/*.svg` | The four figures, written by the generators | COPY |
| `thesis/T2/`, `thesis/T3/` | README and proposal each. Not chosen | SUPERSEDED |
| `tools/check_docs.py` | Flags document lines that contradict the code | SOURCE |
| `tools/word/` | Markdown to Word tools. See `tools/word/README.md` | SOURCE |
| `data/runs/` | Raw capture archives. Gitignored. **Empty on 2026-10-15** (only `.gitkeep`) | |
| `data/summaries/` | Small derived CSVs, committed. Empty on 2026-10-15 | |

Not tracked, on purpose: `.venv/` (rebuild from `requirements.txt`), Python caches, and
`.claude/settings.local.json` (personal "don't ask again" choices).

**Where the raw events are.** `data/runs/` is empty. The September checks (for example 1,641 batch
logons on 2026-09-02, and 0 network logons among 2,892 logon events on 2026-09-26) were counted inside SIEM-01
from `/var/ossec/logs/archives/`. Whether those archives are still on SIEM-01's disk was not checked on
2026-10-15 (unverified). No capture run of the study exists yet.

---

## 3. DOCS, the thesis folder (outside git)

| File | What it is | Status |
|---|---|---|
| `proposal-form-FINAL.md` | The revised proposal text | SOURCE, LIVE |
| `proposal-form-FINAL-for-Word.html` | Paste-ready copy. `tools/word/final_to_html_v2.py` | COPY |
| `T1-REVISIONS-LIST.md` | What changed after the title defense, by revision. **Not submitted** (not required, 2026-10-15) | SOURCE |
| `T1-REVISIONS-LIST-for-Word.html` | Paste-ready copy. `tools/word/revisions_to_html.py` | COPY |
| `Detecting … Algorithm.docx` | **The submitted Word file.** Built 2026-10-12 by `tools/word/build_docx.py` as `FINAL … (updated 2026-10-12).docx`; saved under this name by the student 2026-10-15 with the Title and Author properties fixed. Text and pictures unchanged. The source of the submitted text | SOURCE, SUBMITTED |
| `Detecting … Algorithm.pdf` | **Submitted 2026-10-15.** Made by the student from that Word file; 30 pages; hidden title and author correct | COPY, SUBMITTED |
| `FINAL Detecting … Algorithm (updated 2026-10-12).pdf` | The 2026-10-12 PDF. Same content, but its hidden title is the template's "A Mobile Application for finding Hospital's Facilities…". Do not send | SUPERSEDED |
| `FINAL … (updated 2026-10-12).docx` and `FINAL … Algorithm.docx` (the student's own formatted file, input of `build_docx.py`) | No longer in DOCS after 2026-10-15. Both are kept in `claude-backups\thesis-folder-2026-10-15` | SUPERSEDED |
| `Detecting … Using a Differential.docx` and `.pdf` | The 2026-10-07 version, with "a" in the name | SUPERSEDED |
| `T1_Detection of Hardening-Induced Blind Spots REVISED.docx` | Earlier revision | SUPERSEDED |
| `proposal-form.md` | Same file as `thesis/T1/proposal-form.md` | FROZEN |
| `proposal-form-REVISED.md` | Same file as `thesis/T1/proposal-form-REVISED.md` | SUPERSEDED |
| `T1-REVISION-DRAFT.md` | Earlier replacement text for `proposal-form.md`, written to answer the panel | SUPERSEDED |
| `T1-PANEL-RESPONSE.md` | Each panel question with the reasoning behind the answer. Not submitted; stale in places (banner) | LIVE, not submitted |
| `ACTIVITY-DIAGRAM-EXPLAINED.md` | The diagram in plain words, for study. Not submitted | LIVE, not submitted |
| `ACTIVITY-DIAGRAM-EXPLAINED.2026-09-29.md.bak` | The explainer before the 2026-09-29 rewrite | SUPERSEDED |
| The four figure `.svg` files | Copies of `thesis/T1/figures/*.svg` (identical on 2026-10-15) | COPY |
| The four `*.2026-08-28.svg.bak` files | The figures before 2026-08-28 | SUPERSEDED |
| `T1_Activity_Diagram_Swimlane.png` | The diagram shown at the title defense | FROZEN |
| `TopicProposalFormTemplateBLANK.docx` | The school's blank template (also in the course folder). Its Title property is another thesis's title and its Author is "MaryASoriano"; a Word file made from it keeps both until changed in File, Info | SOURCE |
| `Figure 3 Activity Diagram sheet 1 (full size).pdf`, `Figure 4 Activity Diagram sheet 2 (full size).pdf` | **Submitted 2026-10-15.** The two diagram sheets at full size, one page each, with FINAL's captions and matching hidden titles. Made with Edge headless from `thesis/T1/figures/` | COPY, SUBMITTED |
| `Activity Diagram\` | Four more copies of the same four SVGs (identical on 2026-10-15) | COPY |
| `UWF Test\` | Empty folder left from the UWF test (item 19) | |
| `~$NAL Detecting … (updated 2026-10-12).docx` | Word's lock file, dated 2026-10-13. Word makes it while the file is open and removes it on close. Its Word file is gone, so it is left over and can be deleted by hand | |
| `~$tecting … Algorithm.docx` | Word's lock file for the submitted Word file, 2026-10-15 19:34: Word had it open. It goes away when Word closes | |

---

## 4. DOCS\prep-local (PRIVATE)

Removed from the public repo on 2026-09-10. Never put back.

| File | What it is | Status |
|---|---|---|
| `RE-PRESENTATION-SCRIPT 22-MIN.txt` | Teleprompter script, about 3,100 words, 24 to 26 minutes. The header lists what to skip | SOURCE |
| `RE-PRESENTATION-SCRIPT.txt` | Full script from the top, about 4,400 words; Part C has 31 answer cards | SOURCE |
| `RE-PRESENTATION-SCRIPT (formal version 2026-10-12).txt` | First, formal wording | SUPERSEDED |
| `RE-PRESENTATION-SCRIPT (question-order version 2026-10-12).txt` | Second version, ordered by panel question | SUPERSEDED |
| `STUDY-GUIDE.md` | The study plan for the diagram and the re-presentation | SOURCE |
| `DEFENSE-PREP.md` | Defense preparation notes | SOURCE |
| `Thesis Pre-oral defense transcript.txt` | Transcript of the title defense session (the file name says pre-oral) | FROZEN |
| `title-defense-script.md`, `title-defense-bullets.md`, `topic-proposal-titles.pptx` | Title defense, 2026-08-25 | FROZEN |
| `proposal(ongoing verification).txt`, `proposalll.txt` | Early proposal text | FROZEN |
| `global-CLAUDE.md.backup-2026-09-10` | Backup of the global reply rules | |

---

## 5. Course folder (read only)

`E:\Elijah MASTER COPY DO NOT DELETE\Documents\AMA\MAY 2025\RSCH400_CS`. Nothing here is edited.

- **The professor's guidelines:** `Week 1-VC-RSCH400_CS-Research Fundamentals 1.txt` and
  `WEEK 12 - VC - RSCH400_CS.txt` (lecture transcripts, checked 2026-10-12, OPEN-QUESTIONS 33), and
  the lecture videos for Weeks 1, 2 and 12.
- **Course modules and presentations:** PDFs for research fundamentals, methods of research I to III,
  related literature, sampling, sources of data, statistical tools, research writing.
- **Templates:** `TopicProposalFormTemplateBLANK` and `TopicProposalFormTemplateCS-Ver-08172023`.
- **Old drafts:** topic proposal drafts and the three title forms. All SUPERSEDED.
- **Reference studies:** two "similar research" PDFs, `SIEM DETECTION RULE SET
  OPTIMIZATION_2505.06701v1.pdf` (an arXiv preprint, OPEN-QUESTIONS 33), a Wazuh timed-automata paper,
  and a DNS-tunneling paper.
- `Final Thesis title proposal\`: title-defense era notes and Word files.
- `DRAFTS\`: an earlier, unrelated prototype. Not part of T1.
- Three Word lock files (`~$...`) and nine personal image files. Not thesis material; not listed.

---

## 6. F:\TeLoS Homelab (the VMs)

Each VM folder holds the `.vmx` settings file, a `.vmx.telos-20260903T081807Z.bak` copy of it, five
`.vmdk` disk files, four snapshots and the VMware logs. The permission rules forbid deleting
snapshots or VMs and editing these files.

| VM | Snapshots, oldest first |
|---|---|
| SIEM-01 | `phase3-complete-2026-09-02`, `timesync-off-2026-09-03`, `snapd-off-archive-v2-2026-09-03`, `uwf-test-baseline-2026-09-10` (current, with memory) |
| WIN-EP-01 | `phase3-complete-2026-09-02`, `agent-hardened-2026-09-03`, `tamper-off-2026-09-03`, `uwf-test-baseline-2026-09-10` (current, with memory) |

There is no golden snapshot yet. DC-01 does not exist yet.

**Unrecorded:** both VMs have a `.vmx.lck` lock folder dated 2026-10-08 13:10. The `vmware.log` files
did not change (last written 2026-09-26 for SIEM-01, 2026-09-11 for WIN-EP-01), so the VMs were
probably opened in VMware Workstation but not powered on (unverified). Run `vmrun -T ws list` before
the lab work starts.

---

## 7. C:\Users\Elijah\.telos (PRIVATE)

Four files: a password file for each guest VM, and the SSH key pair for SIEM-01. Commands read them
into a variable (COMMANDS.md). **Never print, echo, log or commit them.** No backup was found on
2026-10-15. If the folder is lost, every command that reads it stops working until new ones are made.

---

## 8. C:\Users\Elijah\claude-backups

| Item | What it holds |
|---|---|
| `2026-09-26\` | Global rules, global settings and the repo CLAUDE.md, saved before the Claude Code setup of that day |
| `CLAUDE-4th-year-CS-student-2026-09-19.md` | A saved instructions file of 2026-09-19. No record refers to it |
| `docs-before-fixes-2026-09-28\`, `docs-before-fixes-2026-09-28-evening\` | The four DOCS text files before the two sweeps of that day |
| `thesis-folder-end-of-day-2026-09-28\` | Full copy of DOCS on 2026-09-28 |
| `thesis-folder-2026-10-15\` | **Full copy of DOCS on the morning of 2026-10-15**, made by chat 27d2595d: 43 files, each compared equal. The Word lock file was left out. Holds the two Word files later removed from DOCS |
| `thesis-folder-2026-10-15-sent\` | **Full copy of DOCS right after the submission, 2026-10-15**: 45 files, each compared equal, lock files left out. Holds the submitted Word file and the three submitted PDFs |
| `thesis-chats\` | Kept by the private hook `thesis_log.py`: `CHAT-LOG.md` (each chat, its dates, files changed), `transcripts\` (38 files in 6 folders), `file-copies\` (changed text files from E: and F:), `state.json`, and a 2026-09-14 sweep note from chat 4e01d810 |

The hook copies text files only (`.md`, `.txt`). It does not copy `.docx`, `.pdf`, `.svg` or `.html`.
**After any change to the Word file, copy DOCS again** to a new dated folder here.

---

## 9. C:\Users\Elijah\.claude (PRIVATE)

| Item | What it does |
|---|---|
| `CLAUDE.md` | Global reply rules. Kept out of the repo on purpose |
| `hooks\check_reply.py` | Checks each reply before the turn ends and asks for a rewrite if a rule is broken |
| `hooks\thesis_log.py` | Archives each thesis chat, records hand changes in DOCS and the VM folder, lists chats with no WORKLOG entry |
| `skills\defense-brief`, `skills\review-order` | Used by the thesis rules |
| `skills\humanizer`, `skills\once-human-furnace` | Not thesis work |
| `projects\E--Claude-general\` | Transcripts of the chats opened in REPO (23 on 2026-10-15), and `memory\` |

---

## 10. Never commit

- Anything in `C:\Users\Elijah\.telos`, and any password, key or token.
- `DOCS\prep-local\`.
- Raw run data (`data/runs/*`) and VM files (`.vmdk`, `.vmsn`, `.vmem` and the rest). `.gitignore` blocks them.
- `.claude/settings.local.json` and the global `CLAUDE.md`.
- The personal files in the course folder.

---

## 11. Copies, and how to make each one again

| Copy | Made from | How |
|---|---|---|
| `thesis/T1/figures/*.svg` | the `make_*.py` beside them | `.venv/Scripts/python.exe thesis/T1/figures/make_<name>.py`; each writes its SVG beside itself |
| The SVGs in DOCS and `DOCS\Activity Diagram\` | `thesis/T1/figures/*.svg` | Copy by hand, then compare (for example `cmp`) |
| The two `-for-Word.html` files | FINAL and the revisions list | `tools/word/` (see its README) |
| The submitted Word file | the student's formatted Word file, FINAL, the figures | `tools/word/build_docx.py`, one time only (2026-10-12). The Word file is now the source |
| The submitted PDF | the submitted Word file | Word, Save As PDF (the student). Check Title and Author in File, Info first |
| The two diagram PDFs | `thesis/T1/figures/` Sheet 1 and Sheet 2 | Edge headless `--print-to-pdf` of an HTML page with the SVG at its own size, the caption and a `<title>` (WORKLOG 2026-10-15) |
| `docs/demo-output.txt` | `src/demo.py` | COMMANDS.md Part 4 |

---

## 12. Loose ends found on 2026-10-15

1. **Submission.** Done 2026-10-15 (student), after the latest date, 2026-10-12. Sent: the proposal's PDF and
   the two full-size diagram PDFs. The revisions list was not sent (not required), so it has no Word or PDF
   copy. Fixed before sending: the template's wrong Title and Author properties (section 3).
2. **VM lock folders** dated 2026-10-08 13:10, with no record (section 6).
3. **A left-over Word lock file** in DOCS, `~$NAL …` (section 3). Delete by hand.
4. **The Word file and PDF had no copy off drive E:.** Fixed 2026-10-15: `thesis-folder-2026-10-15`, then
   `thesis-folder-2026-10-15-sent` after the submission. The next change needs a new copy (section 8).
5. **The five Word tools existed only in a temporary chat folder.** Fixed 2026-10-15: `tools/word/`.
6. **Chat ce64480d** (`E:\MISC\tools\meeting-copilot`) is on the hook's list of chats with no WORKLOG
   entry. It ran outside the three thesis folders. Chat 27d2595d did not read it.
7. **The course folder and `.telos` have no backup** that was found.
8. **The September raw archives** may exist only inside SIEM-01 (section 2, unverified).

# Work Log

What actually happened, session by session. Newest at the top.

This exists because you forget things. Write an entry every time you sit down, even a short
one. "Tried X, it failed, here is the error" is worth more later than a clean summary.

Template:

```
## YYYY-MM-DD - short title
Did:
Result:
Broke / stuck on:
Next:
```

---

## 2026-08-31 (second session) - Built the analysis core. First code in the repo.

**Did:** Wrote stages 2, 3 and 5 of the pipeline in Python, with tests, running on synthetic
data. No lab involved.

**The decision that made this possible:** the analyser consumes event counts and does not care
where they came from. So only stage 1 (acquisition) needs the lab. Recorded in DECISIONS.md.

**Files written:**

| File | Holds |
|---|---|
| `src/blindspot/model.py` | `Phase`, `Finding`, `Classification`, `AnalysisResult` |
| `src/blindspot/variance.py` | Noise floor: CoV and dispersion from the control runs |
| `src/blindspot/differential.py` | The core: align, global gate, rate ratio, BH, classify |
| `src/blindspot/baseline.py` | Naive differencing, the comparison baseline |
| `src/blindspot/report.py` | Text rendering |
| `src/blindspot/synth.py` | Synthetic count generator |
| `src/demo.py` | End-to-end run |
| `tests/test_differential.py` | 20 tests |

**Result:** 20 tests pass. The demo reproduces the headline claim on synthetic data:

```
  method                       TP   FP   FN  precision   recall      F1
  naive differencing            2    8    0     20.0%  100.0%   0.333
  proposed system               2    0    0    100.0%  100.0%   1.000
```

Full output saved to [demo-output.txt](demo-output.txt).

**BROKE:** first test run gave `1 failed, 17 passed`. The failure was a real bug, not a bad
test. When the post-change phase records zero events for every key, `chi2_contingency` raises:

```
ValueError: The internally computed table of expected frequencies
has a zero element at (np.int64(1), np.int64(0)).
```

Cause: an all-zero row makes every expected frequency in that row zero, and the calculation
divides by it. This is not an artificial case. It is what a dead agent, a dropped network, or
logging stopped entirely would produce during a real run. The old code would have crashed
mid-batch instead of reporting the condition.

Fixed in `global_gate()` by checking for degenerate tables before calling chi-square: both
phases empty means no detectable change, one phase empty means the profile certainly changed,
otherwise run the test. Added `test_phase_that_emitted_nothing_does_not_crash` and
`test_two_empty_phases_do_not_crash` so it cannot return.

**Design positions implemented** (all three were argued in the proposal revision and are now
real code): chi-square applied once globally as a gate rather than per event type; a
dispersion-aware rate ratio instead of Poisson; and REDUCED requiring the corrected q value,
the effect size, and the measured noise floor together.

**Versions pinned** in DECISIONS.md and `requirements.txt`. `statsmodels` turned out not to be
needed, because `scipy.stats.false_discovery_control` provides Benjamini-Hochberg.

**Still missing:** stage 1 acquisition (needs the lab), stage 4 impact scoring (needs the
dependency index, buildable offline), persistence to disk, run manifest hashing, and the web
interface.

**Honest limit:** the synthetic generator draws from a rounded normal. Real event counts are
not normal. The demo proves the code is correct, not that the telemetry behaves this way. No
demo number may be presented as a finding.

**Next:** OPEN-QUESTIONS item 1b must be settled before stage 1 is written, because it changes
the profile schema and therefore every stored run.

---

## 2026-08-31 - T1 approved with revisions. Proposal revision drafted. Walkthrough written and then flagged as wrong.

**Did:** Recorded the outcome of the title proposal defense, drafted answers to the panel's
11 revision items, extracted the submitted .docx into markdown, and wrote a system walkthrough.

**T1 is approved.** The panel proposed a new title:
> Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential
> Analysis Algorithm

That wording is missing an article. Recommended correction, which keeps the panel's words and
only reorders them: *Detecting Security Blind Spots Through Differential Analysis of Pre- and
Post-Hardening Events*. Raise with the adviser as a wording question, not a correction.

**Panel's 11 revision items,** all answered in [T1-PROPOSAL-REVISION.md](T1-PROPOSAL-REVISION.md),
mapped to the exact form section each belongs to: system type, report output, input and
prerequisites, compute process, remediation ability, repeatability guarantees, activity diagram
in plain terms, web versus script, algorithm in plain terms, before-and-after comparison, and
the source of the adversary tests. The panel asked no research-validity questions. Every item
was a product question.

**Two decisions taken as assumptions, still unconfirmed by the student:**
1. Web application using the existing Wazuh agent. No new endpoint agent is written.
2. Limited remediation suggestion: report a surviving telemetry source, do not rewrite rules,
   never recommend reversing the hardening.

**Also did:** extracted the submitted proposal form to `thesis/T1/proposal-form.md`. The Gantt
schedule is drawn as cell shading in the .docx, so a plain text conversion loses it entirely.
Recovered it by reading the shading directly.

**BROKE / GOT WRONG:** Wrote `T1-WALKTHROUGH.md` using "disable Audit Process Creation, CIS
17.6.2" as the demo scenario, without reading OPEN-QUESTIONS item 1 first. That item, recorded
2026-08-20, already establishes that CIS **requires** this setting enabled (17.3.1 or 17.3.2),
so disabling it is de-hardening, and it is a class A catalogue item. The control ID 17.6.2 was
also invented. The walkthrough additionally omits condition (d) of the corrected blind-spot
definition and has inconsistent surviving-coverage numbers, contradicting item 1c.

The file is kept but carries a warning banner at the top. Its structure and the naive-versus-
proposed comparison are still usable. The example must be rebuilt around a class C change.

**Lesson recorded:** read OPEN-QUESTIONS before writing anything that uses a specific control,
event ID, or setting. The answer was already in the repo.

**Also corrected:** two earlier WORKLOG entries were dated 2026-08-19 but the commits show the
work happened 2026-08-20 (repo published, Phase 0 checks). Dates fixed. A broken cross-reference
to a non-existent entry titled "Runbook Phase 0 cont." was repointed to DECISIONS.md.

**Next:** rebuild the 16-change catalogue with pinned control IDs and class labels
(OPEN-QUESTIONS item 1). That is still the top task, ahead of Runbook Phase 1, and the
walkthrough cannot be fixed until it is done.

---

## 2026-08-20 - Built the one-slide title deck for the topic proposal defense

**Did:** Made a single slide listing the three candidate titles, in rank order (T1, then T3,
then T2). No full presentation. The Topic Proposal Document is what gets presented; the slide
only exists so the panel can pick a title at the start.

**Result:** `thesis/topic-proposal-titles.pptx`. One slide, 13.333 x 7.5 in. Speaker notes hold
the 30-second spoken description of each title plus the closing question to the panel.

**Built with:** python-pptx 1.0.2 (installed this session, node is not on this host, so
pptxgenjs was not usable). Rendered to PNG through the installed PowerPoint COM object for
visual check, because LibreOffice is not installed either.

**Broke / stuck on:** Nothing. First render had cards 1.55 in tall with dead space at the
bottom and only 0.14 in clearance from the slide edge; reduced to 1.25 in and re-rendered.

**Also did:** Wrote [DEFENSE-PREP.md](DEFENSE-PREP.md), a full preparation guide for the pre-oral
topic proposal defense. Covers all three topics end to end: threat model, the 5-problem to
5-objective pairing, the five modules, algorithms, evaluation and baseline, prior work with the
concrete figures, and the weakest point of each with an honest answer. Includes a glossary, a
numbers-to-memorize table, a question bank, and a list of the known holes in the proposals.

**Holes found while writing it (all listed in DEFENSE-PREP.md section 8):**
- The Tyagi sigmalint citation is dated 2026 in T2 and 2026 with different dates in T3, and T2
  also calls it a 2025 SSRN working paper. The two entries must agree.
- Author names carry mojibake in the proposal text files: "Hackl?nder", "Jo?o", "Map?a".
- The 16 hardening changes are still not pinned to CIS or DISA control IDs (OPEN-QUESTIONS item 4).
  This is the highest-value offline fix before the defense.

**Broke / stuck on:** Could not rebuild the pptx to correct the T3 speaker note, which still
describes validating against the SigmaHQ STP annotations without saying that only 6 of 3,783
rules carry one. `PermissionError: [Errno 13] Permission denied` because the file was open in
PowerPoint. Rebuild after closing it.

**Then stress-tested T1** against a formal definition of security hardening. Found nine problems.
The two that matter:

1. **Four of the 16 catalogue items are anti-hardening.** Verified against the benchmarks on
   2026-08-20. CIS requires Audit Process Creation set to Success (17.3.1 or 17.3.2 by version)
   and requires 'Include command line in process creation events' Enabled (18.9.3.1, or 18.8.3.1
   in some versions). DISA STIG WN10-CC-000326 / V-220860 requires PowerShell script block
   logging Enabled. Catalogue items 1 to 4 turn all of these off, which is de-hardening.
2. **Telemetry loss is not a blind spot.** Disabling SMBv1 removes SMB1 events and SMB1 attacks
   together, so the rule should be retired, not flagged. The blind-spot definition needs a fourth
   condition: the technique must still be executable after the change.

Classification of the catalogue: 4 anti-hardening, 1 with no benchmark control (Sysmon config),
6 where the attack is removed with the telemetry, 5 true blind-spot candidates. Of those 5, one
is content-level and invisible to the current profile design and one is blocked on nested
virtualization, leaving 3 solid positive cases.

**Checked what this does to the submitted proposal.** Nothing in the submitted T1 document names
a specific control, event ID, or setting. The only sentences at risk are the two that say the
16 changes are "drawn from" CIS Benchmarks and DISA STIGs (Objective 4 and Scale of the
Experiment). Those stay true once the catalogue is corrected, and the count of 16 can stay at 16.
The defect is entirely in `lab/blueprint.md` section 8, which was never submitted.

Full detail in [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) items 1, 1b, and 1c.

**Next:** Rebuild the 16-change catalogue with pinned control IDs and a class label per change.
That is now the top task, ahead of Runbook Phase 1.

---

## 2026-08-20 - Runbook Phase 0 checks. Mostly pass, one flag.

**Did:** Ran the Phase 0 readiness checks on the host.

**Results:**
| Check | Result |
|---|---|
| F: free space (need 350 GB) | PASS. 732 GB free. |
| C: free space | 315 GB free. |
| AMD SVM virtualization in firmware | PASS. VirtualizationFirmwareEnabled = True. |
| Python 3.11+ on C: | PASS. Python 3.13.14 at C:\Program Files\Python313. |
| VMware Workstation | PASS. 17.5.1 build-23298084 (matches blueprint pin). |
| vmrun works | PASS. `vmrun -T ws list` returned "Total running VMs: 0". |
| ISOs present | PASS. In E:\Homelab files (see paths below). |
| Python venv created | NOT DONE YET. |

**vmrun path:** `C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe`

**ISO choices (in E:\Homelab files):**
- SIEM-01 (Ubuntu LTS): `ubuntu-24.04.4-live-server-amd64.iso`. 24.04 LTS, which Wazuh supports.
- WIN-EP-01 (Windows): `Windows 11 Enterprise Eval 26200.6584...25h2...CLIENTENTERPRISEEVAL`. The
  evaluation edition the runbook asks for.

**FLAG worth a decision before the spike:** `HypervisorPresent = True`. RESOLVED same day, see
DECISIONS.md entry "Windows hypervisor turned off". Cause was the Hyper-V
feature (not a security feature). Turned it off with `bcdedit /set hypervisorlaunchtype off` and
rebooted. Verified HypervisorPresent = False, VBS = 0, vmrun still works. Host now runs VMware
natively, before any VM was built, which is the correct time to make this change.

**Also noted:** the host has other virtualization tools present (Proxmox, TrueNAS, OPNsense ISOs;
other homelab folders). Our whole plan assumes VMware Workstation + vmrun. If the plan ever moves
to Proxmox, the harness (which calls vmrun) has to be rewritten. Sticking with VMware.

**Next:** decide on the Python venv location, then Phase 1 (virtual networks).

---

## 2026-08-20 - Repo published to GitHub, public

**Did:** Professor cleared publishing (no IP rule, no similarity-check problem). Installed
GitHub CLI (`gh` 2.97.0) via winget. User logged in as EASolutions00. Created the public repo
and pushed all commits.

**Result:** Live at https://github.com/EASolutions00/detection-hardening-lab (public, 6 commits).
`gh` is now installed and authenticated, so future pushes work directly from the Bash tool.

**Note:** `gh` lives at `C:\Program Files\GitHub CLI`. If a shell cannot find it, add that to
PATH for the session: `export PATH="$PATH:/c/Program Files/GitHub CLI"`.

**Still open:** no LICENSE file yet. Add one (MIT or Apache 2.0) before pointing anyone at the
repo, so the "usable by small companies" claim in the proposals is legally true.

**Next:** start the lab. Runbook Phase 0.

---

## 2026-08-19 - Counted SigmaHQ STP annotations. Result is bad for T3.

**Did:** Cloned `SigmaHQ/sigma` at commit `da9bb07`, counted rules carrying a Summiting the
Pyramid robustness tag (`stp.<level>` in the `tags:` list).

**Result:** 6 rules out of 3,783. 0.16%. Levels: stp.1u x3, stp.1k x1, stp.2a x1, stp.4u x1.

**Gotcha worth remembering:** a plain `grep stp.` gave 19 files and looked survivable. 13 were
false hits on `cmstp.exe` / `chrmstp.exe`. Always match the tag line `- stp.<digit>`, not the
substring. If I had trusted the first number I would have called T3 safe when it is not.

**Consequence:** T3's Objective 5 is not executable as written. T3 is no longer a safe fallback.
Recorded in DECISIONS.md and moved the open question to Answered. No decision made yet on whether
the fallback becomes "T3 with self-annotation" or "T2 instead". That waits for the T1 spike.

**Next:** unchanged. T1 is still primary. But the safety net changed, so the T1 spike matters
more than before, because a failed spike no longer has a clean landing.

---

## 2026-08-19 - Reply rules made global

**Did:** Created `C:\Users\Elijah\.claude\CLAUDE.md` holding the full AI rules.

**Why:** The rules were only applying because they were pasted at the start of each chat.
Nothing loaded them automatically. `~/.claude/CLAUDE.md` did not exist, there was no
`settings.json`, no output style, and the memory directory was empty. The project CLAUDE.md
only *linked* to `docs/AI-RULES.txt`, and a link is not a load.

**Result:** Rules now load automatically in every project and every session on this machine.
No more pasting.

**Note for later:** that file is **outside this repo**, so git does not back it up and it will
not follow you to another machine. `docs/AI-RULES.txt` is the versioned copy. Verified the two
are identical apart from a trailing newline. If you edit one, edit both.

---

## 2026-08-19 - CLAUDE.md reviewed and trimmed

**Did:** Reviewed `CLAUDE.md` as an index rather than a document. Cut it from 140 lines to
104. Removed detail that duplicated the runbook (the reasoning behind the silent-failure
rules, the spike Q1/Q2 breakdown), the restated voice rules, and a filler `git status` block.
Created `thesis/README.md` to hold the institutional template and the problem-to-objective
numbering rule, which previously had no home outside `CLAUDE.md`.

**Result:** All 12 internal links verified as resolving. Nothing was lost, only relocated.

**Fixed while reviewing:**
- `CLAUDE.md` said the repo is private on GitHub. It is not. `git remote -v` is empty, no
  GitHub repo exists yet. Now reads "will be created private".
- "end of September" had no year. Now says September 2026.
- "gh is not installed" removed from `CLAUDE.md`. That is machine state, not project state,
  and it is already recorded in this log below.

**Kept deliberately:** the five silent-failure rules stay in `CLAUDE.md` instead of becoming
a pointer. They have to be loaded before deciding which file to read, otherwise a VM ends up
on E: without the runbook ever being opened.

**Next:** unchanged from the entry below.

---

## 2026-08-19 - Repo structure created

**Did:** Turned the folder into an organized git repo. Created `docs/`, `thesis/`, `lab/`,
`src/`, `data/`. Moved the four original documents into place. Wrote `CLAUDE.md` as the
index, `docs/RUNBOOK-homelab.md` as the from-scratch build procedure, and this log.

**Result:** Structure is in place. Nothing about the lab or the thesis has been built yet.
The four source documents are unchanged in content, only moved.

**Broke / stuck on:** `gh` (GitHub CLI) is not installed on this machine, so the repo cannot
be created from the terminal yet. Either install it or create the repo in the browser.

**Next:**
1. Answer the T3 SigmaHQ annotation count question. See `docs/OPEN-QUESTIONS.md`.
   It is offline, takes minutes, and it gates your only fallback.
2. Start Phase 0 of the runbook.
3. Create the private GitHub repo and push.

---

## 2026-08-18 - Source documents written (before this log existed)

**Did:** Wrote the three thesis proposals (T1, T2, T3) and the homelab blueprint.

**Result:** All four are in `thesis/` and `lab/blueprint.md` now.

**Next:** Was superseded by the 2026-08-19 session above.

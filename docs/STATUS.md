# STATUS

Current blockers and dates. This file changes often. CLAUDE.md does not.
Last updated: 2026-10-16 (chat 27d2595d)

Every item here must also exist in OPEN-QUESTIONS.md or DECISIONS.md. This file only
says which ones matter right now. Where every file lives, inside and outside the repo:
[FILE-MAP.md](FILE-MAP.md).

---

## Deadline and target

- **School deadline for the final thesis: 4 June 2027** (stated by the student 2026-09-29).
- **Target: final defense by the end of January 2027** (DECISIONS.md 2026-09-29). March 2027 was
  recommended; January was chosen, with the risk stated: four months, the same length as the Gantt plan
  that slipped, with more work in it. One missed checkpoint moves the defense to February or later.
- The earlier target, a final defense in December 2026 (FINAL's Gantt), slipped at its first lab rows:
  no capture run exists.
- **The re-presentation:** the panel said it will focus on the **activity diagram** (student, 2026-09-29).
  **The panel sets a date only after the revised documentation is submitted, about 3 to 7 days later**
  (student, 2026-09-29). **Submitted 2026-10-15** by email to the panel chair (student), after three missed
  dates: 2026-10-02, 2026-10-07 and 2026-10-12 (`DECISIONS.md` 2026-10-08, overtaken). **The re-presentation
  is Thursday 2026-10-22, 3:30 to 5:00 pm** ("Title Proposal Re-presentation", calendar entry pasted by the
  student 2026-10-16), seven days after the submission.
  Recommended, not decided: run the full data collection only after the panel approves the diagram.

## Checkpoints (proposed 2026-09-29, dates are estimates)

| By | Done when |
|---|---|
| 2026-10-09, latest 2026-10-12 | Revised documentation submitted (the panel then sets the re-presentation date). **Done 2026-10-15** (student), three days after the latest date; 2026-10-02, 2026-10-07 and 2026-10-12 were missed |
| 2026-10-09 | Adviser told of the slip and the January target. **Partly done:** the student told their professor about the delay (by 2026-10-08); the January target is not stated. WORKLOG 2026-10-07: the adviser is named only after the re-presentation |
| 2026-10-22, 3:30 to 5:00 pm | **Re-presentation** (date set by the panel; student, 2026-10-16) |
| 2026-10-30 (was 2026-10-23) | DC-01 built, WIN-EP-01 joined, Sysmon `lsass.exe` rule and audit settings in place, value keying coded and tested, network-logon test designed, golden snapshot taken |
| 2026-11-07 (was 2026-10-31) | Spike run, six answers recorded, final number of changes set. Both moves: DECISIONS 2026-10-16 |
| 2026-11-30 | Data collection done |
| 2026-12-18 | Rest of the system (impact scoring, remediation, reports) and the evaluation done |
| 2027-01-08 | Full draft to the adviser |
| 2027-01-31 | Final defense |

If a checkpoint is missed: cut in the decided order (the graphical interface first, then class B negative
controls), and record the miss in WORKLOG the same day.

## Decided 2026-09-29 (details in DECISIONS.md)

1. **Item 21:** build DC-01, with its own Wazuh agent and a test that makes network logons, before the
   golden snapshot.
2. **Item 18:** value keying for a short list of fields (final list after the C3 capture); an `lsass.exe`
   rule in the Sysmon config; C3 uses `RunAsPPL = 2`, a stated deviation from CIS 18.9.27.2.
3. **Item 20:** Process Creation auditing with command line, and Credential Validation auditing, go into
   the golden snapshot.
4. **Item 25:** target January 2027; keep every measurable class C change; cut the graphical interface,
   then class B, first; the spike sets the final number.

**None of it is built.** Each is work for checkpoint 2.

## Next, in order

1. **Submitted 2026-10-15.** Sent by the student, by email to the panel chair, with three attachments:
   `Detecting … Algorithm.pdf` (30 pages, made from `Detecting … Algorithm.docx`, both in the thesis folder)
   and the two diagram sheets as full-size PDFs. Not sent: the revisions list (not required), the panel
   response and the explainer. The email says the student raised the web-based idea at the title defense
   and the panel asked that it be declared; the system stays a desktop application; and asks whether the
   panel accepts this or the system must still be web-based (DECISIONS 2026-10-07, corrected note). Checks
   before sending: WORKLOG 2026-10-15.
   **Now: the re-presentation, Thursday 2026-10-22, 3:30 to 5:00 pm. Practice.** The scripts are in `prep-local`:
   `RE-PRESENTATION-SCRIPT 22-MIN.txt` (about 3,100 words) and the full script with 31 answer cards
   (WORKLOG 2026-10-14). The study plan is `prep-local\STUDY-GUIDE.md`. **When the panel answers the
   web-based question, record the answer in DECISIONS.** A refusal means a web front end on the same core
   (DECISIONS 2026-10-07, cost if wrong).
2. **Tell the adviser** (checkpoint 2026-10-09). Partly done: the student told their professor about the
   delay. The adviser is named only after the re-presentation (WORKLOG 2026-10-07).
3. From Friday 2026-10-23, the day after the re-presentation (DECISIONS 2026-10-16): **build DC-01 and join
   WIN-EP-01**; apply the Sysmon rule and the audit settings; code value keying, the control-run check
   (item 24) and pairing (item 30). Checkpoint: 2026-10-30, six working days. Until 2026-10-22, no lab
   work: practice only.
   Open question first: does DC-01 still earn its days, now that no positive case needs it (WORKLOG
   2026-10-06)?
4. Golden snapshot, a minimal harness, one capture window by hand as a trial, then the spike.

## Still waiting on the student

- **Item 15 answered 2026-10-15:** the submitted Word file and PDF carry all of FINAL's text and the four
  current figures (OPEN-QUESTIONS, Answered section).
- **Item 33, new 2026-10-12:** from the professor's guidelines, four points to ask or decide. Point 1 first:
  is the January 2027 defense the pre-oral (50% working system) or the final?
- **Item 32, new 2026-10-08:** four points with no record (window length, whether DC-01 is restored each run,
  the Wazuh field-name mapping, whether DC-01 still earns its days). Point 4 should be decided before the lab
  work starts.
- Items 24 and 30 were decided 2026-09-29: both stay in the design and are built before data collection.

## The spike

T1 is approved and final. There is **no fallback** (DECISIONS.md 2026-09-26). The spike has not run. It
answers six questions (runbook Phase 7): run-to-run variance, wall clock, zero findings on
control-versus-control pairs, how many keys reach 30 events, the stimulus fingerprint's spread, and the
extra reboot's effect. Its result sets the number of changes (DECISIONS.md 2026-09-29).

## Why nothing was measurable (items 21 and 18, now decided)

On 2026-09-26: 4768, 4769 and 4776 were zero on every archive date, and the lab never made a network
logon (0 of 2,892). The pinned Sysmon config records no Event 10 (0 of 14,102 Sysmon events). So, as
configured then, **no class C change was measurable.** The 2026-09-29 decisions fix this on paper; about 7
class C changes become measurable once they are built. **2026-10-01:** the study uses Wazuh's shipped rules,
and with them only C1, C3 and C5 can blind a detection (`DECISIONS.md` 2026-10-01, choice 1; OPEN-QUESTIONS 1).

## Also open

- Item 1, the catalogue. 14 changes; several control IDs still `(unverified)`. It still blocks data
  collection. The count no longer has to reach 16.
- Item 26. The harness's own `vmrun` guest calls most likely write a batch logon each, inside every capture
  window: 1,641 on 2026-09-02. With Credential Validation on, probably a 4776 each too.
- Item 27. The host's VMware network adapters broke twice with no known cause. The harness must check the
  path to SIEM-01 before each run.
- Item 28. Events written before the Wazuh agent starts never reach the archive, so boot-time checks such
  as Wininit event 12 must be made inside the guest.
- Item 23. The spike must run `analyse()` on control-versus-control pairs and find none.
- Item 22. The stimulus is asserted identical across runs and never verified.
- Item 31. The event key has no host part; with DC-01, two hosts' events of one key are counted together.

## Lab state

- No lab VM was running on 2026-09-28 (`vmrun -T ws list`: `Total running VMs: 0`). Check with `vmrun`
  rather than trusting this line.
- Host VMnet2 is at `10.20.10.1` again after a hand repair (item 27). Pre-flight now checks it.
- DC-01 does not exist yet.
- Both VM folders on F: have a `.vmx.lck` lock folder dated 2026-10-08 13:10, with no record. The VMware logs
  did not change, so probably opened but not powered on (unverified). Check with `vmrun` first
  (FILE-MAP section 6).

## Recently settled (details in DECISIONS.md)

- 2026-10-07: the system stays a desktop application. Revision 8 answers the panel's instruction to declare
  it web-based (found in the title-defense transcript) and asks the panel to confirm. The interface toolkit
  must run on Windows, Linux and macOS.

- 2026-09-29: four decisions: January 2027 target and the scope rule; build DC-01; value keying, the Sysmon
  `lsass.exe` rule and `RunAsPPL = 2`; process creation and credential validation auditing.
- 2026-09-28: four decisions closing item 29. The whole-profile chi-square is reported, not a filter, and
  every key is tested. One attack-test list is pinned in Phase 0. Remediation is two levels. Fixes are
  applied by script. Code: 58 tests passing.
- 2026-09-26: T1 is the final thesis. There is no fallback topic.
- 2026-09-14: the title is the panel's wording verbatim (item 0).
- 2026-09-14: the system is a Python application with a graphical interface beside the SIEM, not a web
  application (item 17).

# STATUS

Current blockers and dates. This file changes often. CLAUDE.md does not.
Last updated: 2026-09-29 (from git log)

Every item here must also exist in OPEN-QUESTIONS.md or DECISIONS.md. This file only
says which ones matter right now.

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
  (student, 2026-09-29). **Target: submit by Friday 2026-10-02.** Recommended, not decided: run the full
  data collection only after the panel approves the diagram.

## Checkpoints (proposed 2026-09-29, dates are estimates)

| By | Done when |
|---|---|
| 2026-10-02 | Revised documentation submitted (the panel then sets the re-presentation date) |
| 2026-10-09 | Adviser told of the slip and the January target |
| 2026-10-23 | DC-01 built, WIN-EP-01 joined, Sysmon `lsass.exe` rule and audit settings in place, value keying coded and tested, network-logon test designed, golden snapshot taken |
| 2026-10-31 | Spike run, six answers recorded, final number of changes set |
| panel's date | Re-presentation |
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

1. **Submit the revised documentation by Friday 2026-10-02**, one step a day:
   - Tuesday 09-29, **done:** FINAL updated with the four decisions and a new Gantt chart; the key wording
     fixed in Sheet 1 and the pipeline figure; the revisions list made ready to submit; the diagram
     explainer updated for study (WORKLOG 2026-09-29, second). **Submitted: FINAL and the revisions
     list.** Not submitted: the panel response (still stale in places) and the explainer.
   - Wednesday: study the activity diagram box by box and explain each box back.
   - Thursday: the Word copy. The student formats it from copy-friendly text of FINAL.
   - Friday: one consistency check of the submitted files, then submit.
2. **Tell the adviser** (checkpoint 2026-10-09). The student sends it.
3. From Monday 2026-10-05: **build DC-01 and join WIN-EP-01**; apply the Sysmon rule and the audit
   settings; code value keying, the control-run check (item 24) and pairing (item 30).
4. Golden snapshot, a minimal harness, one capture window by hand as a trial, then the spike.

## Still waiting on the student

- **Item 15, the Word file.** The student formats it from copy-friendly text of FINAL (Thursday).
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
class C changes become measurable once they are built.

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

## Lab state

- No lab VM was running on 2026-09-28 (`vmrun -T ws list`: `Total running VMs: 0`). Check with `vmrun`
  rather than trusting this line.
- Host VMnet2 is at `10.20.10.1` again after a hand repair (item 27). Pre-flight now checks it.
- DC-01 does not exist yet.

## Recently settled (details in DECISIONS.md)

- 2026-09-29: four decisions: January 2027 target and the scope rule; build DC-01; value keying, the Sysmon
  `lsass.exe` rule and `RunAsPPL = 2`; process creation and credential validation auditing.
- 2026-09-28: four decisions closing item 29. The whole-profile chi-square is reported, not a filter, and
  every key is tested. One attack-test list is pinned in Phase 0. Remediation is two levels. Fixes are
  applied by script. Code: 58 tests passing.
- 2026-09-26: T1 is the final thesis. There is no fallback topic.
- 2026-09-14: the title is the panel's wording verbatim (item 0).
- 2026-09-14: the system is a Python application with a graphical interface beside the SIEM, not a web
  application (item 17).

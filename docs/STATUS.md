# STATUS

Current blockers and dates. This file changes often. CLAUDE.md does not.
Last updated: 2026-11-13 (chat ee84ae3f, end-of-day check): DC-01 dropped, the C5 tests and decisions, "Next, in
order", "Also open" and "Lab state". The deadline, checkpoint and adviser sections date from 2026-11-02 to 2026-11-03
(chat 27d2595d).

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
  **Held 2026-10-22: accepted on condition** that the document is revised and simplified, then shown to the
  panel again for full approval. Adviser: Prof. Ervin Moran. Pre-oral panel: Prof. Dan Mercolita (chair), Prof.
  Joanna Lynn Mabula, Prof. Josephine Casin (guest). DECISIONS 2026-10-22.
  Recommended, not decided: run the full data collection only after the panel approves the diagram.

## Checkpoints (proposed 2026-09-29, dates are estimates)

| By | Done when |
|---|---|
| 2026-10-09, latest 2026-10-12 | Revised documentation submitted (the panel then sets the re-presentation date). **Done 2026-10-15** (student), three days after the latest date; 2026-10-02, 2026-10-07 and 2026-10-12 were missed |
| 2026-10-09 | Adviser told of the slip and the January target. **Partly done:** the student told their professor about the delay (by 2026-10-08); the January target is not stated. WORKLOG 2026-10-07: the adviser is named only after the re-presentation |
| 2026-10-22, 3:30 to 5:00 pm | **Re-presentation** (date set by the panel; student, 2026-10-16). **Done: accepted on condition of a simplified revision** (DECISIONS 2026-10-22) |
| 2026-10-30 (was 2026-10-23), **missed: no lab work recorded as of 2026-11-02; new date after the adviser answers OPEN-QUESTIONS 33** | Sysmon `lsass.exe` rule and audit settings in place, value keying coded and tested (all three done 2026-11-03), golden snapshot taken. DC-01, the domain join and the network-logon test were dropped 2026-11-11 (DECISIONS) |
| 2026-11-07 (was 2026-10-31) | Spike run, six answers recorded, final number of changes set. Both moves: DECISIONS 2026-10-16 |
| 2026-11-30 | Data collection done |
| 2026-12-18 | Rest of the system (impact scoring, remediation, reports) and the evaluation done |
| 2027-01-08 | Full draft to the adviser |
| 2027-01-31 | Final defense |

If a checkpoint is missed: cut in the decided order (the graphical interface first, then class B negative
controls), and record the miss in WORKLOG the same day.

## Decided 2026-09-29 (details in DECISIONS.md)

1. **Item 21:** build DC-01, with its own Wazuh agent and a test that makes network logons, before the
   golden snapshot. **Superseded 2026-11-11: DC-01 is dropped** (DECISIONS 2026-11-11).
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
   **Re-presentation held 2026-10-22: accepted on condition of a simplified revision** (DECISIONS 2026-10-22).
   **Now: the first online consultation with the adviser, Prof. Ervin Moran.** No word from him as of
   2026-11-02 (student). **Follow-up message sent 2026-11-02** (student), asking for the consultation and the
   three questions below; no reply yet. Ask: what "simplify" means and
   the deadline for the revised document; whether the desktop application is accepted (not asked at the
   re-presentation); which defense January is (OPEN-QUESTIONS 33). Bring the corrections of the answers given on
   2026-10-22, listed in WORKLOG 2026-10-22, first the "zero blind spots" one.
2. **Tell the adviser** (checkpoint 2026-10-09). The adviser is now named: Prof. Ervin Moran. Tell him the
   January 2027 target at the first consultation.
3. From Friday 2026-10-23, the day after the re-presentation (DECISIONS 2026-10-16): **build DC-01 and join
   WIN-EP-01**; apply the Sysmon rule and the audit settings; code value keying, the control-run check
   (item 24) and pairing (item 30). **Done 2026-11-03:** items 24 and 30 built; the Sysmon `lsass.exe` rule and
   both audit settings applied and proven in the guest (COMMANDS 2.11); in the archive the same day: 4688 = 117,
   Sysmon 10 = 121, 4776 = 2 (WORKLOG 2026-11-03). Value keying coded the same day, then corrected to use each rule's own
   pattern (65 tests, OPEN-QUESTIONS 35). DC-01 was waiting for Sir Ervin (student, 2026-11-03); **dropped
   2026-11-11** (DECISIONS 2026-11-11). LSASS trial part 1 run
   the same day: LSA Protection was already on (OPEN-QUESTIONS 36; baseline turns it off, DECISIONS 2026-11-03), and
   Defender stopped all three tests, 0 lsass events (OPEN-QUESTIONS 35). C3 is measured in Config S (DECISIONS
   2026-11-03). WIN-EP-01 must go back to `pre-lsass-trial-2026-11-03` first. Checkpoint: 2026-10-30, six working days. Until 2026-10-22, no lab
   work: practice only.
   Open question first: does DC-01 still earn its days, now that no positive case needs it (WORKLOG
   2026-10-06)? **Answered 2026-11-11: no, dropped.** New open points from that decision: how the C5 RDP sign-in
   is driven from the host with no person at the keyboard, and whether Remote Desktop is on in WIN-EP-01.
4. Golden snapshot, a minimal harness, one capture window by hand as a trial, then the spike.

**Now, as of 2026-11-13: the lab steps before the golden snapshot, in order.**
- **Done:** C5 is designed and tested end to end (DECISIONS 2026-11-12, 2026-11-13 twice; OPEN-QUESTIONS 37): baseline
  Remote Desktop on with NLA off; the default client; the sign-in from the host with the stored password; no
  sign-out step, the revert ends the session.
- **a. LSASS trial part 2** (C3 in Config S, Defender off). **Done 2026-11-13** (COMMANDS 2.13): tests 1, 2 and 13
  never fire rule 92900 (it fired only on Defender's and `svchost.exe`'s own access), **but test 13 fires 92403 (×2)
  and 61625 (×1), both level 12, with LSA Protection off and neither with it on.** **Decided 2026-11-13: prevention**, as for
  C5 (DECISIONS 2026-11-13). **C1 is now the only candidate positive case**, untested: the C1 test moves up. Still
  optional: rerun test 9 on a fresh boot; try tests 3, 4, 12, 14 (OPEN-QUESTIONS 35).
- **Tell the adviser:** with C5 and C3 read as prevention and C1 showing no change, the study has no candidate
  positive case under the shipped rules (OPEN-QUESTIONS 38).
- **b. The C1 test** (WDigest, rule 60118). **Trial done 2026-11-13** (COMMANDS 2.14): a console sign-in wrote the
  same events with WDigest caching on and off; 60118 fired twice both times. **So no candidate change shows a blind
  spot** (OPEN-QUESTIONS 38). **Next, before more lab work: the student and the adviser decide the way forward
  (item 38).**
- **System work that does not wait for item 38** (student, 2026-11-13: build the system now). **Done 2026-11-13:
  the archive reader** (`src/telos/archive.py`, 10 tests), checked on three real windows of today's export. **Done
  2026-11-13: the rule-to-key index** (`src/telos/index.py`, 10 tests, 85 passed), read on the rule export from
  SIEM-01 (COMMANDS 2.15). **For the student:** the index shows the key map misses fields rules read (4624:
  `IpAddress`, `TargetUserSid`, `WorkstationName`); adding them changes the keys (OPEN-QUESTIONS 32). **Done
  2026-11-13: impact ranking** (`src/telos/impact.py`; DECISIONS 2026-11-13: a ranking, no weights; surviving
  coverage counts rules that **did fire** after the change). 94 passed. On the C3 trial it marks T1055 blind (92403
  fired before, not after), as seen in the lab. **Done 2026-11-13: report sections** (`report.py`): verdict, ranked
  blind spots with remediation level 1, coverage change; JSON and CSV exports; 101 passed. Not yet: reproducibility
  record, remediation level 2, Navigator layer. **Done 2026-11-13: the harness code** (`src/telos/harness.py`,
  12 tests with a fake `vmrun`, 113 passed; fixed-length windows, DECISIONS 2026-11-13). **Not yet run on the lab.**
  Before its first real run: the `cfg-suppressed` snapshot, the attack list and change scripts, C1's unattended
  sign-in, a time limit for the C5 `mstsc` host step, how `runProgramInGuest` starts Atomic Red Team, the password
  file's encoding. **Done 2026-11-13: the pipeline** (`src/telos/pipeline.py`, command `src/run.py`, 5 tests,
  118 passed): run folders to report, JSON and CSV. **Student's plan (2026-11-13): reach 100% of the system, then
  the GUI; commit and push every big change.** **Done 2026-11-13:** reproducibility record, Navigator layer
  (format 4.5, checked against MITRE's specification), remediation level 2 (curated list, two entries from lab
  measurements, not tested); 123 passed. **All of FINAL's report sections and exports now exist in code.**
  **Done 2026-11-13:** change scripts C1, C3, C5 with `-Verify`, the Config S script, and the harness's after-boot
  steps (125 passed). Left before the GUI, **all needing the student:** the decisions (C1 baseline, the pinned attack
  list, C1's unattended sign-in, item 38), copying the scripts into the guest, the golden snapshot, and the first
  real harness run.
- **c. The golden snapshot** (runbook Phase 5, taken cold): the baseline now also needs LSA Protection off, Remote
  Desktop on with NLA off and the firewall rule for `10.20.10.1`, and no `eli` session at shutdown.
- **d.** Then the minimal harness, one capture window by hand, and the spike. **Checkpoint 2026-11-07 (spike) was
  missed** (no spike run; first recorded 2026-11-13), and 2026-11-30 (data collection) cannot be met. New dates are
  not set; the student decides them.

## Still waiting on the student

- **Item 15 answered 2026-10-15:** the submitted Word file and PDF carry all of FINAL's text and the four
  current figures (OPEN-QUESTIONS, Answered section).
- **Item 33, new 2026-10-12:** from the professor's guidelines, four points to ask or decide. Point 1 first:
  is the January 2027 defense the pre-oral (50% working system) or the final?
- **Item 32, new 2026-10-08:** four points with no record (window length, whether DC-01 is restored each run,
  the Wazuh field-name mapping, whether DC-01 still earns its days). **Point 4 decided 2026-11-11: DC-01 is
  dropped; point 2 no longer arises.** Points 1 and 3 remain.
- Items 24 and 30 were decided 2026-09-29: both stay in the design and are built before data collection.
  **Both built 2026-11-03** (60 tests pass).

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
- Item 26. **Cause confirmed 2026-11-12:** each `vmrun` guest call writes two 4624 type 4 logons by `vmtoolsd.exe`,
  and rule 67022 (level 3) fires on each; with Credential Validation on, also two 4776 (2026-11-03). The harness must
  count its calls per run.
- Item 27. The host's VMware network adapters broke twice with no known cause. The harness must check the
  path to SIEM-01 before each run.
- Item 28. Events written before the Wazuh agent starts never reach the archive, so boot-time checks such
  as Wininit event 12 must be made inside the guest. Seen again after the 2026-11-12 restart: 0 event 6005, 0
  Wininit.
- Item 23. The spike must run `analyse()` on control-versus-control pairs and find none.
- Item 22. The stimulus is asserted identical across runs and never verified.
- Item 31. The event key has no host part. No longer arises with one Windows host (DC-01 dropped 2026-11-11).

## Lab state

- **End of 2026-11-13 (chat ee84ae3f):** WIN-EP-01 was reverted to `pre-lsass-trial-2026-11-03` at 13:01 UTC for the
  golden snapshot; **no baseline step was done** (the student stopped there). The student shuts both VMs down.
  **Next session starts with the golden snapshot:** the student chooses C1's baseline (`-WDigest On`, recommended, or
  `Default`), copies the 5 scripts into `C:\telos\`, runs `baseline-golden.ps1`, restarts, verifies 20 of 20, signs
  out, shuts down, disconnects NAT in the VM settings; then Claude takes `golden-base` cold. Check with `vmrun`
  rather than trusting this line.
- **Host state:** `eli`'s guest password is stored in the host's Credential Manager as `TERMSRV/10.20.10.20`
  (`cmdkey`, 2026-11-12); the C5 harness needs it. `cmdkey /delete:TERMSRV/10.20.10.20` removes it. On SIEM-01:
  `/home/eli/c5/p-hostip.txt`, the pattern file `"ipAddress":"10.20.10.1"`.
- **Time sync is off on both VMs.** Suspend a VM and its clock goes stale; shut it down or power-cycle instead
  (WORKLOG 2026-11-11 to 2026-11-12).
- Host VMnet2 is at `10.20.10.1` again after a hand repair (item 27). Pre-flight now checks it.
- DC-01 does not exist and will not be built (DECISIONS 2026-11-11).
- Both VM folders on F: have a `.vmx.lck` lock folder dated 2026-10-08 13:10, with no record. The VMware logs
  did not change, so probably opened but not powered on (unverified). Check with `vmrun` first
  (FILE-MAP section 6).

## Recently settled (details in DECISIONS.md)

- 2026-11-13: **tested.** C1 trial: WDigest caching on or off, a console sign-in wrote identical 4624 type 2 events
  and fired 60118 twice. The stated effect was not seen. With C3 and C5, no candidate change shows a blind spot under
  the shipped rules: **new item 38, for the student and the adviser.**

- 2026-11-13: **decided.** C3's lost level-12 alerts (92403, 61625 on test 13) are prevention, not a blind spot:
  with LSA Protection on the dump never reached `lsass.exe`, and the attempt still raised level-3 and level-4
  alerts. Same rule as C5. C1 is the only candidate positive case left. Exit codes cannot show the blocked attack
  (item 22).

- 2026-11-13: **tested.** LSASS trial part 2, Defender off: with LSA Protection on, the tools could not open
  `lsass.exe` (0 Sysmon 10); with it off, they could (`0x1fffff`, `0x1410`, `0x10147a`), but **rule 92900 fired on
  none of them**. All 14 hits of 92900 were Defender's and `svchost.exe`'s own access (`0x101000`, `0x1010`).
  **Corrected the same day:** test 13 (rdrleakdiag) fired 92403 twice and 61625 once (level 12) with LSA Protection
  off, and none with it on. So C3 does remove three alerts; blind spot or prevention is not decided (item 35).
  Test 9 failed: test 13 leaves a second `lsass.exe` running, so test order matters.

- 2026-11-13: **decided.** No sign-out step for C5; the revert before each run ends the session; the golden snapshot
  is taken cold with no `eli` session. Tested 2026-11-12: a fresh boot leaves no `eli` session, and a `vmrun` guest
  call does not create one (type 10 with 92653 both times). Also confirmed: each `vmrun` guest call writes two type 4
  logons that fire rule 67022 (item 26).
- 2026-11-13: **decided.** C5 uses the default RDP client and is reported as "the predicted effect was not seen".
  The refused no-check sign-in is prevention, not a blind spot (blueprint condition (d)). Positive cases stay C1 and
  C3 (item 37, point 5).
- 2026-11-12: **tested.** The C5 sign-in needs no person at the keyboard: with `eli`'s password stored once on the
  host (`cmdkey`), `mstsc /v:10.20.10.20` signed in twice with no box and fired 92653.

- 2026-11-12: **tested.** NLA on and off give the same events with the default client (two type 3 NTLM with 92657,
  then two type 10 with 92653). With a client that skips the password check, NLA off gives type 10 and 92653 only,
  and NLA on refuses the connection with no logon event and no alert. New open point: which client the C5 test uses,
  and whether the refused attempt is prevention or a blind spot (item 37, point 5).

- 2026-11-12: **tested.** A local-account RDP sign-in from the host fired rule 92653 (two type 10 logons). WIN-EP-01 was
  reverted to `pre-lsass-trial-2026-11-03` first. New open item 37: NLA is already on in the baseline (the C3
  problem again), the sign-in writes type 7 if the account already has a session, and every sign-in also fires 92657.
- 2026-11-12: **decided.** The baseline turns Remote Desktop on with NLA off (firewall open to `10.20.10.1` only); C5
  turns NLA on. Same pattern as C3. Whether NLA on and off give different events is still open (item 37, point 3).
- 2026-11-11: DC-01 is dropped. The lab is WIN-EP-01 and SIEM-01. C5 signs in over RDP with a local account from
  the host. C4, C6 and B5 leave the study. FINAL said the domain is required, so the simplified revision states
  the change.

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

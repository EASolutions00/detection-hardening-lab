# Decision Log

Every choice that would be expensive to reverse, or that you will forget the reason for.
Newest at the top. Never delete an entry. If a decision is reversed, add a new entry that
says so and link back.

Format: date, the decision, why, and what it costs if wrong.

---

## 2026-10-08 - The revised documentation is submitted Friday 2026-10-09 if the mock panel passes, and Monday 2026-10-12 at the latest. The 2026-10-07 date is missed

**Decision, by the student, chat 27d2595d:** the goal date to submit FINAL and the revisions list is Friday
2026-10-09. On Thursday 2026-10-08 the student makes the Word file from `proposal-form-FINAL-for-Word.html`.
On Friday morning the student takes the mock panel (15 questions, pass mark 12, `prep-local\STUDY-GUIDE.md`)
and the assistant checks the `.docx`. If the mock panel scores 12 or more, the documents go in on Friday. If
not, they go in on **Monday 2026-10-12 at the latest, with no further move.**

**What led to it.** Wednesday 2026-10-07 passed without a submission: the Word file did not exist yet, and the
paste-ready HTML was made only that evening (WORKLOG 2026-10-07). The student told their professor about the
re-presentation delay and that the work is still in progress, and the professor accepted a new date (as stated
by the student, 2026-10-08; whether the January target was mentioned is not stated).

**Why a latest date.** This is the second missed date, after 2026-10-02. The date only decides when the panel
sets the re-presentation (3 to 7 days after the submission). The lab work, which decides the January target,
shares the student's days with study and documents, so an open "submit when ready" keeps taking lab days.

**What it costs.** The lab work planned from Thursday 2026-10-08 starts the working day after the submission,
2026-10-12 or 2026-10-13. The 2026-10-23 checkpoint (DC-01, settings, value keying, network-logon test, golden
snapshot) then has about nine working days, and the 2026-09-29 entry says one missed checkpoint moves the
defense to February or later. The re-presentation falls between about 2026-10-12 and 2026-10-19.

**Cost if wrong:** if the Word file or the mock panel slips again, Monday is the backstop; past Monday, the
next move is a decision about the January target, not about the submission date.

## 2026-10-07 - The system stays a desktop application; Revision 8 answers the panel's instruction to declare it web-based and asks the panel to confirm

**Decision, by the student, chat 5e235b74:** keep the desktop application (2026-09-14). Do not change FINAL.
Answer the panel's instruction in `T1-REVISIONS-LIST.md`, Revision 8, and point to it from Q8.

**What the record had missed.** The title-defense transcript (pasted by the student 2026-10-07) shows the
panel chair's closing instruction: the topic document must declare the system web-based ("kailangan
naka-declare ... na web-based siya"). The stated reason was access: an engineer should not have to go to each
computer, for example in another building. Earlier, asked if the student had changed their mind, the student
said "Opo, pwede po." The 2026-09-14 entry and OPEN-QUESTIONS 17 treated this as a question nobody had
decided, not as an instruction.

**Why, as written into Revision 8.** (1) The access concern is already met: nothing is installed on the
monitored computers, and the attack tests start through a channel the organization controls, so the operator
never goes to them. In the lab the operator works from the VM host, because `vmrun -T ws` controls only local
virtual machines; a first draft of Revision 8 implied work from anywhere on the network and was corrected the
same chat. (2) A hosted server,
sessions and a login serve many users of one copy; the method needs one operator per run (2026-09-14).
(3) A web application would add a network service able to start attack tests, with its own login to secure;
the desktop design keeps the credentials readable only by the operator's MFA account and adds no login of its
own (2026-10-01). (4) Python runs on Windows, Linux and macOS. (5) A web front end can be added later on the
same core without changing any measurement.

**What it commits to.** Revision 8 says the interface toolkit "runs on all three" operating systems. Both
desktop candidates of 2026-09-14, CustomTkinter and PySide6, do (general knowledge, `(unverified)` here). A
browser-based toolkit such as Streamlit would now contradict Revision 8, so the 2026-09-14 recommendation of a
desktop toolkit follows from this entry.

**Cost if wrong:** the panel can refuse and require a web application. Then a web front end goes on the
existing core, with a login, sessions and access control of its own, and the 2026-10-01 rule "the system adds
no login of its own" is reversed. That is new work in a January plan with no spare time `(unverified how
much)`. The answer is asked for openly, so a refusal comes at the re-presentation, not at the pre-oral.

---

## 2026-10-02 - The revised documentation is submitted on Wednesday 2026-10-07, not Friday 2026-10-02. Checkpoint 1 is missed

**Decision, by the student, chat 243e446b:** the submission moves five days, to Wednesday 2026-10-07. From
Saturday 2026-10-03 to Tuesday 2026-10-06 the student studies the activity diagram box by box and the
panel's eleven questions, following `prep-local\STUDY-GUIDE.md` in the thesis folder. The student's reason:
to understand the work well enough to answer every panel question before the documents go in.

**Why it is reasonable.** The panel sets the re-presentation 3 to 7 days after the submission, and said it
will focus on the activity diagram. From 2026-09-29 to 2026-10-01, studying one box changed FINAL three
times (the operator-access row, "about seven" to "about three", six preconditions to seven), and a fourth
fix is waiting. A FINAL submitted on 2026-10-02 would have carried those errors. No Word copy of FINAL
exists yet (OPEN-QUESTIONS 15).

**What was said against it before the student chose.** Understanding is not needed to submit, only for the
re-presentation, and study time exists after the submission. In those three days the study covered one
box, because six side tasks took the time. So the plan has four rules: one box at a time with an
explain-back; no document changes during study, with all fixes in one batch on Tuesday; no side work; a
time limit per box. Readiness is tested on Tuesday: a mock panel of 15 questions, pass mark 12.

**What it costs.** Checkpoint 1 of 2026-09-29 is missed, and that entry says one missed checkpoint moves
the defense to February or later. The lab work planned from Monday 2026-10-05 starts Thursday 2026-10-08 at
the earliest, so the 2026-10-23 checkpoint has three fewer days. The re-presentation falls between
2026-10-10 and 2026-10-14. The January target is not changed by this entry; it is at more risk.

**Cost if wrong:** if the study again turns into side work, Wednesday is missed too. The Tuesday mock panel
shows this a day early.

## 2026-10-01 - The attack-test list is chosen from the rules: each test covers the ATT&CK technique of a shipped Wazuh rule that reads a kept change's evidence

**Decision, by the student, chat 243e446b:** the one pinned attack-test list (2026-09-28) is chosen from the
rule set, not from the changes alone. For each kept change, the Wazuh rules that read its evidence
(OPEN-QUESTIONS 1, "Which changes a Wazuh rule depends on") name their ATT&CK techniques, and the list takes
Atomic Red Team tests (commit `cb486d9`) for those techniques. Two additions that do not come from a rule:
the network-logon test (2026-09-29), and tests whose evidence the class B negative controls remove, so those
changes have something to act on.

**A test is kept only if** it runs on the lab's Windows 11; it needs no internet after the golden snapshot;
it needs no one at the keyboard and cleans up after itself; it is not destructive; its definition reads
correctly with `-ShowDetailsBrief` (runbook 3.8); and it completes in every spike control run without an
unusual swing in its event count (OPEN-QUESTIONS 22). The list is kept short, because it runs in every window.

**Recorded for each test:** the technique ID, the test number, and the library commit. One hash over the
list goes into the hashed parameters.

**Why.** Every test is then tied to a detection that really runs, so each one matters for the blind-spot
question, and "why these tests?" has a checkable answer: the rules chose the techniques. Choosing from the
changes alone would add tests whose evidence no rule reads. Those would still feed the statistical
comparison, but they would lengthen every window.

**What it means.** The list depends on the rule set, so the two are chosen and pinned together in Box 1;
changing either one makes a new environment. The tests themselves do not depend on Wazuh: they run the same
under any rule set, and Wazuh cannot stop one, because active response is off (2026-09-03).

**Not done:** the list itself. It is chosen before the spike, and the spike then tests its stability.

**Cost if wrong:** low. Evidence that no rule reads is exercised only when a chosen test happens to produce
it, so C2, C6 and C7 may get little stimulus. Under choice 1 (the entry below) they affect no detection
anyway.

## 2026-10-01 - The study uses Wazuh 4.14.7's shipped rules, exported whole; a change whose evidence no rule reads is reported as affecting no detection (choice 1)

**Decision, by the student, chat 243e446b, in two parts:**

1. **The rule set is Wazuh's own.** The rule set installed with the pinned manager `4.14.7-1` is exported
   whole from SIEM-01 (`/var/ossec/ruleset/rules/`, plus `/var/ossec/etc/rules/` if it holds custom rules),
   not picked by hand. Its version and one hash over the folder go into the hashed parameters. The index
   keeps the rules that read a Windows event key: 454 rules in 15 files at tag `v4.14.7`. Sigma is not used;
   the clone at `da9bb07` stays a record of the T3 count. The student's reason: "to not complicate things".
2. **Choice 1: accept what the shipped rules give, and report it.** With these rules only C1, C3 and C5
   have a rule that reads their evidence while the attack still works (OPEN-QUESTIONS 1, "Which changes a
   Wazuh rule depends on"). The study reports that plainly. It does not add Sigma rules for the other
   changes (choice 2). It writes no rules of its own to create dependencies (choice 3), because the study
   would then report blind spots it had made itself.

**Why Wazuh's rules.** The thesis asks whether the detections a SIEM actually runs go blind. On SIEM-01
those are Wazuh's rules; Wazuh does not run Sigma rules directly. Phase 5's "confirm the rule now fires" can
be checked on SIEM-01 only with Wazuh's rules. The version is already pinned with the package.

**What it changes.**
- **Positive cases: about 3, not about 7.** Supersedes in part the two 2026-09-29 entries that expected
  about 7 measurable class C changes. About 7 may still change telemetry, but only C1, C3 and C5 can blind a
  shipped Wazuh rule. C4's only affected rules (92652, 92657) detect pass-the-hash, which C4 blocks, so it
  behaves like class B. C2, C6 and C7 have no rule that reads their evidence.
- **The value-keying list follows the rule set.** A field is keyed by value only when a rule matches
  specific values of it (2026-09-29). With Wazuh's rules: `GrantedAccess` qualifies (rule 92900 matches
  `0x1010|0x40`), `LogonType` qualifies (60118 matches `2`; 92653 and 92656 match `10`), and
  `AuthenticationPackageName` qualifies (92652 matches `NTLM`). `LmPackageName` and `TicketEncryptionType`
  do not: no rule reads them, so under FINAL Module 2 they are not tracked at all, and C2 and C7 leave the
  key unchanged. The final list is still set after the C3 capture.
- **The statistical comparison keeps its test cases** from every change that moves a tracked key, class B
  included. What shrinks is the number of real blind spots the study can show.
- **Changed the same day, approved by the student:** FINAL "Scale of the Experiment" and
  `T1-REVISIONS-LIST.md:141` no longer say "about seven"; both now say the lab uses Wazuh's shipped rules
  and that a first check finds about three changes a rule depends on. STATUS updated. **Still to change:**
  `DEFAULT_TRACKED_FIELDS` in `eventkey.py`, when the index is built.

**Not checked** `(unverified)`: the per-change result comes from a text search of the rule files at tag
`v4.14.7`, not a reading of all 454 rules, and parent-rule conditions were not followed. Whether those files
equal the ones installed on SIEM-01 needs a hash comparison there. The index, once built, gives the exact
list.

**For the defense:** "Why do only three of your changes produce blind spots?" Because a blind spot needs a
detection that reads the evidence, and the SIEM's own rules read the evidence of only three. The others
change telemetry that no shipped rule uses, and the system reports them as affecting no detection. That is
a result, not a failure.

**Cost if wrong:** if the search missed a rule, a change is misclassified. Low, and caught before data
collection by the index and the hash comparison. If the panel expects more positive cases, choice 2 (Sigma
for the rest) is still possible before data collection.

## 2026-10-01 - Operator access is a precondition: the credentials are limited to one account that signs in with MFA; the system has no login of its own

**Decision, by the student, chat 243e446b:** FINAL's preconditions table gains a seventh row. The passwords
and the key the system uses to reach the hosts and the SIEM archive are readable only by the authorized
operator's account, which signs in with multi-factor authentication. The organization provides it, as
existing access control. The system adds no login of its own. The written-authorization row stays as it is.

**Why.** The student's point: a typed ticket number proves nothing, because anyone can type one. The student
proposed MFA and administrator-only use. Placed inside the system, that fails: the system is a Python program
on the operator's computer (2026-09-14), so anyone who can run it can also edit it, or call `vmrun` with the
stored password, and skip the check. Without the credentials the system cannot touch any machine, so
limiting them is the control that cannot be bypassed from inside the program. MFA proves who the operator
is, not that a second person approved. Approval stays with the written-authorization row (separation of
duties, NIST SP 800-53 AC-5).

**Proposed, not decided:** detection. A SIEM rule that alerts on attack-test activity with no registered run
ID, and the operator's account name in each run's manifest record part. Every run already leaves fence events
with its run ID in the SIEM, and the export tool cannot delete them (runbook Phase 6).

**Changed:** `proposal-form-FINAL.md`, the preconditions table (one row); `T1-REVISIONS-LIST.md`, Revision 9,
"six" to "seven" with the new item named. Not changed: a Word copy of FINAL, if one was already made.

**Cost if wrong:** low. One table row; no code and no measurement changes. In the lab the operator is the
student and the credentials are in `C:\Users\Elijah\.telos\`; whether that folder is readable only by one
account is not checked.

**For the defense:** "Why does your system have no login?" Because a login inside a program on the
operator's own computer can be skipped. The control sits on the credentials, and the SIEM records every run.

## 2026-09-29 - The control-run check and field-loss pairing stay in the design, and are built before data collection (items 24, 30)

**Decision, by the student, chat 27d2595d:** the activity diagram keeps both steps as drawn. The check that
stops the setup when a control run recorded nothing (item 24) is built into `VarianceModel.from_control()`
or before it, and `field_loss_pairs()` is connected to `analyse()` and the report (item 30). Both are
built before data collection, with the lab work from 2026-10-05.

**Why.** The panel will focus on the activity diagram at the re-presentation. Keeping the steps keeps the
submitted design unchanged; removing them would have meant a new limit and a changed diagram. Both are
small in code: the check mirrors `capture_problem()`, and pairing is already built and tested.

**Cost if wrong:** low. Until built, the diagram shows two steps the code does not run, which must be said
plainly if the panel asks (PROMPT-new-chat section 6).

## 2026-09-29 - Target: final defense by end of January 2027. Scope keeps every measurable class C change (item 25)

**Superseded in part:** "about 7" positive cases became about 3 under Wazuh's shipped rules (2026-10-01,
choice 1). The submission dates were moved twice (2026-10-02, 2026-10-08).

**Decision, by the student, chat 27d2595d:** the final defense is targeted for the end of January 2027.
Scope keeps every class C change that the lab can measure. When time runs short, the cut is made in
this order: the graphical interface is reduced first, then the class B negative controls are reduced.
The spike, by 2026-10-31, sets the final number of changes. "16 changes" is no longer a target.

**The dates, as stated by the student on 2026-09-29.** The school's deadline for the final thesis is
**4 June 2027**; no record of it existed in this repo before today. The student's own earlier target was a
final defense in December 2026, weeks 3 and 4, as FINAL's Gantt chart shows. That plan slipped at its
first lab rows: "Laboratory Build and Telemetry Acquisition" and "Preliminary Trial", both September 2026,
produced no capture run. The student wants to finish the course as soon as possible.

**Why January, and the risk stated to the student before choosing.** March 2027 was recommended. January
gives four months, the same length as the Gantt plan that slipped, and this plan adds work the old one did
not have: DC-01, a network-logon test, and value keying (the three entries below). One missed checkpoint
moves the defense to February or later. 4 June 2027 stays the hard limit and leaves time for the
revisions a final defense usually brings.

**Why keep class C.** Class C changes are the positive cases, where a blind spot can exist. OPEN-QUESTIONS
1 says fewer than about 8 makes the precision and recall comparison weak, and with DC-01 and value keying
about 7 are measurable (C8 is blocked, item 2). Class B is reduced, **not removed**: the comparison with the
naive method needs changes where telemetry is lost but no blind spot exists, and class B is that set
(OPEN-QUESTIONS 1). The graphical interface is cut first because FINAL's own Gantt note already names it
"the component that would be reduced first if the schedule slips".

**Checkpoints, proposed 2026-09-29.** Dates are estimates `(unverified)`; the tracked list is in STATUS.md.
1. 2026-10-09: adviser told of the slip and the new target; re-presentation date requested.
2. 2026-10-23: DC-01 built, WIN-EP-01 joined, Sysmon rule and audit settings in place, value keying coded
   and tested, network-logon test designed, golden snapshot taken.
3. 2026-10-31: spike run, its six answers recorded, final number of changes set.
4. Re-presentation, on the panel's date.
5. 2026-11-30: data collection done.
6. 2026-12-18: the rest of the system and the evaluation done.
7. 2027-01-08: full draft to the adviser.
8. By 2027-01-31: final defense.

**Corrected later on 2026-09-29:** checkpoint 1 cannot request a date. The panel sets the re-presentation
date only after the revised documentation is submitted, about 3 to 7 days later (student). The student's
target is to submit by Friday 2026-10-02; STATUS.md holds the corrected list.

**What must change outside this file:** FINAL's Gantt chart and every "16 changes" in FINAL and the other
submission documents. The Gantt change probably needs the adviser's approval. Not done.

**Cost if wrong:** if the spike shows even the class C set cannot be captured in time, the evaluation rests
on fewer positive cases and says so, or the date moves toward March. Both are recoverable only if the
spike runs on time.

## 2026-09-29 - Build DC-01, with a test that makes network logons (item 21, option 1)

**Note, 2026-10-08:** the "Why" below counted about 7 measurable class C changes. Under Wazuh's shipped
rules (2026-10-01) the positives are C1, C3 and C5, and none needs a domain. Whether DC-01 still earns its
days is OPEN-QUESTIONS 32, point 4. This entry is not reversed.

**Decision, by the student, chat 27d2595d:** build `DC-01` as `lab/blueprint.md` Tier B specifies (Server
2022 Evaluation, AD DS and DNS, 2 vCPU, 6 GB, 60 GB, on F:). WIN-EP-01 joins the domain. DC-01 gets its own
Wazuh agent, because 4768 and 4769, and 4776 for domain accounts, are written on the domain controller. A
test that makes network logons during every capture window is designed and added to the pinned test list.
All of it happens **before the golden snapshot**.

**Why.** The archive count on 2026-09-26 found 4768, 4769 and 4776 at zero on every date and 0 network
logons among 2,892 (OPEN-QUESTIONS 21). C2, C4, C6 and C7 have nothing to act on without a domain. With
the value keying below, about 7 class C changes become measurable instead of 0. The golden snapshot does
not exist yet, so joining the domain now costs no re-taken snapshot.

**What it costs.** One to two days to build (item 21's estimate, `(unverified)`), plus designing the
network-logon test, which does not exist. Two blueprint rules change: DC-01 is no longer "optional", and
the rule "suspend all Tier B VMs during actual capture runs" cannot apply to it, because the capture needs
it running. The blueprint budget for Tier A and B fits (49 GB of 64). The Server 2022 evaluation period is
180 days `(unverified)`, which from October 2026 ends after the January target.

**For the defense:** the student must explain Kerberos ticket requests (4768, 4769) and NTLM credential
validation (4776). The class C changes need that knowledge anyway.

**Cost if wrong:** one to two days and a larger lab. If the network-logon test cannot be built, C2 and C4
still see zero before and zero after.

## 2026-09-29 - The event key adds values for a short list of fields; Sysmon records `lsass.exe` access; C3 uses `RunAsPPL = 2` (item 18; supersedes in part 2026-09-04)

**Superseded in part, 2026-10-01:** the candidate list below follows the rule set. Under Wazuh's shipped
rules it is `GrantedAccess`, `LogonType` and `AuthenticationPackageName`; `LmPackageName` and the ticket
encryption type are not read by any rule, so they are not tracked.

**Decision, by the student, chat 27d2595d, in three parts:**

1. **Value keying for a short list of fields.** For those fields the key records the value, grouped into a
   few classes, not only that the field was filled. A field is keyed by value only when detection rules
   match on specific values of it (item 18, option 1). The final list is set after the C3 capture.
   Candidates from the catalogue, `(unverified)` until then: 4624 `LogonType` (C1, C5), 4624
   `LmPackageName` (C2), Sysmon 10 `GrantedAccess` (C3, C8), and the 4768 and 4769 ticket encryption type
   (C7). This also fixes `DEFAULT_TRACKED_FIELDS`, which tracks 4776 `PackageName`, a field that never
   changes, and does not track 4624 `LmPackageName` or 4768 and 4769 at all.
2. **An `lsass.exe` rule in the Sysmon `ProcessAccess` section.** The pinned config records no Event 10
   today (0 of 14,102 Sysmon events). The config hash changes, so the pinned table below is updated before
   the golden snapshot. The added event volume is not measured, and the config's own comment warns about
   load.
3. **C3 uses `RunAsPPL = 2` in the lab**, stated as a deviation from CIS Windows 11 Enterprise v5.1.0
   18.9.27.2, which requires the UEFI lock (value `1`). Value `1` writes a UEFI variable the registry
   cannot undo, and whether a snapshot revert clears it is untested. Microsoft's LSA protection page says
   LSASS runs as a protected process with or without the lock.

**Why.** Six of the eight class C changes change a value, not whether a field is filled (OPEN-QUESTIONS 18).
The key as built on 2026-09-04 records presence only, so `GrantedAccess` going from one number to another
leaves the key and the count the same, and the analyser reports UNCHANGED. The value change is the blind
spot in those cases. The 2026-09-04 entry says key format changes are cheap only while no real runs exist,
which is still true today.

**What it supersedes:** 2026-09-04's rule that the key records "that" a field carried a value and never
"which" value, for the listed fields only. Every other field is still keyed by presence. 2026-09-04's
honest limit applies here too: better keys help the naive method equally.

**What must change, before the re-presentation:** `eventkey.py` and its tests; the event key definition in
FINAL Module 2, the activity diagram, the diagram explainer, the panel response, the revisions list and
PROMPT-new-chat section 4; and the `key-values` check in `tools/check_docs.py`, which today flags any key
defined by values. Not done.

**Still open inside item 18:** which registry key the C3 script sets, Microsoft's direct key or the CIS
policy key (item 18, consequence 3).

**For the defense:** the rule to explain is "a field is keyed by value only when a detection rule matches
on its value".

**Cost if wrong:** more keys, so fewer of them reach 30 events (item 25's power question). Grouping values
into a few classes limits this; the spike measures it.

## 2026-09-29 - Process creation and credential validation auditing go into the golden snapshot (item 20)

**Decision, by the student, chat 27d2595d:** before the golden snapshot, WIN-EP-01 audits Process Creation
(success) with `ProcessCreationIncludeCmdLine_Enabled = 1`, and audits Credential Validation. DC-01 audits
Credential Validation too, because domain 4776 events are written there. The exact success and failure
settings follow the CIS benchmark the catalogue cites, matched when the script is written.

**Why.** 200 process starts produced 0 Security 4688 events, because Process Creation auditing is off, and
the proposal's main key example is a 4688 key (OPEN-QUESTIONS 20). The endpoint is also out of line with
the CIS control that OPEN-QUESTIONS 1 cites. 2,285 local credential checks produced 0 4776 events,
probably because Credential Validation is off; **check it first** inside the guest with
`auditpol /get /subcategory:"Credential Validation"`.

**What it costs:** more events per window. Each harness `vmrun` guest call probably writes a 4776 as well as
its batch logon (item 26, `(unverified)`), so the harness must count its own calls.

**Cost if wrong:** low while no snapshot exists. After the golden snapshot, changing it means taking the
snapshot again.

## 2026-09-28 - The whole-profile chi-square is reported, not a filter. Every event key is tested (item 29, finding 1)

**Decision, approved by the student:** the chi-square test over the whole profile no longer decides
whether any key is tested. Every key is tested every time. The chi-square result is kept in the report
as a summary of whether the profile changed at all. A capture that recorded nothing still stops the
analysis as NOT_TESTABLE.

**Why.** Reproduced on the code, with made-up data: 299 steady keys and one key falling from 198
events to 0 gave a chi-square p of 0.999, so `analyse()` returned UNCHANGED with no key tested. The
same key tested on its own is LOST with q = 3.1e-84. One key lost among many steady ones is the usual
shape of a blind spot, which is where a test over the whole table is weakest. Keeping the gate and
stating the miss as a limitation would mean the method misses its main target.

**What protects against false findings now:** the Benjamini-Hochberg correction across all keys, which
holds the expected share of false findings to alpha. In the same run, testing every key flagged none of
the 299 steady keys. That was made-up data where the noise model was right by construction.

**What changed:** `differential.py` `analyse()` and module docstring, `model.py` `ProfileOutcome`
(CHANGED now means at least one key LOST or REDUCED), `report.py`, two new tests and one rewritten,
both figures, FINAL's Objective 4 wording, the explainer, the panel response and the revisions list.
OPEN-QUESTIONS 23's second half, the gate passing on noise, no longer matters, because the gate no
longer filters.

**Cost if wrong:** more false findings on real data, if the 5-run noise model underestimates the real
noise. The Phase 7 spike checks it: count findings on control-versus-control comparisons, where there
should be none.

## 2026-09-28 - One attack-test list is pinned for the whole study, in Phase 0 (item 29, finding 2)

**Decision, approved by the student:** the attack tests, the window length and the repetitions are
fixed once, in Phase 0, and every control, pre-change and post-change run uses them. Phase 1 no longer
chooses tests. Two runs are compared only when their hashed parameters equal the control runs'. In the
code, a key the control runs never saw is INCONCLUSIVE and not tested.

**Why.** The noise model was measured in Phase 0 with "the stimulus", while the tests were chosen later,
per change, and FINAL and the panel response allowed a different set per change. A key the control runs
never saw got a coefficient of variation of 0 and the Poisson dispersion, the least noise the code can
express, so any drop passed the noise condition. The previous code reported such a key as LOST, verified
2026-09-28 by the new test. `lab/blueprint.md` already specified one pinned technique list.

**Cost if wrong:** the one list must exercise everything the catalogue's changes affect, and choosing it
is not done yet. Per-change test lists are future work: each would need its own Phase 0.

## 2026-09-28 - Remediation candidates are two levels. Ranked discriminating fields are dropped (supersedes D1's third level; item 29, finding 3)

**Decision, approved by the student:** the system suggests surviving sources and known compensating
controls. It no longer ranks discriminating fields. D1's main point stands: the system never drafts
detection rules.

**Why.** D1 defined the third level as fields that "separate adversary activity from control activity".
Every capture in this design runs the attack suite, the 5 control runs included, because "control" here
means no configuration change, not no attack. The study records no attack-free activity, so the ranking
has nothing to compare against. Adding attack-free captures was the alternative. It was rejected for
lab time and harness work the schedule does not have.

**What changes for the panel:** question Q5, "can it suggest a fix?", is answered "yes, at two levels",
with the third named as future work because it needs attack-free captures.

**Cost if wrong:** low. The ranking can be added later with attack-free captures, and it changes no
measurement.

## 2026-09-28 - Fixes are applied by script, like the change. D2 extends to Phase 5 (item 29, finding 4)

**Decision, approved by the student:** a telemetry fix is supplied as a script with an ID, like the
hardening change. A re-validation run restores the configuration snapshot, applies the change script,
then the fix script, confirms both on the host, and only then captures. A rule re-validation replays the
manifest the same way: restore, apply the change, run the pinned tests. The accepted baseline is the
snapshot plus the scripts applied on top, and a later run rebuilds it the same way.

**Why.** Under D2 every capture begins by restoring the configuration snapshot. A fix made once by hand
was erased by that restore, together with the hardening change. The re-validation would then measure the
original machine, match the pre-change profile, and report "coverage restored" for a fix that was never
tested: a false FIXED.

**Scope in this study:** each change is tested alone against the unchanged snapshot (Scope and
Limitations, limit 2), so the list of accepted scripts is empty for every study run. It matters for real
use. Phase 5 is designed, not built.

**Cost if wrong:** low. Scripts are what D2 already requires for changes.

## 2026-09-26 - T1 is the final thesis. There is no fallback topic (supersedes the open choice in 2026-08-19)

**Decision, by the student, in their words:** "No fallback this time. T1 is the final thesis title."

**What it closes.** The 2026-08-19 entry "T3 loses its fallback status" listed two paths if T1
failed its spike, fixing T3's validation or switching to T2, and said "Not yet decided: which of the
two paths above." This entry decides: neither. T2 and T3 are not chosen and are kept as a record only.

**A correction this makes necessary.** Before today, `CLAUDE.md`, `PROMPT-new-chat.md`, the T3 README
and OPEN-QUESTIONS 25 all said T2 was the fallback, and OPEN-QUESTIONS 25 said this file already
recorded it. **This file never did.** No entry chose T2. The claim passed from document to document
with no decision behind it, the same failure as OPEN-QUESTIONS 17. Found 2026-09-26 by checking the
documents against this file.

**What changes.** The Phase 7 spike is no longer a choice between topics. It still measures run-to-run
variance and real wall clock, and its result now decides scope only.

**Cost if wrong:** if the spike shows T1 cannot finish before the deadline, there is no other topic
ready to switch to. The only lever left is scope, meaning fewer hardening changes, as OPEN-QUESTIONS 25
describes. That makes the item 25 scope decision more urgent, not less.

## 2026-09-14 - The system is a Python application with a graphical interface beside the SIEM, not a web application (closes OPEN-QUESTIONS 17)

**Decision, by the student:** no web application. The system is a Python application with a clean
graphical interface, running on a machine beside the SIEM. It is not inside the SIEM and not on the
monitored endpoints.

**The student's reason:** the system works beside the SIEM, so a web application is not needed.

**Why that reason holds.** A server-side web application brings a server to host, user sessions,
access control, and a deployment of its own. Those serve many people reaching one shared instance
from their browsers. Nothing in the method needs that. What the method needs is one operator who
defines a run, watches it, and reads the result, on a machine that can reach the SIEM's event
archive and the hypervisor. A graphical interface over the existing Python package does that.

**What it closes.** OPEN-QUESTIONS 17: "server-side web application ... distributed as a set of
containers" was marked ASSUMPTION four times in a draft, never confirmed, and then written as fact
into `proposal-form-FINAL.md`, `T1-PANEL-RESPONSE.md` and `T1-REVISIONS-LIST.md`. Those were the
last three real defects the document checker reported.

**What stays exactly as it was:**
- The analytical core is the Python package in `src/telos/`. The interface calls it.
- The command line still runs the experiments reported in the study, so every measurement comes from
  the same code the interface uses.
- **No new agent on the endpoints.** The endpoints keep the SIEM agent, which only collects.

**One correction made in the same paragraph, backed by an existing decision.** The documents said the
system "drives the experiment from the server side through that existing channel", meaning the SIEM
agent. The Wazuh feature that lets the manager run commands on an endpoint, active response, was
**disabled** on 2026-09-03, with the reason that the measuring instrument must not be able to change
the machine under test. So the documents now say the attack tests reach the endpoint through an
execution channel the operator controls, the hypervisor's guest operations in the laboratory, and that
the SIEM agent executes nothing.

**Cost if wrong:** an organization that wants several analysts sharing one instance from their
browsers would need a web front end later. Because the core is a package and the interface only calls
it, that front end could be added without changing any measurement or any stored run.

**Not decided here:** which toolkit builds the graphical interface. That is a separate choice with its
own schedule cost, and nothing in the documents names one.

**Recommendation given the same day, not accepted or rejected yet.** A **desktop** toolkit, not a
browser-based one. Python tools that draw their interface in a browser, Streamlit for example, run a
small web server on the operator's machine, and a panelist can then say the system is a web
application after all, reopening the question this entry closes. Between desktop options:
**CustomTkinter**, built on Python's standard Tkinter, simpler and easier to explain line by line at a
defense; or **PySide6** (Qt), more polished with more to learn. The lean was CustomTkinter,
`(unverified: a short prototype should come before committing)`. The schedule puts the interface in
November, after the harness and the spike, so this is not urgent.

## 2026-09-14 - The title is the panel's proposed wording, verbatim, with no grammar correction (closes OPEN-QUESTIONS 0)

**Decision, by the student:** the title is exactly what the panel proposed:

> Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential Analysis
> Algorithm

No article is added. No other word changes.

**Why.** It is the wording the panel approved. Any change, even one word, produces a title the panel
did not see. OPEN-QUESTIONS 0 already recorded that keeping the panel's wording costs nothing: "use it
everywhere and stop revisiting it."

**What changes in the documents.** `proposal-form-FINAL.md` and `T1-REVISIONS-LIST.md` carried "Using
**a** Differential Analysis Algorithm". Both now carry the panel's wording. `T1-REVISIONS-LIST.md` also
said the article was "raised as a wording question to the adviser". No record shows that question was
ever asked, so that sentence was removed rather than left as a claim. The public `README.md` already used
the panel's exact wording and needed nothing.

**The obligation this creates, and it is not optional.** The title names a category, "Differential
Analysis Algorithm", not a specific method. **Chapter 3 must name the specific algorithm and define it
once**, as the composite of profile alignment, the capture check and global gate, dispersion-aware rate
testing, Benjamini-Hochberg correction, and classification. *(Updated 2026-09-28: the chi-square is no
longer a gate. Chapter 3 defines it as a whole-profile summary that never stops the per-key tests; see
the 2026-09-28 entry.)* `T1-PANEL-RESPONSE.md`'s title section
already warns that a panel should not accept "Algorithm" attached to a category with nothing behind it.

**Cost if wrong:** low. A reader may notice the missing article. The answer is one sentence: it is the
panel's approved title, used verbatim.

**Not changed:** the filename `Detecting Security Blind Spots Through Pre- and Post-Hardening Events
Using a Differential.docx` still contains "a". It is a filename, not the title, and renaming the
student's file was not asked for.

## 2026-09-14 - Correction to 2026-09-09: PNG can be rendered on this host, and the renamed PNGs are gone

**This supersedes one sentence of the 2026-09-09 entry "Figures are generated from a script, not
hand-drawn". That entry is kept as written.**

**What it said:** "It does not render PNG. No renderer is installed and none is added."

**What is true.** The first sentence is right about the figure scripts: they write SVG and nothing
else. **The second is false.** This log's WORKLOG entry of 2026-08-20 records rendering a slide to
PNG "through the installed PowerPoint COM object". And on 2026-09-14 Microsoft Edge in headless mode
rendered all four figures to PNG so they could be looked at:

```
msedge.exe --headless=new --disable-gpu --hide-scrollbars --screenshot=<scratch>.png ... <figure>.svg
exit=0
```

**The decision does not change.** The figures are generated as SVG, and SVG is what goes into Word,
because Word keeps it as vector. Only the reason given was wrong. PNG renders made for checking are
scratch files and are never committed or placed in the documents folder.

**How the false sentence spread.** On 2026-09-12 it was repeated into `T1-PANEL-RESPONSE.md` as
"Nothing in this project renders PNG", in the same edit that kept a reference to PNG files "beside"
the SVGs. Both were corrected on 2026-09-14.

**A related fact with no record.** The four `*.SUPERSEDED-2026-08-28.png` files that WORKLOG
2026-09-09 records renaming are no longer in the documents folder. Nothing says when they were
removed or by whom. The only PNG left there is `T1_Activity_Diagram_Swimlane.png`, the original
submitted diagram.

**Cost if wrong:** none. No result depends on it.

## 2026-09-14 - The accepted baseline is promoted when a finding closes either way: FIXED or ACCEPTED

> **Superseded in part, 2026-09-28.** Promotion on both closures stands. What the accepted baseline
> **is** changed: not "the current profile", the latest capture, but the configuration snapshot plus
> the change and fix scripts applied on top of it, so a later run can rebuild it the way every
> capture is built. See the 2026-09-28 entry "Fixes are applied by script, like the change".

**Decision:** when a finding closes, the current profile becomes the accepted baseline that later runs
are compared against. That happens after a passing re-validation (closed as FIXED) **and** after a
documented risk acceptance (closed as ACCEPTED).

**Why.** The two documents disagreed. The activity diagram promoted the baseline only after FIXED.
`T1-PANEL-RESPONSE.md:528` promoted it "once a change is accepted". After a risk acceptance the changed
machine **is** the machine the organization runs. Comparing every later run against the pre-change
profile would report the accepted loss again on every run, and a finding that reappears each time
teaches the reader to ignore findings.

**Which profile.** "The current profile" means the latest capture: the post-change profile after an
acceptance or a rule fix, which does not change what the host emits, and the re-validation capture
after a telemetry fix, which does.

**What must follow:** the diagram's closing box reads "Close the finding as FIXED or ACCEPTED; promote
the current profile to the accepted baseline", and both paths enter it.

**Cost if wrong:** low. Nothing is built. If a reviewer wants acceptance to leave the old baseline in
place, it is one arrow in the figure and one sentence in the panel response.

## 2026-09-14 - A capture that recorded nothing is NOT_TESTABLE, never a finding (closes OPEN-QUESTIONS 16)

**Decision:** a run has one of three profile outcomes, **CHANGED, UNCHANGED or NOT_TESTABLE**. Any
repetition, in either phase, whose counts sum to zero across every key makes the run NOT_TESTABLE.
It never reaches the classifier and produces no findings.

**Why.** Measured against the previous code on 2026-09-14: an all-zero post-change phase passed the
gate with `p = 0` and every key with 30 or more events before was reported LOST. **A dead agent was
reported as blind spots.** An all-zero pre-change phase reported every key NEW. And a run where two of
three post-change captures recorded nothing was reported as "no significant change". Full evidence in
OPEN-QUESTIONS, Answered, item 16.

**Why zero is the right line.** Every real capture window contains at least the two fence events the
harness fires, each a Sysmon Event 1 from `telos-fence.exe`, verified in Phase 3. A hardening change
cannot remove the harness's own marker process. So a repetition with zero events is not a possible
result of any change in the catalogue. It can only be a broken capture.

**Why not report it and let a person decide.** Because the report would already have classified the
keys. A list of LOST findings with a footnote is still a list of LOST findings, and it is the first
thing a reader sees.

**Also decided in the same change:** a profile with exactly one informative key skips the chi-square,
because a 2-by-1 table has nothing to compare, and tests the key directly. Before, it was reported as
"no significant change" regardless of what happened to that key. And the gate now uses the alpha it is
given, closing defect one of OPEN-QUESTIONS 23.

**Cost if wrong:** low. A NOT_TESTABLE run is re-run. The only way this rule loses real data is a
hardening change that silences every event including the fences, which would itself be a finding worth
investigating by hand.

**What it does not catch, recorded so it is not assumed:** a capture that died partway through a window,
and an empty control repetition inflating the noise model. Both are listed under item 16's answer.

**Verification:** `55 passed`. Each new test's input was run against the previous code first, so each
is known to protect a real defect.

## 2026-09-14 - D3. In the activity diagram, a tinted box means "the proposed system performs this step", and the generator must enforce it

**Decision:** a tinted box, `system_box()` in `thesis/T1/figures/svgkit.py`, is used for every step the
proposed system performs and for nothing else. Every tinted box sits in the Proposed System lane. The
generator checks this and refuses to write a sheet that breaks it.

**Why.** On 2026-09-14 an outside review found the tint had three meanings at once, and none was true:

| Source | What it said the tint meant |
|---|---|
| `svgkit.py:121` docstring | "A step the proposed system performs" |
| `ACTIVITY-DIAGRAM-EXPLAINED.md:237`, `:246-248` | The same, and "point at the tinted boxes" when asked what the system does |
| `T1-PANEL-RESPONSE.md:113-115` legend | "New or corrected in this revision" |
| **What the script actually did** | New since the 2026-08-15 diagram. Verified against the original image: every tinted box is new, every white box is carried over or split from an original box |

Under the explainer's reading, four tinted boxes are not system steps. By x-coordinate, "Register the
environment" and "Restore telemetry" are in the engineer lane, "Configuration state changes" and
"Restore snapshot, run the stimulus" are in the environment lane. And the core of the method is white:
the per-key rate-ratio test and the box that builds the event-key profile.

**The defense instruction pointed at the wrong boxes.** A student told to point at the tint would have
pointed at four steps the system does not perform and missed the statistical test.

**Why this meaning and not "new since August".** "What does your system do" is a question a panel
asks. "Which boxes are new since your first draft" is not. The tint should answer the question that
will be asked.

**What must follow, in Step 3:** the four outside-lane boxes become white; the rate-ratio test, both
profile-building boxes, align, traverse, impact score and every other system step become tinted;
"Record no significant change" moves from the environment lane into the system lane, where it was
misplaced in the 2026-08-15 original; the panel legend at `:113-115` is rewritten; and the generator
asserts that every `system_box` x-coordinate lies inside the Proposed System lane, so the meaning
cannot drift a second time.

**Cost if wrong:** low. Presentational only. No measurement depends on it.

## 2026-09-14 - D2. A post-change run restores the configuration snapshot and applies the change by script, before the start fence

**Decision:** there is no post-change snapshot. Every post-change capture restores the same
configuration snapshot as the pre-change captures, applies the hardening change by script, reboots
if the change needs it, settles, and **only then** fires the start fence.

**Why the method.** `lab/blueprint.md:149` already says "Do not create 16 post-change snapshots", for
two reasons that still hold: the change stays version-controlled and auditable as a script, and F:
avoids 16 branching delta chains. The activity diagram (`make_activity_diagram.py:190-191`) and the
explainer (`:505`) said the opposite, "Re-run the identical manifest from the post-change snapshot".
`proposal-form-FINAL.md:343` and `T1-PANEL-RESPONSE.md:510` do not say which snapshot. This entry
settles it in favour of the blueprint.

**A third reason, found while deciding.** With one configuration snapshot for both phases, the
snapshot identifier is the same before and after the change. That is what allows a hash of the run
parameters to match between the phases at all. Under a post-change snapshot it never could.

**Why the order changes.** Blueprint run protocol steps 4 and 5, and runbook Phase 6 steps 4 and 5,
fire the start fence **first** and apply the change **second**, including "reboot if required". So the
change, its reboot and the boot event storm fall **inside post-change capture windows only**. A
confound is a second difference between the two phases besides the change being measured, and this
is one. New order:

```
1  revert to the configuration snapshot
2  start the VM
3  settle 180 s
4  post-change only: apply the change by script, reboot if required, settle 180 s again
5  start fence
6  Atomic Red Team suite
7  end fence
8  drain 120 s
```

**What it does not remove, stated honestly.** A post-change run still has one extra reboot before its
fence that a pre-change run does not. The second settle is meant to absorb it, and **that has never
been measured.** Phase 7 can check it with the control runs it already needs: a control run with an
extra reboot before the fence against one without.

**The manifest follows from this, and it was never defined.** Two documents define two different
manifests. `proposal-form-FINAL.md:127-130` lists parameters only. `lab/blueprint.md:178` lists
`run_id`, `phase` and fence timestamps, which change every run and could never hash equal. The manifest
therefore has two parts:

- **Hashed, must match between compared runs:** configuration snapshot ID, Atomic test IDs and
  versions, window length, repetitions, rule set version, thresholds, Sysmon config hash, agent version,
  harness commit.
- **Recorded, not hashed:** run ID, phase, change ID and change script hash, fence timestamps, host
  load, and the per-atomic exit statuses OPEN-QUESTIONS 22 requires.

**What must follow, in Steps 3 and 4:** the diagram's Phase 2 becomes the engineer supplying the change
script and its benchmark ID, and the application moves into the system's post-change loop; blueprint
steps 4 and 5 and runbook Phase 6 are reordered; explainer `:505` and the manifest wording are
corrected everywhere.

**Cost if wrong:** a change that cannot be applied by a script, for example one that needs Group Policy
or a firmware setting, would need a post-change snapshot for that change alone. Its snapshot ID would
then differ, and the hash rule would have to exclude it for that change and say so. None of the current
catalogue needs this `(unverified for C8, Credential Guard)`.

## 2026-09-14 - D1. The system ranks discriminating fields. It does not draft detection rules.

> **Superseded in part, 2026-09-28.** The third level, ranked discriminating fields, is dropped: the
> study records no attack-free activity to rank against. "No rule drafting" still stands. See the
> 2026-09-28 entry on remediation candidates.

**Decision:** the third level of remediation candidates is a **ranked list of the event fields that
still separate adversary activity from control activity after the change**. The system does not
generate a Sigma rule, a skeleton rule, or any other detection content.

**Why.** The documents disagreed and nothing settled it:

| Says the system drafts a rule | Says it does not |
|---|---|
| Diagram box, `make_activity_diagram.py:296-297`: "draft Sigma rule" | `proposal-form-FINAL.md:407`: "It does not author rules." |
| `T1-PANEL-RESPONSE.md:477`: "A skeleton Sigma rule" | `T1-REVISIONS-LIST.md:220`: the same sentence |

`ACTIVITY-DIAGRAM-EXPLAINED.md` did both: it quotes the box at `:675` and then describes ranked fields
at `:684-686`.

The submitted proposal is the authority after the code, and it says no. It is also the smaller and more
defensible claim. A ranked field list is a measurement the study can check. A generated rule invites
the question "how good are your rules", which Scope and Limitations item 7 already puts out of scope.
And rule induction is unbuilt work the schedule does not have.

**The answer to panel question Q5 does not change.** Can it suggest a fix? Yes, at three levels:
surviving sources, known compensating controls, and ranked discriminating fields.

**What must follow, in Steps 3 and 4:** the diagram box reads "surviving sources, known compensating
controls, ranked discriminating fields"; tier 3 at `T1-PANEL-RESPONSE.md:477` is rewritten; the
explainer's quotation of the box is updated.

**Cost if wrong:** low. If the adviser or panel wants rule drafting, it can be added later as an
extension that changes no measurement and no stored run.

## 2026-09-11 - A write filter is an accepted way to return a host to a known state (closes OPEN-QUESTIONS 19)

**Decision:** the requirement on a target host is **the ability to return it to a known state**, and
that can be met by a hypervisor snapshot, by the Windows **Unified Write Filter**, or by a disk
image. It is no longer "the host must be a virtual machine under a hypervisor supporting snapshots".

**The lab does not change.** WIN-EP-01 and SIEM-01 keep using `vmrun`, which reverts in seconds. UWF
costs a reboot per run. This decision is about **where the method can be deployed**, not about how
this experiment is run.

**Why.** `proposal-form-FINAL.md:240` states the VM precondition, and it is in the preconditions
table but **not** in Scope and Limitations, so a reader of the limitations never learns of it. It is
a larger restriction on where the system can be used than the Windows-only limit that *is* stated.
The snapshot was never the special part. Returning the machine to a known state is, and Windows
already ships something that does it.

**What was measured, on 2026-09-11.** All six steps of OPEN-QUESTIONS 19 passed on WIN-EP-01,
Windows 11 Education `10.0.26100.9168`, **unactivated**. The feature exists and installs; a write
made before a reboot is gone after it, files and registry alike; a change can be made permanent; a
40-minute window used 191 MB of a 1024 MB overlay with **zero** UWF events; and an identical
stimulus produced **exactly 100 of 100** Sysmon Event 1 with the filter both on and off. Full
evidence in OPEN-QUESTIONS, Answered section, and WORKLOG 2026-09-11.

**Two things this decision depends on, which a deployment must implement.**

1. **Every event must reach the SIEM before the reset.** Under UWF the machine's **entire local event
   log is discarded at reboot**, not merely the agent's unsent queue. This was measured, not assumed.
2. **The overlay must be watched during the run.** `uwfmgr overlay get-consumption` at both ends of
   a capture window, and `Microsoft-Windows-UnifiedWriteFilter/Operational` and `/Admin` checked for
   Event ID 2. A run that fills its overlay is corrupt while its numbers still look ordinary.

**Cost if wrong: low for this study, real for the deployment claim.** No result in this thesis
depends on UWF, because the lab uses snapshots. If UWF later turns out to be unusable on real
hardware, the precondition returns to what it was and nothing already collected is affected. What
would be lost is the wider deployment claim and the physical-machine path for Credential Guard
(C8, item 2).

**What is deliberately not decided here.** The wording change to `proposal-form-FINAL.md:240` and the
matching addition to Scope and Limitations. **That addition should happen regardless of this
decision**, because the restriction is real and the limitations section does not state it today.

**Known limits of the evidence, carried forward honestly:** no real capture harness existed, so the
window used a synthetic load that deleted its own files, making the measured 0.45 MB per minute a
floor rather than a forecast; only Sysmon Event 1 was compared end to end; and servicing mode, the
route needed for a change that is not a single registry value or file, was never tested.

## 2026-09-09 - Figures are generated from a script, not hand-drawn

**Decision:** every figure in this thesis is produced by a program kept in the repository. The
first is `thesis/T1/figures/make_activity_diagram.py`, which writes both sheets of the T1
activity diagram. Hand-authored SVG is not used again.

**Why.** The 2026-08-28 activity diagram still described the analysis as keyed on event type
alone, five days after the key changed on 2026-09-04. Four of its labels were wrong and one
activity had no box at all. The cause was not carelessness about that one edit. **The figure had
no source.** It existed only as SVG text with hand-computed absolute coordinates, so adding a
box meant shifting every coordinate below it by hand. Work that expensive does not get done, so
the figure silently drifted away from the code.

A generated figure changes the economics. Adding a step is one function call, and the layout
arithmetic is in Python where it can be read and checked.

**The second reason is defense.** A panelist may ask whether the diagram matches the
implementation. "It is generated from a script in the repository, and here is the commit" is a
better answer than "I updated it by hand."

**Cost if wrong:** low. The script emits plain SVG with no dependencies beyond the standard
library, so the output stays editable by any other tool if this convention is later dropped.

**What it does not do.** It does not render PNG. No renderer is installed and none is added.
Word inserts SVG directly and keeps it as vector, which is better for print than the PNG it
replaces.

**Verification:** both sheets were regenerated, opened in a browser, and read at full size
before being installed. The 2026-08-28 originals are kept as `*.2026-08-28.svg.bak` next to
them. Details and the full finding list are in WORKLOG 2026-09-09.

## 2026-09-04 - The unit of analysis is (event type + populated tracked fields), not event type alone (closes OPEN-QUESTIONS 1b)

**Superseded in part, 2026-09-29:** for a short list of fields the key now records the value, grouped
into a few classes, not only presence. See the 2026-09-29 entry on item 18. Not built yet.

**Decision:** an analysis key is the event type **plus which tracked fields were actually
populated**, written `Security-4688[CommandLine,NewProcessName]`. Chosen over the simpler
event-type-only key, and chosen now rather than deferred.

**Why.** A hardening change can leave an event firing at exactly its former rate while
emptying a field inside it. Disabling `ProcessCreationIncludeCmdLine_Enabled` leaves 4688
firing normally with an empty CommandLine, and every detection rule matching on CommandLine
goes blind. Keyed on event type alone, the rate never moves, the analyser correctly reports
UNCHANGED on the evidence it has, and the blind spot is invisible.

Under the composite key the same change produces a matched pair:

```
Security-4688[CommandLine,NewProcessName]   1247 -> 0      LOST
Security-4688[NewProcessName]                  0 -> 1247   NEW
```

A LOST and a NEW at the same rate under one event type is the signature of a field being
stripped, as distinct from an event type stopping.

**Why now and not later.** This defines the shape of every stored run. Deciding it after
collection would make every capture unusable. Full-time availability for the remaining weeks
made the more accurate option affordable, so the permanent risk was removed rather than
deferred.

**Which fields are tracked.** Not all of them; keying on every field would give almost every
event its own key. A field belongs in the key only if some detection rule reads it, because
losing a field no rule reads blinds nothing. `DEFAULT_TRACKED_FIELDS` in `src/telos/eventkey.py`
is a provisional hand-written map, structured so it can later be generated from the rule set
(a Sigma rule names the fields it matches on in its detection block) **without changing the key
format or invalidating stored runs**.

**Present-but-empty counts as absent.** A stripped field usually remains in the event carrying
an empty value rather than disappearing. Treating that as present would hide the exact loss
being measured. Windows placeholders (`-`, `N/A`, `(null)`, `NULL`) are treated as absent too.
Numeric zero is treated as populated, because LogonType 0 and GrantedAccess 0 are real values.

**Honest limit, and it should be stated in the paper.** The composite key is a **profiling**
improvement, not a statistical one, and it helps the naive baseline equally. In the demo the
baseline also catches the field loss once it is given field-aware keys. The two contributions
are separate and should be claimed separately:

| Contribution | What it improves |
|---|---|
| Composite key | What can be **seen** at all |
| Variance model, gate, correction | What can be **trusted** once seen |

An engineer comparing raw event counts by hand would not have field-aware keys, so the baseline
as implemented is stronger than real hand comparison. That is deliberate: a baseline that has
been quietly handicapped proves nothing.

**Cost if wrong:** low now, high later. Key format changes are cheap while no real runs exist.
After collection begins they are not.

**Verification:** 49 tests pass, up from 20. `test_field_loss_is_invisible_to_event_type_keying`
demonstrates the failure this decision prevents and must not be deleted; if it goes, the reason
for the composite key goes with it.

## 2026-09-03 - The run protocol exports archives by date and never truncates (closes OPEN-QUESTIONS 14)

**Decision:** blueprint run-protocol step 10 and runbook Phase 6 step 10 no longer truncate
`archives.json`. The harness exports the **dated** archive for the run's date and verifies the
copy. `lab/scripts/telos-archive` was rewritten: `truncate` and `rotate` are **removed entirely**.

**Why the old step was wrong.** It said "rotate `archives.json`, gzip, pull, then truncate on the
SIEM", written before anyone looked at how Wazuh stores archives. Observed 2026-09-03 when the
date rolled over mid-session:

```
-rw-r----- 2 wazuh wazuh 5272919 Sep  3 08:19 archives.json
          ^ link count 2
```

`archives.json` is a **hard link** to the current day's file under
`YYYY/Mon/ossec-archive-DD.json`. One file, two names. So:

1. **A run crossing midnight splits across two files.** 101 runs of 25 to 60 minutes will run
   overnight. Reading `archives.json` would export half a run and report success.
2. **Truncating `archives.json` empties the dated archive too.** That step did not clear a scratch
   file, it destroyed the day's permanent record. Safe only if the export had already succeeded
   and been verified, which nothing checked.

**The second benefit, and it is the one that helps at the defense.** With truncation gone,
`telos-archive` has **no destructive subcommand at all**. The single sudoers rule now grants the
harness account **read and export only**, so it cannot alter or delete the evidence store.
"How do you know your archives were not modified?" has a checkable answer instead of an assurance.

**Cost if wrong:** disk management now rests entirely on Wazuh's own rotation plus a retention
policy that is still deferred (OPEN-QUESTIONS 3). The harness must check free space before every
run with `telos-archive disk` and abort cleanly when low. That guard existed in the risk table
already; it is now load-bearing rather than a nicety.

**To reverse:** restore the previous script from git history and re-install it. The sudoers rule
does not change, only the file it points at.

## 2026-09-03 - VMware Tools clock synchronisation fully disabled on both VMs, and the analysis will use the endpoint clock only (closes OPEN-QUESTIONS 6)

**Decision one:** all six `time.synchronize.*` switches set to `FALSE` in **both** `.vmx` files,
alongside the `tools.syncTime` that was already there.

```
tools.syncTime                  = "FALSE"
time.synchronize.continue       = "FALSE"
time.synchronize.restore        = "FALSE"
time.synchronize.resume.disk    = "FALSE"
time.synchronize.resume.host    = "FALSE"
time.synchronize.shrink         = "FALSE"
time.synchronize.tools.startup  = "FALSE"
```

**Why:** `tools.syncTime` alone stops only the **periodic** sync. The other six cover snapshot
revert, resume, and Tools startup. Phase 6 reverts a snapshot before **every one of 101 runs**, so
a clock step there would land at the start of every capture window, in every run, on both sides
of the pre-change and post-change comparison.

**Verified through a full power cycle**, because VMware rewrites the `.vmx` on every power off and
could have stripped them. All seven lines were still present afterwards. Backups kept as
`<name>.vmx.telos-20260903T081807Z.bak`.

**Decision two, and it is the more important half:** the analysis uses the **endpoint's own
clock** and never the manager's.

Every archive line carries both:

```
endpoint clock : "systemTime":"2026-09-02T13:30:38.7096614Z"
manager clock  : "timestamp":"2026-09-02T13:30:40.599+0000"
```

**Rule for the Phase 6 harness:** every capture-window boundary and every measurement uses the
endpoint's `systemTime` or `utcTime` from inside the event. The manager's `timestamp` is used for
nothing except measuring pipeline latency, and that number is only meaningful while the two clocks
are known to agree. Under this rule SIEM-01's clock drift after isolation cannot reach the
results, because it never enters them.

This is runbook rule 5 applied properly: fence in the telemetry, not on a host clock.

**What this rejects, deliberately:** running a time source on the Windows host at `10.20.10.1`,
which was option 2 in OPEN-QUESTIONS 6. It would place a live network service on a segment the
thesis describes as isolated, in order to solve a problem the rule above removes.

**Cost if wrong:** if some later analysis genuinely needs manager-side timing, the timestamps
cannot be repaired after the fact. The mitigation is that the endpoint timestamp is present in
every event, so nothing is lost by preferring it.

**To reverse:** delete the six lines from both `.vmx` files with the VMs powered off, or restore
the `.bak` files.

**Left for Phase 5, and currently only an implication:** a **cold** snapshot boots the guest fresh
and VMware sets the virtual clock from the host, so no sync is needed. A **live** snapshot restores
a stale clock. The blueprint's run protocol implies cold but never says so. **The golden snapshot
must be taken cold**, and Phase 5 has to state that.

## 2026-09-03 - Second checkpoint snapshot on both VMs

**Decision:** `agent-hardened-2026-09-03` on WIN-EP-01 and `timesync-off-2026-09-03` on SIEM-01,
both taken cold.

**Why:** the existing `phase3-complete-2026-09-02` checkpoint predates the item 12 fix. Reverting
to it today would have silently re-enabled active response. The new checkpoint captures items 6, 8
and 12 together, so a revert cannot lose them.

Two flat snapshots per VM, not a branching chain, so the warning in `lab/blueprint.md` section 5
about 16 branching delta chains does not apply. F: has 607.4 GB free.

**To reverse:** `vmrun -T ws deleteSnapshot <vmx> <name>`

## 2026-09-03 - Active response disabled on WIN-EP-01 (closes OPEN-QUESTIONS 12)

**Decision:** `<active-response><disabled>yes</disabled>` in the agent's `ossec.conf`, with a
comment in the file explaining why. Confirmed by the agent itself after restart:

```
2026/09/03 08:04:36 wazuh-agent: INFO: (1350): Active response disabled.
```

**Why:** active response lets the **manager execute commands on the endpoint**. The measuring
instrument must not be able to change the machine under test, and least of all inside a capture
window. Nothing had fired, but a real Atomic Red Team run is exactly when the manager is most
likely to see something it reacts to. Unlike the scan modules in item 8, this one changes state
rather than adding events, so its failure mode is worse and harder to detect after the fact.

`active-responses.log` is still collected as a `<localfile>`. It will simply stay empty, which is
itself evidence that nothing fired.

**Cost if wrong:** the deployment is one more step away from a default Wazuh install, and Chapter
3 must say so. The answer to a panelist is one sentence: active response was disabled because it
allows the monitoring platform to modify the endpoint under measurement, which would introduce
state changes the experiment does not control or record.

**To reverse:** one word in the file, or restore
`C:\Program Files (x86)\ossec-agent\ossec.conf.telos-pre-item12` and restart `WazuhSvc`.

## 2026-09-02 - WIN-EP-01 installer media disconnected, and a checkpoint snapshot taken on both VMs

**Decision one:** `sata0:1.startConnected = "FALSE"` in `WIN-EP-01.vmx`, matching what Phase 2 did
for SIEM-01. The CD-ROM device stays present and still points at the ISO, but it no longer
connects at power-on.

**Why:** with it connected, the endpoint **depended on E: at every boot**, and E: is the hard disk
that the runbook's first rule says no VM may depend on. Move or rename that ISO and WIN-EP-01
fails to start. It also left an installer disc inside what becomes the golden image.

**When it has to be done:** with the VM powered off. VMware rewrites the `.vmx` on power off and
would discard an edit made while it was running.

**To reverse:** set it back to `"TRUE"` with the VM powered off.

**Decision two:** a checkpoint snapshot named `phase3-complete-2026-09-02` on both VMs.

**Why:** neither machine had any restore point, and a host power loss already happened on the same
day. Two days of build work had no protection at all. F: had 587.6 GB free before, 611.6 GB after
the guests released their memory files, so cost is not a factor.

**This is not the Phase 5 golden snapshot.** That one is taken later, with NAT disconnected, and
it is the base of the `cfg-suppressed` and `cfg-natural` branches in `lab/blueprint.md` section 5.
This is a single flat checkpoint, and the blueprint's warning about branching delta chains does
not apply to it.

**Cost if wrong:** a snapshot delta grows as the VM changes. If F: gets tight before Phase 5,
delete it.

**To reverse:** `vmrun -T ws deleteSnapshot <vmx> phase3-complete-2026-09-02`

## 2026-09-02 - Four Wazuh agent scan modules disabled on WIN-EP-01 (closes most of OPEN-QUESTIONS 8)

**Decision:** disabled `rootcheck`, `sca`, `syscheck` (file integrity monitoring) and
`syscollector` in the agent's `ossec.conf`. Each change carries a comment in the file saying why.
The agent is now a log forwarder and nothing else.

**Verified from what the agent reports about itself after restart, not from the file:**

```
2026/09/02 13:56:21  (6001): File integrity monitoring disabled.
2026/09/02 13:56:21  rootcheck: Rootcheck disabled.
2026/09/02 13:56:21  syscollector: Module disabled. Exiting...
2026/09/02 13:56:21  sca: Module disabled. Exiting.
```

The measurement path is untouched. `Application`, `Security`, `System`,
`Microsoft-Windows-Sysmon/Operational` and `active-responses.log` are all still analyzed, and the
agent reports `Connected to the server` with `status='connected'`.

**Why. There are two separate reasons and the second is the serious one.**

*Noise.* All four have `scan_on_start` behaviour, and every Phase 6 run begins with a snapshot
revert and a boot, so all four would run at the start of **every one of 101 runs**. FIM also
synchronises every 5 minutes and watches some paths in real time. With `logall_json` on, every
event they produce lands in `archives.json`. That is the measuring instrument's own output
entering the measurement, and it lands in the coefficient of variation that T1's whole
statistical argument rests on.

*Confounding, which is worse.* Two of the four **react to the change being measured**:

- `sca` evaluates a **CIS Windows 11 policy**. Apply a hardening control and its results change.
- `syscheck` monitors the **registry**. It would observe the hardening script making its edit.

Both would emit events that appear only in post-change runs. A differential analysis comparing
pre-change and post-change event profiles would see a systematic difference caused by the
instrument watching the change happen. That is not background noise, and it would have looked
like a finding.

**Cost if wrong:** the deployment is a reduced Wazuh agent and Chapter 3 must say so. The answer
to a panelist is one sentence: the agent's own assessment and inventory modules were disabled
because they generate events on timers unrelated to the experiment, and two of them respond
directly to the hardening changes under test, which would confound the comparison. Their data
cannot show telemetry loss, so nothing measurable is given up.

**Not fixed, and stated as such:** the agent-upgrade module still starts
(`wazuh-modulesd:agent-upgrade: INFO: (8153): Module Agent Upgrade started.`). There is no
agent-side switch. The only control is on the manager: never issue an upgrade command.
OPEN-QUESTIONS 8 stays open with that reduced scope.

**Deliberately not changed, because they are separate decisions:** `active-response` is still
enabled, which lets the manager run commands on the endpoint (OPEN-QUESTIONS 12), and
`client_buffer` still throttles at 500 events per second with a 5000-event queue, which is a
third silent loss channel alongside the Sysmon channel and journald (OPEN-QUESTIONS 13).

**To reverse:** the previous config is in the guest at
`C:\Program Files (x86)\ossec-agent\ossec.conf.telos-pre-item8`. Copy it back and restart
`WazuhSvc`. Every change is a single word.

## 2026-09-02 - WIN-EP-01 runs Windows 11 **Education, unactivated**, not the Enterprise Evaluation ISO

**Decision:** Installed Windows 11 Education from the retail multi-edition ISO
`Win11_24H2_English_x64.iso`, choosing "I don't have a product key" and selecting Education from
the edition list (index 4, verified by reading the XML block inside `install.wim` before
installing). The machine is left **unactivated**. This supersedes the 2026-08-20 choice of
`Windows 11 Enterprise Eval 26200.6584 25H2`.

**Why:** The runbook offered "Windows 11 Enterprise Eval (or Server 2022 Eval)" and never picked
one. Windows 11 Enterprise Evaluation runs for **90 days**. Installed 2026-09-02, it stops around
**2026-12-01** and then shuts down once per hour. Reverting a snapshot does not fix that, because
the grace period is computed from the install date stored inside the restored image against the
real clock. Every capture run after that date would be broken, and the December defense sits
right on the boundary.

Education carries the same security feature set as Enterprise, including Credential Guard and
AppLocker `(unverified against Microsoft's edition matrix, taken from the edition requirements
pages)`, so the hardening catalogue is unaffected. The CIS Microsoft Windows 11 Enterprise
Benchmark and the Microsoft Windows 11 STIG still apply, which keeps OPEN-QUESTIONS 4 answerable.
Unactivated Windows has **no expiry timer at all**. Verified on the built machine:

```
Name          : Windows(R), Education edition
LicenseStatus : 5   (Notification)
GracePeriodRemaining : 0
```

`Notification` is the nag state. It does not shut the machine down.

**Cost if wrong:** a desktop watermark, personalization settings locked, and the Software
Protection service retrying activation on its own schedule and failing. That retry is a
background event source and must be named in the baseline description. Rebuilding to a different
edition later would mean a new golden snapshot and discarding every run before it.

**To reverse:** reinstall. There is no in-place path from Education to another edition without a
key.

## 2026-09-02 - WIN-EP-01 uses UEFI with Secure Boot and **no virtual TPM**

**Decision:** `firmware = "efi"` and `uefi.secureBoot.enabled = "TRUE"` in the `.vmx`, with no
TPM device. Windows 11 setup was passed with four `LabConfig` registry values set from the
Shift+F10 command prompt at the first setup screen:

```
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassTPMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassSecureBootCheck /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassRAMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassCPUCheck        /t REG_DWORD /d 1 /f
```

**These are required.** Setup showed `This PC doesn't currently meet Windows 11 system
requirements` and only proceeded after they were set. Anyone rebuilding from this runbook must
do this step.

**Why no TPM:** VMware Workstation 17 requires the virtual machine to be encrypted before it will
attach a TPM. An encrypted VM asks for a password at power-on. The Phase 6 harness must run 101
cycles unattended, so that password would have to live in the harness configuration, putting a
secret into a project whose repository is public. Secure Boot without a TPM still permits VBS,
so hardening change #8 (Credential Guard) remains possible. TPM 2.0 is recommended but not
required for VBS `(unverified against current Microsoft documentation)`.

**Verified on the built machine:** `TpmPresent : False`, `SecureBootOn : True`.

**Cost if wrong:** no BitLocker, and a panelist may ask whether an endpoint without a TPM is
representative. The answer is that no control in the 16-change catalogue depends on a TPM.

**To reverse:** add a TPM in VMware, accept the encryption prompt, and give the harness the
password. The guest keeps working.

## 2026-09-02 - `vhv.enable = "FALSE"` so that Windows cannot switch VBS on by itself

**Decision:** nested virtualization is explicitly disabled in `WIN-EP-01.vmx`.

**Why:** Windows 11 enables Virtualization-Based Security by default on capable hardware. If VBS
were already running in the golden image, hardening change #8 (Enable Credential Guard) would
have nothing left to switch on and would measure nothing. Without virtualization extensions in
the guest, VBS cannot start, so the change stays a real, measurable change.

**Verified twice, from two independent sources.** `Win32_DeviceGuard` reports
`VirtualizationBasedSecurityStatus : 0` and `SecurityServicesRunning : 0`, and `systeminfo`
during the Phase 3 atomic test reported `Virtualization-based security: Status: Not enabled`.

**Cost if wrong:** none while it stays off. It must be switched **on** deliberately, and the
golden snapshot re-examined, when change #8 is tested. This is tied to OPEN-QUESTIONS 2, which is
still untested.

**To reverse:** set `vhv.enable = "TRUE"` with the VM powered off. Then check whether Windows
turns VBS on by itself, because that would silently invalidate change #8.

## 2026-09-02 - WIN-EP-01 time zone set to UTC to match SIEM-01

**Decision:** `Set-TimeZone -Id 'UTC'`. Windows setup had left it at `Singapore Standard Time`
(UTC+8).

**Why:** SIEM-01 runs `Etc/UTC`. Two machines in two time zones turns every cross-host comparison
into a manual conversion, and OPEN-QUESTIONS 6 already concerns cross-host time. Windows stores
event times in UTC internally, so this changes how times are displayed, not what is recorded.

**Cost if wrong:** none to the data. The desktop clock inside the VM shows UTC, which is mildly
confusing when working in the guest by hand.

**To reverse:** `Set-TimeZone -Id 'Singapore Standard Time'`.

## 2026-09-02 - Sysmon baseline config is SwiftOnSecurity at a pinned commit

**Decision:** `SwiftOnSecurity/sysmon-config`, file `sysmonconfig-export.xml`, pinned at commit
`1836897f12fbd6a0a473665ef6abc34a6b497e31`, committed to the repo as
`lab/configs/sysmonconfig.xml`.

**Why:** the alternative considered was `olafhartong/sysmon-modular`, which has a wider event
surface and MITRE ATT&CK mapping. It was rejected for two reasons. First, archive growth under
load is still unmeasured (OPEN-QUESTIONS 3), and a much more verbose sensor makes an unmeasured
disk risk worse. Second, catalogue item 15 is "narrow the Sysmon config" treated as a hardening
change in its own right. That item only means something if the baseline is not already the
narrowest available option.

**Two limits that must be stated in Chapter 3, both discovered at install time:**

1. `Sysmon64.exe -c` reports `Image loading : disabled`. **Sysmon Event ID 7 never appears.** Any
   hardening change whose effect would show up as a DLL load is invisible to the method.
2. The config file's own header reads `Source version: 74 | Date: 2021-07-08`, and Sysmon loaded
   it as schema `4.50` into a `4.91` binary. It contains no rules for the event types Sysmon
   added later: 25 (ProcessTampering), 26 (FileDeleteDetected), 27, 28 and 29.

**Cost if wrong:** a config change later invalidates every earlier run under runbook rule 2.

**To reverse:** `Sysmon64.exe -c <newconfig.xml>`, then re-record the hash here and discard all
prior runs.

## 2026-09-02 - Atomic Red Team is pinned by **commit and file count**, not by archive hash

**Decision:** the pin is `cb486d9a888e921fac5902a06c7b46e420bb14a7` plus the count of 1310 files
in the `atomics` folder. The transfer archive `atomics.zip` is **not** a valid pin.

**Why:** the archives were built by a custom lock-tolerant archiver that does not preserve file
timestamps, so the SHA256 of the zip changes on every repack. This was observed directly: the
same 74-file module produced two different archive hashes on two consecutive packs. Anyone who
recorded the archive hash as a pinned value would be recording a number that cannot be
reproduced.

**Cost if wrong:** nothing, provided the distinction is written down. It is written down here and
in `C:\AtomicRedTeam\TELOS-PROVENANCE.txt` inside the guest.

## 2026-09-02 - Antivirus exclusions on the host and in the guest, for the Atomic Red Team folder only

**Decision:** two exclusions.

1. **Host:** `E:\TeLoS-artifacts` added to Kaspersky 21.26's exclusion list, by hand.
2. **Guest:** `Add-MpPreference -ExclusionPath "C:\AtomicRedTeam"` on WIN-EP-01.

**Why the host exclusion:** Kaspersky was blocking read access to **66** Atomic Red Team files.
Verified by counting them, not estimated. The list included three technique definitions
(`T1218.005.yaml`, `T1548.002.yaml`, `T1685.yaml`), `Indexes/windows-index.yaml`, and most of the
Windows payload binaries for T1055 process injection, T1218 proxy execution and T1134.001 token
manipulation. Without the exclusion the pinned commit `cb486d9a` would describe a set of files
that is not what is on the endpoint, and the reproducibility claim in the proposal would be
false. After the exclusion: **1310 files packed, 0 blocked.**

Note that Windows Defender is **not running on the host**. `Get-MpPreference` fails with
`0x800106ba` and `WinDefend` is `Stopped`, because Kaspersky has taken over.

**Why the guest exclusion, and why it is narrow:** without it, Defender quarantines the same class
of files **once, at extraction time**, before the golden snapshot exists. Quarantined files are
then permanently absent from the image. That would not be studying an endpoint where antivirus
blocks attacks. It would be studying an endpoint where an unrecorded subset of test files simply
does not exist, chosen by whichever signature version was current on the build day. The exclusion
covers only `C:\AtomicRedTeam` and is identical in Config S and Config N, so it cancels out
between them. Atomic Red Team is the stimulus generator, part of the instrument, not the machine
under test.

**Verified:** the exclusion was accepted **despite Tamper Protection being on**
(`RESULT: ACCEPTED`, `TamperProtection : True`), and after extraction
`Defender detections during extraction: 0` with all 1310 files present.

**Cost if wrong:** a stated deviation from a default endpoint that must appear in Chapter 3. A
panelist can reasonably say the baseline is less realistic. The answer is that the alternative is
an unrecorded and unreproducible difference baked into the golden snapshot, which runbook rule 2
exists to prevent.

**To reverse:** `Remove-MpPreference -ExclusionPath "C:\AtomicRedTeam"` in the guest, and delete
the entry from Kaspersky's exclusion list on the host. Remove the host exclusion when the thesis
is finished.

## 2026-09-02 - Unattended access to SIEM-01: one SSH key and one narrow sudo rule

**Decision:** two changes on SIEM-01.

1. An `ed25519` key pair at `C:\Users\Elijah\.telos\siem01_ed25519`, **no passphrase**, public
   half in `/home/eli/.ssh/authorized_keys`.
2. A root-owned helper script `/usr/local/sbin/telos-archive` with a fixed list of subcommands,
   and exactly one sudoers line in `/etc/sudoers.d/telos-archive`:
   ```
   eli ALL=(root) NOPASSWD: /usr/local/sbin/telos-archive
   ```

**Why:** blueprint run protocol step 10 is "over SSH to SIEM-01: rotate `archives.json`, gzip,
pull to `E:\runs\`, then truncate on the SIEM", and the harness must complete 101 cycles with
nobody watching. `/var/ossec` is mode 750 owned by `root:wazuh` and `eli` is not in the `wazuh`
group, so root is required.

**Why a script rather than adding `eli` to the `wazuh` group.** Group membership was the one
command answer, but it grants the interactive login account read **and write** access to
everything Wazuh holds, including `client.keys` and the archive files that are the evidence base
of the thesis. A panelist can reasonably ask how you know the archives were not altered. "The
harness account could not write to them" is an answer. "It could, but I did not" is not.

**The script also enforces a measurement rule.** Its `count` and `show` subcommands take a
**file** holding the search pattern, never the pattern on the command line, because `sudo` writes
every command line to journald and Wazuh collects journald. That is OPEN-QUESTIONS 1b, found on
this machine in Phase 2. The design makes the mistake impossible rather than relying on
discipline.

**Cost if wrong:** a passphrase-less private key on the host can reach SIEM-01. In a disconnected
lab with one user the practical risk is small, but it is a real credential and it must never be
committed. It lives in `C:\Users\Elijah\.telos\`, outside the repository.

**To reverse:** `sudo rm /etc/sudoers.d/telos-archive /usr/local/sbin/telos-archive` and delete
the `telos-harness` line from `~/.ssh/authorized_keys`.

## 2026-09-02 - WIN-EP-01 was built from a hand-written `.vmx`, not the Workstation wizard

**Decision:** the disk was created with `vmware-vdiskmanager.exe -c -s 80GB -a lsilogic -t 0` and
the `.vmx` was written by hand.

**Why:** the New Virtual Machine wizard forces a virtual TPM and VM encryption for a Windows 11
guest, which is exactly what the decision above rejects. A hand-written config also means the
machine's definition can be read, reviewed and committed rather than clicked.

**Deviations from SIEM-01's configuration, each deliberate:**

| Setting | SIEM-01 | WIN-EP-01 | Reason |
|---|---|---|---|
| Firmware | BIOS | `efi` + Secure Boot | Windows 11 needs UEFI; Secure Boot keeps VBS possible |
| Disk controller | LSI SCSI | NVMe | Windows 11 has no in-box LSI SAS driver, setup would not see the disk |
| Network card | `e1000` | `e1000e` | `e1000` driver is not in-box on Windows 11 24H2 `(unverified)`; `e1000e` is |
| Sound card | present | absent | one less device and driver emitting background events |
| 3D graphics | on | off | removes GPU driver activity from the guest |
| CPU and RAM hot-add | on | off | the device set must not change during a measurement run |

**Cost if wrong:** a malformed `.vmx` would refuse to power on, which is loud and immediate, not
silent. It powered on first time.

## 2026-09-02 - Wazuh vulnerability detection disabled on SIEM-01

**Decision:** Set `<enabled>no</enabled>` inside the `<vulnerability-detection>` block of
`/var/ossec/etc/ossec.conf`. Backup kept at `ossec.conf.pre-vd.bak`. Confirmed by Wazuh itself:
`wazuh-modulesd:vulnerability-scanner: INFO: Vulnerability scanner module is disabled.`

**Why:** The module was configured with `<feed-update-interval>60m</feed-update-interval>` and
`ossec.log` showed it acting on that timer (UTC):

```
20:02:49  Initiating update feed process.
20:31:46  Initiating update feed process.
20:51:53  Triggered a re-scan after content update.
20:51:53  Feed update process completed.
```

The 20:31 update ran for about 20 minutes and then triggered a full re-scan. Four reasons to
turn it off:

1. It cannot contribute to the measurement. It compares installed package versions against a
   CVE list. It does not observe system events, so it can neither produce nor lose the event
   types T1 counts.
2. Phase 5 removes its internet access. An internet-dependent module on a deliberately isolated
   machine will log repeated failures on a timer, forever.
3. An hourly download plus a 20 minute re-scan is uncontrolled change inside a capture window.
   Fencing capture windows in telemetry does not help when the noise arrives inside the window.
4. It had consumed 12 GB in `/var/ossec/queue/vd`.

**Cost if wrong:** SIEM-01 is a reduced Wazuh deployment, and the methodology must say so. The
answer to a panelist is one sentence: vulnerability detection was disabled because it depends on
external content updates incompatible with an isolated measurement environment, and it observes
package inventory rather than events.

**To reverse:** `sudo cp -a /var/ossec/etc/ossec.conf.pre-vd.bak /var/ossec/etc/ossec.conf`
then restart `wazuh-manager`. Needs internet to rebuild the feed, so it must be done before
Phase 5 isolation, not after.

**The 12 GB at `/var/ossec/queue/vd` was left in place on purpose.** With 159 GB free it is not
urgent, and once the machine is isolated that data cannot be downloaded again.

## 2026-09-02 - Automatic package updates disabled, and the 49 pending updates applied once

**Decision:** Disabled `apt-daily.timer` and `apt-daily-upgrade.timer`, set both
`APT::Periodic` values in `/etc/apt/apt.conf.d/20auto-upgrades` to `"0"`, then ran
`apt upgrade -y` once and applied all 49 pending updates. Verified afterwards:
`apt list --upgradable` returns only `Listing... Done`, nothing kept back, and no reboot was
required. `systemctl is-enabled` reports both timers `disabled`, `is-active` reports both
`inactive`.

**Why:** Ubuntu 24.04 patches itself on a schedule by default. Both timers were armed. Doing
nothing does not freeze the machine, it just means the change happens at a time nobody chose,
possibly mid-run. The choice was never "change it or leave it alone", it was "change it now on
purpose and write it down" or "let it change itself later".

Applying the updates rather than freezing an unpatched machine, because:
1. Exact reproduction from the ISO is not achievable anyway. The Wazuh install itself pulls from
   the internet. The real reproducibility artifact is the Phase 5 golden snapshot.
2. The hardening catalogue is CIS-based, and CIS baselines assume a patched system. Measuring
   telemetry loss on a knowingly unpatched host invites an obvious panel question.

The kernel was **not** among the updates. It stays `6.8.0-138-generic`. The 49 packages included
`apparmor` (writes audit records), `cloud-init` 25.2 to 26.1, `netplan.io`, and `open-vm-tools`
12.5 to 13.0. All four were checked after the upgrade and a reboot: `ens37` still held
`10.20.10.10/24`, exactly one default route on `ens33`, kernel unchanged, clock on UTC with NTP
active. `systemd`, `openssh-server` and `rsyslog` were **not** in the update list, so the
logging stack did not move.

**Cost if wrong:** SIEM-01 no longer receives security updates automatically, so it must not be
exposed to an untrusted network. Acceptable because it is isolated on vmnet2 from Phase 5. If a
future update is ever needed, it becomes a deliberate, recorded act that invalidates prior runs.

**To reverse:** `sudo systemctl enable --now apt-daily.timer apt-daily-upgrade.timer` and set
both `20auto-upgrades` values back to `"1"`.

**Still open:** `snapd` refreshes its snaps on its own schedule and has **not** been dealt with.
See OPEN-QUESTIONS item 5. Same class of problem, not yet closed.

## 2026-09-02 - Root logical volume extended to the whole volume group (one-way)

**Decision:** Kept the installer's LVM layout rather than reinstalling without it, and ran
`lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv` followed by
`resize2fs /dev/ubuntu-vg/ubuntu-lv`. Root filesystem went from 97 GB to 195 GB, online, with no
reboot. Free space went from 86 GB to 179 GB.

**Why:** The Ubuntu guided install with LVM gave the root logical volume 99 GiB of a 200 GB disk
and left 99 GiB unallocated in the volume group. No error and no warning was shown. It was found
only by reading the SSH login banner. Half the disk was unreachable while `df` reported a
plausible-looking number.

Reinstalling without LVM would have cost 20 minutes for no benefit, because rollback is handled
by VMware snapshots of the whole VM, not by LVM snapshots. Free extents in the volume group
would have bought a second rollback mechanism that this project will not use.

**Cost if wrong:** The extend is effectively **one-way**. Shrinking an ext4 root filesystem
requires booting from other media. If free extents in the volume group are ever needed, the VM
must be rebuilt.

## 2026-09-02 - Wazuh pinned to 4.14.7-1, repo disabled, packages held

**Decision:** Three separate locks on the Wazuh version.

1. Downloaded the installer from `https://packages.wazuh.com/**4.14**/wazuh-install.sh`, not the
   runbook's `4.x`. Recorded its SHA256 before running it.
2. Commented out the repository the installer added, per runbook step 6. Verified: `apt update`
   no longer contacts `packages.wazuh.com`.
3. Ran `apt-mark hold wazuh-manager wazuh-indexer wazuh-dashboard` as a second, independent lock.

**Why:** `4.x` is a moving pointer that returns whatever is newest on the day it runs, which
contradicts the project's own rule to pin every version. Worth noting that the installer, having
been fetched from the pinned `4.14` path, then configured the machine to track `4.x`:

```
deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main
```

So pinning the download alone would not have pinned the machine. The repo had to be disabled too.
The `apt-mark hold` is the third lock because a repository can be re-added by a reinstall, by a
later runbook step, or by hand, and a hold still blocks the upgrade if it is.

**On `WAZUH_REVISION="rc1"`:** `wazuh-control info` reports that string. Why it reads `rc1` is
**not known**. The authoritative record is the apt package version `4.14.7-1` from a repository
component literally named `stable`, which is what all three packages report. Do not cite `rc1`
as a version.

**Cost if wrong:** Low. Unlocking is `apt-mark unhold` plus uncommenting one line. The cost of
not doing it is high and silent: a version bump partway through discards every earlier run.

## 2026-09-02 - Retention decision deferred until a measured event rate exists (deviates from runbook step 8)

**Decision:** Runbook Phase 2 step 8 says to shorten retention. That half of the step was
**deliberately not done**. The replica half was verified as already satisfied and needed no
change.

**Why:** The runbook itself admits the 16 GB and 200 GB figures were unmeasured headroom. Now
there are measurements:

| Item | Measured 2026-09-02 |
|---|---|
| Archive growth, idle, no agents | about 9.7 MB per day |
| Archives on disk | 88 KB |
| Indexer data on disk | 3.4 MB |
| Free space | 159 GB |

At the idle rate, archives take decades to matter. The real risk is a burst during a Phase 6 run,
and that rate cannot be known until a run has happened. Setting a retention number now would
replace one guess with another.

**Instead:** record the measured baseline (done, in WORKLOG), add a free-space check to the
Phase 6 harness so a run aborts rather than filling the disk (already required by runbook Phase
6), and set retention after the first real run.

**Cost if wrong:** If Phase 6 generates events far faster than expected, the disk could fill
before retention exists. The harness free-space check is what prevents that from corrupting a
run, so **that check is now load-carrying and must actually be implemented.**

## 2026-09-02 - Smaller Phase 2 build choices

Four small decisions, grouped because none of them warrants its own entry.

**1. Declined the Ubuntu installer self-update.** The installer offered to update itself from
24.04.4 to 24.04.4.1. Chose "Continue without updating". The installer is fetched live, so its
version would depend on the day the build ran. The installed OS is 24.04.4 LTS either way.
*Cost if wrong:* if a bug in the shipped installer had broken the install, redo it and accept
the update. Cheap, because no data existed at that point.

**2. Hostname is lowercase `siem-01`, not `SIEM-01`.** The Ubuntu installer lowercased it.
Left as is, because lowercase is the Linux convention and hostname lookups are case-insensitive.
The VMware display name stays `SIEM-01`. Wazuh event fields will show `siem-01`. Both refer to
the same machine.

**3. Netplan file uses `dhcp4: false` instead of the runbook's `routes: []`.** The goal of
`routes: []` was to stop the lab interface adding a default gateway. With `dhcp4: false` and no
gateway specified, netplan adds only the local `10.20.10.0/24` route, which is the same result,
without relying on an empty-list construct that was not verified for this netplan version.
Confirmed with `ip route`: exactly one `default` line, on `ens33`.

**4. The lab interface is `ens37`, not `ens34`.** The runbook guessed `ens34`. The real name
comes from the PCI slot: `ethernet0.pciSlotNumber = "33"` gives `ens33` and
`ethernet1.pciSlotNumber = "37"` gives `ens37`. The runbook was right to say "find it with
`ip link show`" rather than trusting the guess.

## 2026-08-19 - Windows hypervisor turned off (host runs VMware natively)

**Decision:** Disabled the Windows hypervisor with `bcdedit /set hypervisorlaunchtype off`,
then rebooted. Verified: HypervisorPresent went True to False, VBS status went 2 to 0, vmrun
still works.

**Why:** Phase 0 found a Windows hypervisor running. The cause was the Hyper-V feature, not any
security feature (Memory Integrity off, Credential Guard off, EnableVirtualizationBasedSecurity=0,
no Docker, no WSL2). Two reasons to turn it off:
  1. VMware now runs directly on the hardware. Sharing the machine with the Windows hypervisor
     can add timing changes, and T1 measures timing variance. This removes that variance source.
  2. Hardening change #8 (Credential Guard) needs nested virtualization inside the guest. VMware
     exposes that more reliably when the host hypervisor is off.

**Cost if wrong / how to reverse:** `bcdedit /set hypervisorlaunchtype auto` then reboot. This
also disables Docker Desktop, WSL2, and host Credential Guard while off, but none of those are
in use here.

**Must stay off for the whole experiment.** Changing this mid-experiment changes timing and
invalidates prior runs. It is now part of the host baseline, same status as a pinned version.

## 2026-08-31 - Project named TeLoS

**Decision:** The system and lab are named **TeLoS**. Chosen from a shortlist that included
`covdrift`, `Scotoma`, and `anino` (Tagalog for shadow).

**Why:** Two readings land on the same word. "TeLoS" reads as **Telemetry Loss**, which is
literally the thing the system detects. It is also the Greek word for purpose or end goal,
which fits a thesis project without being decorative. Checked against PyPI and GitHub search
at decision time; no existing security tool found using this name `(unverified, spot-check
only, not an exhaustive trademark search)`.

**Where it is used:** the homelab folder on F: (`F:\TeLoS Homelab\`, with a space, exact
casing). Runbook paths written before this decision (`F:\Homelab\...`) are corrected to match.
The Python package is still `src/blindspot/`; renaming it to match is a follow-up task, cheap
now, expensive after the harness and web layer exist.

**Cost if wrong:** Low. A folder rename on F: is a `Move-Item`. The package rename is more
work the later it happens, so do it before Phase 3 if the name is final.

## 2026-08-31 - Build the analysis core before the lab, using synthetic data

**Decision:** Write stages 2, 3 and 5 of the pipeline (variance model, differential analysis,
reporting) now, tested against generated counts. Leave stage 1 (acquisition from live VMs) and
stage 4 (impact scoring) until later.

**Why:** The analyser consumes event counts. It does not care whether a real Windows machine or
a script produced them. So nothing about stages 2, 3 and 5 needs a lab, Wazuh, or Atomic Red
Team. Waiting for the lab before writing any code would have cost weeks for no reason.

This also corrects an earlier claim in this log. The broken hardening catalogue
(OPEN-QUESTIONS item 1) was described as blocking everything. It is not. It blocks the
**experiment design**, not the analyser.

**Cost if wrong:** Synthetic data proves the code is correct. It proves nothing about real
telemetry. Real event counts are not normally distributed, and the demo generator draws from a
rounded normal. No result from `src/demo.py` may be presented as a finding. The moment real
captures exist, the same tests must be re-run against them.

**Immediate benefit:** the test suite found a genuine crash before any real data existed. See
the WORKLOG entry for the same date.

## 2026-08-19 - T3 loses its fallback status (SigmaHQ has only 6 STP-annotated rules)

> **The open choice at the end of this entry was settled on 2026-09-26: neither path.** T1 is final
> and there is no fallback topic. See the 2026-09-26 entry at the top of this file.

**Finding:** `SigmaHQ/sigma` at commit `da9bb07` carries STP robustness tags on only **6 of
3,783 rules (0.16%)**. See the full evidence in OPEN-QUESTIONS.md, Answered section.

**Decision:** T3 can no longer be treated as the safe fallback to T1. Its Objective 5 (validate
automated scores against the manually annotated subset with Cohen's kappa) cannot be executed on
6 rules across 4 levels.

**Why this matters now:** The plan assumed T1 primary, T3 fallback. As of this finding there is
**no verified fallback.** If T1 fails its spike gate, the options are:
  1. Redesign T3's validation: annotate a subset yourself with a second annotator and report
     inter-rater agreement. This turns T3 into a partly manual study and weakens its main
     selling point (that it validates against someone else's labels).
  2. Switch the fallback to **T2** (severity inversion), which needs no external annotation
     corpus. Its weakness is self-created ground truth, which is a smaller problem than having
     no ground truth at all.

**Cost if wrong:** Low to act on now, high to ignore. Knowing this in August means the fallback
can be rebuilt calmly. Discovering it in October, after a failed T1 spike, means no time to
recover.

**Not yet decided:** which of the two paths above. This is a strategic call to make alongside
the T1 spike result, not before it. T1 is still the primary and still the goal.

## 2026-08-19 - Repo can be public now (supersedes the private decision below)

**Decision:** The repo can be public from the start. No need to wait for the defense.

**Why:** The professor confirmed two things. There are no intellectual property rules that
stop a student publishing thesis work early. And there is no similarity-check problem: a
match between the final paper and my own public repo is not treated as an issue.

This removes both reasons the earlier entry gave for staying private.

**Still true, separate point:** the repo has no code yet. It is not a strong portfolio piece
until the harness exists. Being public early does not harm this, because the value of a public
repo is the commit history built over time. Publishing now starts that history and also backs
up the work off the single local disk.

**Cost if wrong:** Low. A public repo can be made private again at any time.

## 2026-08-19 - Repo stays private until the defense (SUPERSEDED, see entry above)

**Decision:** GitHub repo is private now. Flip to public on defense day.
**Why:** Three unsubmitted thesis proposals in a public repo is an academic integrity and
scooping risk. The commit history still proves months of work when it goes public, which is
the part that has portfolio value.
**Cost if wrong:** Delayed portfolio visibility by a few months. Low.

## 2026-08-19 - Raw run data never enters git

**Decision:** `data/runs/` is gitignored. Only small derived files in `data/summaries/`
are committed.
**Why:** GitHub rejects files over 100 MB and warns past 1 GB per repo. 101 gzipped archive
exports will not fit. Git LFS free tier is 1 GB storage and 1 GB bandwidth per month, which
this would blow past and start costing money.
**Cost if wrong:** Raw data exists on one disk only. Mitigate with a separate backup copy
to a second physical drive, not with git.

## 2026-08-19 - Everything lives in E:\Claude general

**Decision:** Repo, code, docs, and archives all in this one folder on E:.
**Why:** One place to look. Nothing to forget. The blueprint originally put code on C: for
speed, but the only hard rule is that **VMs** must never run from E:. Git and Python on a
hard disk are just slower, not wrong.
**Cost if wrong:** Slower git operations and Python imports. Acceptable.

## 2026-08-19 - T1 gets full structure, T2 and T3 get stubs

**Decision:** Build out `thesis/T1/` properly. T2 and T3 keep a folder and a README that
holds the fallback reasoning.
**Why:** Only one topic will be built. Empty scaffolding for two abandoned topics is
maintenance work for nothing. But the fallback trail must stay written down, because T1
can still fail its spike gate.
**Cost if wrong:** If T1 fails and you switch to T3, you build that structure then. Cheap.

---

# Pinned versions (fill these in during Phase 4 of the runbook)

A version bump partway through the experiment means every earlier run must be discarded.
Record these **before** taking the golden snapshot.

## Host and analysis stack (recorded 2026-08-31)

| Item | Value | Date recorded |
|---|---|---|
| Host OS | Windows 11 Pro 10.0.26200 | 2026-08-31 |
| CPU | AMD Ryzen 9 7950X, 16C/32T | 2026-08-20 |
| VMware Workstation | 17.5.1 build-23298084 | 2026-08-20 |
| Windows hypervisor | **OFF** (`hypervisorlaunchtype off`) | 2026-08-20 |
| Python | 3.13.14 (`C:\Program Files\Python313`) | 2026-08-31 |
| numpy | 2.5.2 | 2026-08-31 |
| scipy | 1.18.1 | 2026-08-31 |
| pandas | 3.0.5 | 2026-08-31 |
| PyYAML | 6.0.3 | 2026-08-31 |
| pytest | 9.1.1 | 2026-08-31 |
| Analyser git commit | `78f41f4` (first version of the analysis core) | 2026-08-31 |
| **Host antivirus** | **Kaspersky 21.26** (`AVP21.26` service running). **Windows Defender is OFF on the host** as a result: `WinDefend` is `Stopped` and `Get-MpPreference` fails with `0x800106ba`. Kaspersky blocks Atomic Red Team files, so `E:\TeLoS-artifacts` is on its exclusion list. **Remove that exclusion when the thesis is finished.** | 2026-09-02 |
| Artifact store | `E:\TeLoS-artifacts\` holds every pinned installer, clone and archive. **Not** in the repo. Binaries do not belong in git. | 2026-09-02 |
| Credentials store | `C:\Users\Elijah\.telos\` holds `WIN-EP-01.pw`, `SIEM-01.pw` and the `siem01_ed25519` key pair. Outside the repo on purpose, since the repo is public. **Never commit these.** | 2026-09-02 |
| `git core.autocrlf` | **`true`** on this host. This silently rewrote the pinned Sysmon config on first commit, one byte short of the recorded hash. `.gitattributes` now pins `lab/configs/sysmonconfig.xml` as binary and keeps `lab/scripts/telos-archive` and `*.sh` at LF. | 2026-09-02 |

`scipy` supplies Benjamini-Hochberg through `scipy.stats.false_discovery_control`, so
`statsmodels` is not a dependency. `scikit-learn` was in the original plan for Cohen's kappa,
which belonged to T3 and is no longer in scope.

## Lab stack (fill in during Runbook Phase 4)

| Item | Value | Date recorded |
|---|---|---|
| **Wazuh version** | **`4.14.7-1`** for `wazuh-manager`, `wazuh-indexer` and `wazuh-dashboard`, from `packages.wazuh.com/4.x/apt stable main`. Repo now disabled and all three packages held. | 2026-09-02 |
| Wazuh installer script | `wazuh-install.sh` from `https://packages.wazuh.com/4.14/wazuh-install.sh`, 204 KB, SHA256 `8ebe9514688ace8af9445805e8887cd491dd9f95fa9d421a70f0ea012ab06f3a` | 2026-09-02 |
| Wazuh deployment mode | all-in-one (`-a`). Certificates issued for `127.0.0.1`, so the Phase 5 NAT disconnect cannot break component communication. | 2026-09-02 |
| SIEM-01 OS | Ubuntu 24.04.4 LTS (Noble Numbat), hostname `siem-01` | 2026-09-02 |
| SIEM-01 kernel | `6.8.0-138-generic` | 2026-09-02 |
| SIEM-01 patch level | all 49 pending updates applied once, then automatic updates disabled. No kernel update was included. `apt list --upgradable` returns empty. | 2026-09-02 |
| SIEM-01 lab address | `10.20.10.10/24` on `ens37` (VMnet2), MAC `00:0c:29:8c:83:33` | 2026-09-02 |
| **Sysmon binary version** | **`15.21`**, `Sysmon64.exe` SHA256 `A60AA845457406383277AFDEAD35BD90C7804572B99901D239CC974841DF2528`, from `https://download.sysinternals.com/files/Sysmon.zip` (zip SHA256 `6D48089C7FAE14944C82B06767B79CCBA3CC26D13218A4227ED28C90F80D0F0E`) | 2026-09-02 |
| **Sysmon config SHA256** | **`055FEBC600E6D7448CDF3812307275912927A62B1F94D0D933B64B294BC87162`**, 123,257 bytes. `SwiftOnSecurity/sysmon-config` pinned at commit `1836897f12fbd6a0a473665ef6abc34a6b497e31`, file `sysmonconfig-export.xml`, committed to the repo as `lab/configs/sysmonconfig.xml`. **Sysmon itself reports this same hash** via `Sysmon64.exe -c`, so the running sensor is provably using the committed file. | 2026-09-02 |
| Sysmon config caveats | Config schema `4.50` running on a `4.91` binary. `Image loading : disabled`, so Sysmon Event ID 7 never appears. The config's own header reads `Source version: 74 \| Date: 2021-07-08`, so it has no rules for the event types Sysmon added later (25 to 29). | 2026-09-02 |
| **Atomic Red Team commit** | **`cb486d9a888e921fac5902a06c7b46e420bb14a7`** (`redcanaryco/atomic-red-team`, committed 2026-08-28), shallow clone, **1310 files** in the `atomics` folder, 342 technique YAML files | 2026-09-02 |
| Invoke-AtomicRedTeam commit | `8af478bb9e4637df568ac1e596553b025b16cd1b` (`redcanaryco/invoke-atomicredteam`, committed 2025-09-08), module version `2.1.0`, 74 files | 2026-09-02 |
| `powershell-yaml` | `0.4.12`, nupkg SHA256 `D4602BC7A4A093766520422D53CA8B09ACDE162286FAE11E2EE6C8EDFEA07810`. Hard dependency of `Invoke-AtomicTest`, which cannot parse the atomics without it. | 2026-09-02 |
| **Windows build number (guest)** | **`10.0.26100.9168`**, Windows 11 **Education**, `DisplayVersion 24H2`. Fully patched: two update passes, the second returned `updates found: 0`. 7 hotfixes: KB5120710, KB5050575, KB5054273, KB5122035, KB5121003, KB5043113, KB5123304. | 2026-09-02 |
| Wazuh agent version | `4.14.7`, stage `rc1`, commit `8c41e20`, from `wazuh-agent-4.14.7-1.msi` SHA256 `E967F36B75589D6210244FD58239C7021FA53A77C38D92315C3B3BD115002EDE`. Registered as `id=001 name=WIN-EP-01`. Matches the manager exactly. | 2026-09-02 |
| **WIN-EP-01 agent `ossec.conf`** | **current: SHA256 `CED16E0B41384BF421192317E3754732D0E3155A85BA98F2CEEDFA846B0278B1`, 12,115 bytes**, committed as `lab/configs/wazuh-agent-ossec.conf`. History, each kept in the guest: as installed `4F4531A2...F4D64B` (10,152 bytes) as `ossec.conf.telos-orig`; plus the Sysmon `<localfile>` block `F9541429...C4D82F` (10,409 bytes) as `ossec.conf.telos-pre-item8`; plus `rootcheck`, `sca`, `syscheck`, `syscollector` disabled `1F36416E...8F2658` (11,848 bytes) as `ossec.conf.telos-pre-item12`; current adds `active-response` disabled. | 2026-09-03 |
| WIN-EP-01 lab address | `10.20.10.20/24` on adapter `LAB`, MAC `00:0C:29:A7:96:32`. NAT adapter `NAT`, MAC `00:0C:29:A7:96:28`, `192.168.243.130/24`. Default route exists only on NAT. | 2026-09-02 |
| WIN-EP-01 VMware Tools | `12.3.5 build-22544099` from the Workstation `windows.iso` dated 2024-02-12. Drivers after the Windows Update pass: VMware SVGA 3D `9.17.11.3` (Broadcom), VMCI Bus `9.8.30.0` (Broadcom), Pointing Device `12.5.12.0` (VMware). | 2026-09-02 |
| Fence tool | `telos-fence.exe`, 4,096 bytes, SHA256 `D35C939B71ECAC94868947932292531C02A171DECFD3046DEE47DB8E3BD0D814`. Built on the host from `lab/scripts/telos-fence.cs` with the .NET Framework compiler. Verified to emit **exactly one** Sysmon Event ID 1 per run, carrying the run id in its command line. | 2026-09-02 |
| Ubuntu ISO used | `ubuntu-24.04.4-live-server-amd64.iso`, **installed on SIEM-01**. Installer self-update to 24.04.4.1 declined on purpose. | 2026-09-02 |
| **Windows ISO used** | **`E:\Homelab files\Win11_24H2_English_x64.iso`**, retail multi-edition, **Windows 11 Education selected**, left unactivated. Supersedes the Enterprise Evaluation ISO chosen on 2026-08-20. See the decision entry of 2026-09-02. | 2026-09-02 |

`WAZUH_REVISION` reads `rc1` in `wazuh-control info`. The reason is unknown. Cite the apt package
version `4.14.7-1`, not `rc1`.

## Reference corpora

| Item | Value | Date recorded |
|---|---|---|
| `SigmaHQ/sigma` clone commit | `da9bb07d642a2826e89702445d32c795209ec108` | 2026-08-19 |
| `wazuh/wazuh` clone commit | not yet cloned | |

---

# Spike results (fill in after Phase 7)

The spike decides scope, not the topic: T1 is final with no fallback (2026-09-26). Six questions,
listed in runbook Phase 7 and `lab/blueprint.md` section 7. Q3 to Q6 were added on 2026-09-28; until
then this table had rows for Q1 and Q2 only and called the spike "the go/no-go gate for T1".

| Question | Result | Date |
|---|---|---|
| Q1 CoV under Config S | not yet measured | |
| Q1 CoV under Config N | not yet measured | |
| Q2 real wall clock per run | not yet measured | |
| Q2 projected total for 101 runs | not yet measured | |
| Q3 findings on the ten control-versus-control pairs (should be 0) | not yet measured | |
| Q4 share of event keys with at least 30 events across 3 runs | not yet measured | |
| Q5 stimulus fingerprint spread across the 5 control runs | not yet measured | |
| Q6 effect of one extra reboot before the start fence | not yet measured | |
| **Topic decision** | **T1 final, no fallback** (entry of the same date above) | 2026-09-26 |

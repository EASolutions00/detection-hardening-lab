# T1 System Walkthrough

> **Overtaken in part on 2026-10-01; read this first.** The study now uses Wazuh 4.14.7's shipped
> rules (`docs/DECISIONS.md` 2026-10-01, choice 1). No shipped rule names event 4776, and C4's only
> affected rules (92652, 92657) detect pass-the-hash, which C4 blocks, so **C4 behaves like a negative
> control, not a blind spot**. The statistics in Part 3 stay correct for the made-up counts. The
> security reading, "a detection rule that reads 4776 cannot fire", and the rule mapping in Parts 1.2
> and 4 do not hold under the chosen rule set. The positive cases are now C1, C3 and C5; C3 (LSA
> Protection, rule 92900) is the natural replacement example, but it is a value change and needs value
> keying, which is not built. Choosing a new example is the student's decision (WORKLOG 2026-10-08).
>
> **Aligned 2026-09-30 to the current design** (chat 243e446b). It follows the activity diagram
> regenerated 2026-09-29 (`thesis/T1/figures/make_activity_diagram.py`) and `docs/DECISIONS.md` up
> to 2026-09-29. Where this file disagrees with the code, `DECISIONS.md` or
> `proposal-form-FINAL.md`, they win (`docs/PROMPT-new-chat.md` section 3).
>
> **The example is illustrative.** Every count is made up. The analysis numbers in Part 3 are what
> the real code in `src/telos/` prints for those made-up counts, so the classes, rate ratios and q
> values are correct for that input. No capture has run in the lab yet (`docs/STATUS.md`).
>
> **Each part says what is built and what is only designed.** For a designed step, say "is
> designed to", never "does".
>
> The version of 2026-08-31 is in git history (commit `19f6b90`). Its example, disabling Audit
> Process Creation under an invented "CIS 17.6.2", was de-hardening, and it described a design
> that has since changed in twelve places: keys built from the event ID alone, one hash over the
> whole manifest, the change applied once between the phases, no run checks, and the chi-square
> as a gate among them.

---

A complete demonstration of using the system, with worked numbers. It is written as a
demonstration script for the defense, and as a specification to build against. It follows the
activity diagram box by box; the box numbers are those in `ACTIVITY-DIAGRAM-EXPLAINED.md`.

## The scenario

**The change: C4, "Restrict NTLM: Outgoing NTLM traffic to remote servers"**, a class C change in
the catalogue (`lab/blueprint.md`). It is set on the endpoint WIN-EP-01:
`HKLM\System\CurrentControlSet\Control\Lsa\MSV1_0\RestrictSendingNTLMTraffic = 2`, Deny all.

**Why it is class C.** The attack survives: authentication continues over Kerberos
(`lab/blueprint.md`, C4). What changes is the evidence. NTLM credential validation, event 4776, is
written on the machine that holds the account, which for a domain account is the domain controller
(Microsoft's 4776 reference, recorded in `lab/blueprint.md`). After the change NTLM is not used, so
4776 is not written, and a detection rule that reads 4776 cannot fire.

**Three things about this change are not settled.** A panel can check all three.

1. **The control ID.** The catalogue says CIS 2.3.11.13, with no benchmark version. Third-party
   copies of the CIS text, read 2026-09-30, number this item **2.3.11.12** in CIS Microsoft
   Windows 10 Enterprise v5.0.0 (Syxsense) and CIS Windows Server 2019 Stand-alone v2.0.0
   (Tenable), and **2.3.11.13** in the domain controller benchmarks (Tenable). The Windows 11
   Enterprise number is not checked `(unverified)`. OPEN-QUESTIONS 1.
2. **The value.** CIS requires "Audit all" or higher, and states that Deny all also conforms (same
   sources). Audit all, value `1`, only logs NTLM use and blocks nothing, so it cannot cause the
   expected 4776 drop. This walkthrough uses Deny all, value `2`. The catalogue does not record a
   value yet.
3. **The stimulus.** The expected effect needs NTLM logons before the change that still succeed,
   over Kerberos, after it. The network-logon test that must create them is decided but not
   designed (DECISIONS 2026-09-29). A test that can only use NTLM `(unverified: for example one
   that connects to an IP address)` would fail after the change. The run check would then void
   every post-change run, and for that test the change would behave like class B, removing the
   attack together with its evidence (OPEN-QUESTIONS 22).

**The lab it needs:** DC-01 with its own Wazuh agent, WIN-EP-01 joined to the domain, Credential
Validation auditing on both, and the network-logon test. All decided 2026-09-29, none built.

---

## Part 1: Environment setup (Phase 0)

Done once per environment, not once per change. "Environment" means everything in the hashed
parameters (Part 2.2). The hashed parameters of every run must equal the control runs' (Box 8), so
changing any of them, for example adding the `lsass.exe` rule to the Sysmon config, means new
control runs.

### 1.1 Register the environment (Box 1, the engineer)

- **SIEM:** SIEM-01, running Wazuh. The system exports the dated event archive over SSH with
  `telos-archive` (`lab/blueprint.md` section 6, step 10). It does not query the indexer.
- **Hosts:** WIN-EP-01 and DC-01.
- **Configuration snapshot:** `cfg-suppressed`, restored at the start of every run
  (`lab/blueprint.md` section 6, step 1).
- **Rule export:** Wazuh 4.14.7's shipped rule set, exported whole from SIEM-01 (DECISIONS
  2026-10-01; this line said "the pinned clones of the Sigma and Wazuh rule sets" until 2026-10-08).
- **Pinned once, for the whole study:** the attack-test list, the window length, and the repeats (5
  control, 3 before, 3 after). **The list is not chosen yet** (DECISIONS 2026-09-28). This
  walkthrough uses 18 tests and a 15-minute window as examples.

No software is installed on the endpoints. They already run the Wazuh agent, which only collects.
The attack tests reach the guest through the hypervisor's guest operations (FINAL, "System Type and
Deployment").

*Designed, not built: the capture harness does not exist. In the lab, SIEM-01 and WIN-EP-01 exist;
DC-01, the golden snapshot and `cfg-suppressed` do not.*

### 1.2 Build the dependency index (Box 2)

The system reads the rule set and builds the map from event key to the rules that read it, and from
each rule to its ATT&CK techniques.

*Designed, not built. No index module exists in `src/telos/`.*

### 1.3 Five control runs (Boxes 3 and 4)

Five runs with **no change at all**. Each one: restore `cfg-suppressed`, boot, settle 180 s, start
fence, the 18 pinned tests, end fence, drain 120 s, export the dated archive and verify its hash. The
fences are single marker events written inside the telemetry (`lab/scripts/telos-fence.cs`), so the
window is cut by what the machine recorded, not by the host clock.

### 1.4 Check the control runs (the Phase 0 check)

Every control run must have recorded events and completed all 18 tests. If one did not, the setup
ends at **CONTROL RUNS NOT USABLE: investigate, then capture again**. A control run that recorded
nothing would make every key look far noisier than it is, and real losses would be reported
UNCHANGED.

*Designed, not built: `VarianceModel.from_control()` does not check yet. Decided 2026-09-29: built
before data collection (OPEN-QUESTIONS 24).*

### 1.5 Fit the noise model (Box 5)

Six of the keys, as an illustration:

| Event key | R1 | R2 | R3 | R4 | R5 | Mean | CoV | Dispersion |
|---|---|---|---|---|---|---|---|---|
| `Security-4776[PackageName,TargetUserName,Workstation]` | 42 | 40 | 41 | 43 | 39 | 41.0 | 3.86% | 1.00 |
| `Security-4624[AuthenticationPackageName,LogonType,TargetUserName]` | 120 | 117 | 123 | 119 | 121 | 120.0 | 1.86% | 1.00 |
| `Security-4769[]` | 58 | 61 | 57 | 60 | 59 | 59.0 | 2.68% | 1.00 |
| `Sysmon-3[DestinationIp,DestinationPort,Image]` | 412 | 385 | 446 | 390 | 429 | 412.4 | 6.25% | 1.61 |
| `Security-4697[ServiceFileName,ServiceName]` | 2 | 1 | 3 | 2 | 2 | 2.0 | 35.36% | 1.00 |
| `Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]` | 1171 | 1208 | 1134 | 1236 | 1190 | 1187.8 | 3.24% | 1.24 |

**CoV**, the coefficient of variation, is the standard deviation divided by the mean: how much a
count moves between identical runs, as a fraction. **Dispersion** is the variance divided by the
mean. It is floored at 1.0, so the system never claims a key is more regular than random arrival;
four of these six keys sit on that floor.

**This table is why subtraction fails.** The 4624 key moves under 2% between identical runs. The
Sysmon-3 key moves over 6%. The same 5% drop is a signal for the first and nothing for the second.

`Security-4769[]` has empty brackets because 4769 has no tracked fields in the code today
(`DEFAULT_TRACKED_FIELDS` in `eventkey.py` has no entry for 4768 or 4769; OPEN-QUESTIONS 18). Such
an event is counted by its type alone.

*Built: `variance.py`, `VarianceModel.from_control()`. These numbers are its output.*

The same five runs give the **stimulus fingerprint** and its spread. Here the fingerprint is the
count of Sysmon Event 1, process creation, in the window: 1,134 to 1,236 across the five runs. This
walkthrough uses that lowest-to-highest range as the tolerance; how the tolerance is computed is not
decided (OPEN-QUESTIONS 22). *Designed, not built.*

### 1.6 Saved (Box 6)

The noise baseline, the stimulus tolerance and the index are stored, and connector **A** carries
them into Phase 4.

---

## Part 2: Running a validation (Phases 1 to 3)

### 2.1 The engineer defines the run (Box 7)

```
NEW VALIDATION RUN
Target hosts             WIN-EP-01, DC-01
Tests, window, repeats   as pinned in Phase 0   (18 tests, 15 minutes, 3 per phase)
```

The engineer chooses nothing else here. The engineer does not need to know which detection rules
will be affected. Finding that out is the purpose of the system.

### 2.2 The manifest's parameters are frozen and hashed (Box 8)

The manifest has two parts (D2, DECISIONS 2026-09-14; `lab/blueprint.md` section 6, step 11).

- **Hashed parameters,** which must be identical for two runs to be compared: the configuration
  snapshot ID, the Atomic Red Team commit and test IDs, the window, the repetitions, the rule set
  version, the thresholds, the Sysmon config hash, the Wazuh version, and the harness's git commit.
- **Recorded, not hashed:** the run ID, the phase, the change ID and its script hash, the fence
  times, and each test's exit status and duration.

```
Parameters hash     7f3a9c2e14b8d05f    (example)
Control runs        7f3a9c2e14b8d05f    match
```

If the hashes differ, the system is designed to decline the comparison and name the parameter that
differs (FINAL, Module 1). *Designed, not built.*

### 2.3 Three valid pre-change runs (Boxes 9 and 10, the Phase 1 run check, Box 11)

```
[P1] Restore snapshot cfg-suppressed ........... done
     Boot, settle 180 s ........................ done
     START FENCE ............................... emitted
     18 pinned tests ........................... 18 of 18 completed
     END FENCE ................................. emitted
     Drain 120 s ............................... done
     Export dated archive, verify hash ......... done
     Run check: 18 of 18 tests, fingerprint 1,182 (tolerance 1,134 to 1,236) ... VALID
```

**A voided run, as an example.** On its first attempt P3 completed 17 of 18 tests and its
fingerprint was 1,090, outside the tolerance. The run is **VOID**: the reason is written in the
manifest, the run is not analysed, and it is captured again. That is why the loop reads "3 valid
runs": the analysis needs the same number of runs in both phases (`analyse()` refuses otherwise).
The repeat of P3 was valid, with a fingerprint of 1,165.

**The pre-change profile** is built from the exported events. Each event becomes a key: the event
type plus which tracked fields carried a value. Empty, `-`, `N/A`, `(null)` and `NULL` count as
absent; numeric zero counts as present. For a short list of fields the key will also record the
value, grouped into a few classes (DECISIONS 2026-09-29). C4 needs none of them, because its effect
is a change in rate, not in value.

*Built: `eventkey.py`, `KeyBuilder.build()` and `is_populated()`. Designed, not built: the run
check, the voiding, and value keying.* The pre-change profile is stored, and connector **B**
carries it into Phase 5.

### 2.4 Supply the hardening change (Boxes 13 and 14)

The engineer supplies the change ID and the script that applies it,
`change-C4-restrict-ntlm-outgoing.ps1` (the naming rule in `lab/scripts/README.md`; no change script
exists yet). The system records both in the manifest's record part, **outside the hash**. The
change is the one thing that must differ between a before run and an after run. Inside the hash,
the two could never match.

### 2.5 Three valid post-change runs (Box 15, the Phase 3 run check)

```
[Q1] Restore snapshot cfg-suppressed ........... done
     Apply change-C4-restrict-ntlm-outgoing.ps1  done
     Reboot if needed, settle 180 s ............ done
     Confirm inside the host ................... RestrictSendingNTLMTraffic = 2
     START FENCE, 18 of 18 tests, END FENCE, drain 120 s, export ... done
     Run check: tests 18 of 18, fingerprint 1,178, change confirmed ... VALID
```

**The order is the design.** The change is applied, and the machine restarts and settles, **before**
the window opens (D2). Otherwise the change and its restart would sit inside every after run and no
before run, and the comparison would measure two differences at once. The change is applied again
in every run because every run begins by restoring the snapshot, and the restore erases it. The
2026-08-31 version of this walkthrough applied the change once between the phases, which that
restore would have undone.

The change is confirmed inside the host, not from the SIEM, because events written during start-up
never reach the archive (OPEN-QUESTIONS 28).

What this does not yet prove: that the extra restart leaves no trace in the window. The spike
measures it (runbook Phase 7).

*Designed, not built: the whole capture sequence is the harness.*

---

## Part 3: What the system computes (Phase 4)

### Stage A. Align (Box 19)

The two profiles are aligned over the union of their keys, with an explicit zero wherever a key is
missing from one phase.

| Event key | P1 | P2 | P3 | Q1 | Q2 | Q3 |
|---|---|---|---|---|---|---|
| `Security-4776[PackageName,TargetUserName,Workstation]` | 43 | 40 | 41 | 0 | 0 | 0 |
| `Security-4624[AuthenticationPackageName,LogonType,TargetUserName]` | 121 | 118 | 124 | 119 | 123 | 120 |
| `Security-4769[]` | 60 | 58 | 61 | 101 | 98 | 103 |
| `Sysmon-3[DestinationIp,DestinationPort,Image]` | 418 | 392 | 431 | 399 | 440 | 385 |
| `Security-4697[ServiceFileName,ServiceName]` | 2 | 2 | 1 | 2 | 1 | 2 |
| `Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]` | 1182 | 1201 | 1165 | 1178 | 1195 | 1189 |

*Built: `differential.py`, `align()`.*

### Stage B. Capture check, then one chi-square as a summary (the Phase 4 check, Box 19a)

Every repetition in both phases recorded events, so the run can be tested. Had any repetition
recorded nothing, the run would end as **NOT TESTABLE**, because an empty capture cannot be told
apart from a dead agent.

```
Chi-square over the whole 2 x 6 profile:  155.6,  p = 8.6e-32
Reported as a summary. Every key goes on to Stage C whatever it says.
```

*Built: `capture_problem()`, `global_gate()` and `analyse()` in `differential.py`.*

### Stage C. Test and classify every key (Boxes 20 and 21)

Rates are events per run.

| Event key | Before | After | Ratio | q | Class |
|---|---|---|---|---|---|
| `Security-4776[PackageName,TargetUserName,Workstation]` | 41.3 | 0.0 | 0.000 | 7.0e-54 | **LOST** |
| `Security-4624[AuthenticationPackageName,LogonType,TargetUserName]` | 121.0 | 120.7 | 0.997 | 0.97 | UNCHANGED |
| `Security-4769[]` | 59.7 | 100.7 | 1.687 | 7.4e-8 | UNCHANGED |
| `Sysmon-3[DestinationIp,DestinationPort,Image]` | 413.7 | 408.0 | 0.986 | 0.97 | UNCHANGED |
| `Security-4697[ServiceFileName,ServiceName]` | 1.7 | 1.7 | n/a | n/a | INCONCLUSIVE |
| `Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]` | 1182.7 | 1187.3 | 1.004 | 0.97 | UNCHANGED |

Profile outcome: **CHANGED**, because one key is LOST. Five keys were tested; the 4697 key was not.

Reading each row:

- **4776 is LOST.** 124 events before, at least the 30 needed, exactly zero after, and its q value
  survives the correction. The q value is the p value after the Benjamini-Hochberg correction, which
  holds the expected share of false findings at 5% or less when many keys are tested at once.
- **Sysmon-3 fails all three REDUCED conditions.** Its q is 0.97, above 0.05. Its ratio is 0.986,
  above 0.5. Its drop, 1.4%, is inside its noise band of 3 × 6.25% = 18.7%. Any one failure is
  enough to keep it out of the report.
- **4769 rose by 69%, and that is not a finding.** Its q is 7.4e-8, so the rise is real, but the
  method looks for lost evidence, and a rise is UNCHANGED. It is the expected sign that
  authentication moved to Kerberos.
- **4624 did not move in count.** The same logons still happen, now over Kerberos, so their
  `AuthenticationPackageName` changes from `NTLM` to `Kerberos`. That is a change of value, which
  a key that records only presence cannot see, and the field is not on the value-keying candidate
  list (DECISIONS 2026-09-29).
- **4697 is INCONCLUSIVE.** Five events before is under 30, so it is not tested. It is reported as
  "not tested", never as "unchanged".
- A key the control runs never saw would also be INCONCLUSIVE. There is none here.

*Built: `_test_key()` and `classify()` in `differential.py`.*

### The comparison that is the study's result

The naive method on the same data reports every key whose mean fell, by any amount (`baseline.py`).

| Event key | Naive differencing | Proposed method |
|---|---|---|
| `Security-4776[...]` | reports it, 100% drop | LOST |
| `Sysmon-3[...]` | **reports it, 1.37% drop** | not reported |
| `Security-4624[...]` | **reports it, 0.28% drop** | not reported |
| Result | 1 correct, **2 false alarms** | 1 correct, **0 false alarms** |

Both false alarms are keys that moved by less than their own run-to-run noise.

**This is made-up data, and the claim is falsifiable either way.** If the lab's measured noise turns
out near zero, the naive method raises almost no false alarms, the statistical layer gains nothing
inside the lab, and the study says so (FINAL, "The Variance Floor and External Validity").

*Built: `baseline.py`, `naive_differencing()`; `report.py`, `render_comparison()`.*

### Stage D. Pair field-level losses (Box 22)

A LOST key and a NEW key of the same event type, where the new key has fewer fields, would mean a
field was emptied while the event kept firing. There is no NEW key here: C4 stops 4776 as a whole
event, so nothing is paired.

*Built but not connected: `field_loss_pairs()` in `eventkey.py` is tested, but `analyse()` and
`report.py` do not call it yet. Decided 2026-09-29: connected before data collection
(OPEN-QUESTIONS 30).*

### Stage E. Map the loss to rules and techniques, and score it (Boxes 23 and 24)

The lost 4776 key is looked up in the index: which rules read it, which ATT&CK techniques those
rules cover, and whether another key that is still observed also supports each technique
(**surviving coverage**). A technique that keeps another working source is not blind. A technique
whose only source went silent is.

The impact score weighs the severity of the affected rules, how many are affected, the importance
of the techniques, and surviving coverage (FINAL, Module 4).

*Designed, not built. There is no index and no scorer, so this walkthrough names no rules and gives
no score. The 2026-08-31 version printed rule IDs and a score of 89; no index produced them.*

### Stage F. Remediation candidates (Box 25)

Two levels, in order of confidence: a **surviving source**, another key still observed that
supports the same technique; and a **known compensating control** from a curated list. The system
does not write rules and deploys nothing (DECISIONS 2026-09-14, D1; 2026-09-28).

*Designed, not built.*

---

## Part 4: The report (Box 26)

```
VALIDATION REPORT                                          (example data)
Change    C4  Restrict NTLM: Outgoing NTLM traffic to remote servers
          CIS item number and benchmark version: to be confirmed (see the scenario)
Hosts     WIN-EP-01, DC-01
Manifest  7f3a9c2e14b8d05f  (parameters; the change is recorded outside the hash)

VERDICT   BLIND SPOTS FOUND.  1 finding.  Profile outcome CHANGED.
          Whole-profile chi-square 155.6, p = 8.6e-32 (summary only)

FINDING 1   LOST   Security-4776[PackageName,TargetUserName,Workstation]
  rate before    41.3 per run
  rate after     0.0 per run
  95% bound      the after rate is at most 0.024 of the before rate
  q value        7.02e-54   (BH corrected)
  noise floor    3.86% CoV, dispersion 1.00
  rules, techniques, impact, remediation     designed, not built

NOT TESTED, REPORTED AS INCONCLUSIVE
  Security-4697[ServiceFileName,ServiceName]   5 occurrences before the change

NOT REPORTED
  Sysmon-3[...]       fell 1.4%, inside its noise band of 18.7%
  Security-4769[]     rose 69%; a rise is not a loss
  Security-4624[...]  same count; its package moved from NTLM to Kerberos,
                      a value change this key does not see
```

*Built: the statistical part, printed as text by `report.py`. Designed: the rules and techniques,
coverage change, remediation, and the CSV, JSON and ATT&CK Navigator exports.*

---

## Part 5: Review, remediate, re-validate (Phase 5)

*All of Phase 5 is designed, not built.*

### 5.1 The detection engineer reviews the report (Box 27)

Three outcomes are possible.

- **No remediation:** the engineer documents and accepts the residual risk. The finding closes as
  ACCEPTED.
- **A detection rule:** the engineer writes a rule against evidence that still exists.
- **Restore telemetry:** the engineer supplies a fix as a script, an audit or Sysmon setting.

**For C4, restoring telemetry is not a real option `(reasoning, not measured)`.** 4776 records NTLM
credential validation, and after the change NTLM is not used. Bringing 4776 back would mean allowing
NTLM again, which undoes the hardening. So the realistic choices here are a rule on the evidence
that remains, or acceptance.

### 5.2 Re-validation, detection rule mode (Box 31)

A new rule does not change what the host emits, so a fresh telemetry comparison would prove
nothing. The system replays the manifest and checks that the rule fires.

```
RE-VALIDATION  (mode: detection rule)                      (example)
Replay manifest 7f3a9c2e14b8d05f:
  restore cfg-suppressed, apply change-C4 script, confirm, run the 18 pinned tests
New rule fired on the stimulus ............ yes
FINDING 1 -> CLOSED AS FIXED
Accepted baseline: cfg-suppressed + change-C4-restrict-ntlm-outgoing.ps1
```

If the rule had not fired, the finding would go back to review. **A finding cannot reach "closed as
fixed" without a passing re-validation run.** The system is designed to enforce this rather than
accept the engineer's word.

### 5.3 Re-validation, telemetry mode (Box 30)

Not used for C4, for the reason in 5.1. For a change where it applies: restore the snapshot, apply
the change script and then the fix script, confirm both inside the host, capture, and compare
against the stored pre-change profile (connector **B**). A fix made once by hand would be erased by
the restore at the start of every capture, so the fix must be a script (DECISIONS 2026-09-28).

### 5.4 The accepted baseline

Whether the finding closes as FIXED or ACCEPTED, the accepted baseline becomes the snapshot plus the
scripts applied on top of it. Later runs rebuild it the same way, so an accepted loss is not
reported again on every run. In this study each change is tested alone against the unchanged
snapshot, so the list of accepted scripts is empty for every study run (DECISIONS 2026-09-28).

---

## For the defense: three sentences

1. "The system learns how much each event key naturally varies, by running the same pinned attack
   tests five times and changing nothing."
2. "Then it compares before and after. It reports a loss only when it survives the correction for
   testing many keys, and a reduction only when the rate also fell to half or less, by more than
   that key's own natural variation."
3. "Then it is designed to show which detection rules depended on the lost evidence, which
   techniques are now unseen, and which still-working source could replace it."

## The single strongest slide

The comparison table in Part 3: on the same data, the naive method raises two false alarms and the
proposed method raises none. **Say that the numbers are illustrative** until the lab produces its
own. The real version of this table comes from the evaluation.

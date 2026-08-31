# T1 System Walkthrough

> # DO NOT USE THIS FOR THE DEFENSE YET
>
> **The example scenario in this document is wrong.** Written 2026-08-31 without checking
> [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) item 1, which had already recorded the defect on
> 2026-08-20.
>
> **What is wrong:**
> 1. The scenario uses "disable Audit Process Creation". CIS **requires** this setting to be
>    enabled (17.3.1 or 17.3.2). Disabling it is de-hardening, not hardening. It is a class A
>    item in the catalogue classification.
> 2. The control ID "CIS 17.6.2" cited below is invented and does not exist.
> 3. The walkthrough never applies condition (d) of the corrected blind-spot definition: the
>    technique must still be executable after the change.
> 4. The surviving-coverage numbers are internally inconsistent. If Sysmon Event ID 1 still
>    records process creation, the Mshta and Service Control detections would likely survive
>    too. See OPEN-QUESTIONS item 1c.
>
> **What is still usable:** the structure (Parts 1 to 5), the noise-floor table in Part 1.3,
> and the naive-versus-proposed comparison in Stage D. Those do not depend on which change is
> used as the example.
>
> **To fix:** rebuild the example around a class C change once the 16-change catalogue is
> rebuilt with pinned control IDs. The three solid class C candidates recorded so far are
> disable WDigest, restrict NTLM, and enforce RDP NLA. The catalogue rebuild is the top task
> in OPEN-QUESTIONS item 1.

---

A complete demonstration of using the system, with worked numbers.

**Nothing is built yet.** This describes the designed behavior. It is written as a
demonstration script for the defense, and as a specification to build against.

**Scenario (INVALID, see the warning above):** a company must disable Audit Process Creation
to meet CIS Benchmark 17.6.2. The change is correct and required. The question is whether
detection survives it.

---

## Part 1: One-time setup

Done once per environment, not once per change.

### 1.1 Connect to the existing platform

The engineer enters the Wazuh indexer address and credentials. No new agent is installed
anywhere. The endpoints already run the Wazuh agent, which is how their events reach the
platform.

### 1.2 Build the dependency index

The system reads the detection rule set and builds the map linking event types to rules to
ATT&CK techniques.

```
Index built.
  Rules read:            847
  Event-type keys found: 213
  ATT&CK techniques:      94
```

### 1.3 Measure the noise floor

The system runs the same attack suite 5 times against the same snapshot, changing nothing.
About 2 hours, unattended.

Three of the 213 event types, as an illustration:

| Event type | R1 | R2 | R3 | R4 | R5 | Mean | Noise (CoV) |
|---|---|---|---|---|---|---|---|
| 4688 Process Creation | 1251 | 1238 | 1247 | 1259 | 1240 | 1247.0 | **0.7%** |
| 5156 Network Connection | 4102 | 3847 | 4455 | 3901 | 4290 | 4119.0 | **6.2%** |
| 4697 Service Installed | 2 | 1 | 3 | 2 | 2 | 2.0 | 36% |

**This table is the heart of the system.**

Event 4688 is stable. It varies under 1% between runs. A 5% drop in 4688 means something
real happened.

Event 5156 is noisy. It swings over 6% on its own with nothing changed. A 5% drop in 5156
means nothing at all.

The same 5% drop means two different things. That is why simple subtraction fails, and it is
the empirical basis for the whole statistical layer.

---

## Part 2: Running a validation

### 2.1 The engineer fills one form

```
NEW VALIDATION RUN

Change ID          CIS-17.6.2
Description        Disable Audit Process Creation subcategory
Apply script       change-01-disable-audit-process-creation.ps1
Target host        WIN-EP-01
Snapshot           cfg-natural
Stimulus set       ART-WINDOWS-BASELINE-v1  (18 tests)
Window duration    15 minutes
Repetitions        3 per phase

                                        [ Start ]
```

The engineer needs no prior knowledge of which rules will be affected. Determining that is
the purpose of the system.

### 2.2 The manifest is frozen and hashed

```
Manifest hash: 7f3a9c2e14b8d05f
Any later run must produce this same hash to be comparable.
```

### 2.3 Three pre-change captures

Unattended, about 75 minutes. Each capture:

```
[1/3] Restoring snapshot cfg-natural .............. done
      Booting ............................. done
      Settling 180 s ...................... done
      START FENCE emitted at 14:02:11
      Running 18 Atomic Red Team tests .... done
      END FENCE emitted at 14:17:44
      Draining 120 s ...................... done
      Collecting events between fences .... 34,891 events
```

The settle period excludes the boot event storm. The drain period catches events still
buffered by the agent. Both are required, and both are fixed for every run.

### 2.4 Apply the hardening change

```
Running change-01-disable-audit-process-creation.ps1
  auditpol /set /subcategory:"Process Creation" /success:disable /failure:disable
Verifying ......... setting confirmed OFF
Rebooting ......... done
```

### 2.5 Three post-change captures

Same manifest. Same 18 tests. Same timings. Nothing else differs.

Total: about 3 hours, unattended.

---

## Part 3: What the system computes

### Stage A. Count

**Before the change:**

| Event type | P1 | P2 | P3 | Mean |
|---|---|---|---|---|
| 4688 | 1244 | 1252 | 1249 | 1248.3 |
| 5156 | 4180 | 3920 | 4310 | 4136.7 |
| 4697 | 2 | 2 | 1 | 1.7 |

**After the change:**

| Event type | Q1 | Q2 | Q3 | Mean |
|---|---|---|---|---|
| 4688 | 0 | 0 | 0 | **0.0** |
| 5156 | 3990 | 4402 | 3850 | 4080.7 |
| 4697 | 2 | 1 | 2 | 1.7 |

### Stage B. The global gate

One chi-square test across the whole profile, not one per event type.

```
Chi-square across 213 event types
Result: the profile changed. p < 0.001
Gate PASSED. Proceeding to per-event testing.
```

If this had failed, the run stops and records "no significant change". A negative result is
recorded, not discarded.

### Stage C. Test each event type

| Event | Before | After | Ratio | Noise floor | Verdict |
|---|---|---|---|---|---|
| 4688 | 1248.3 | 0.0 | 0.000 | 0.7% | **LOST** |
| 5156 | 4136.7 | 4080.7 | 0.986 | 6.2% | **UNCHANGED** |
| 4697 | 1.7 | 1.7 | 1.000 | too few counts | **INCONCLUSIVE** |

Reading each row:

**4688 went from 1248 to zero.** Its natural variation is 0.7%. A drop to zero is far outside
that. This is a real loss.

**5156 dropped 1.4%.** Its natural variation is 6.2%. The drop is smaller than the noise. Not
a finding.

**4697 occurs twice per run.** Below the minimum count needed for the test to have power.
Reported as inconclusive, not as unchanged. Calling it unchanged would claim knowledge the
data does not support, and would inflate the reported recall.

### Stage D. The comparison that is the experimental result

The naive method runs on the same data. It reports any event whose count went down.

| Method | 4688 | 5156 | Result |
|---|---|---|---|
| Naive differencing | reports LOST | **reports LOST** | 1 correct, **1 false alarm** |
| Proposed system | reports LOST | reports unchanged | 1 correct, **0 false alarms** |

This table, scaled across 16 changes, is the headline result of the study.

### Stage E. Map the loss to detections

```
4688 is read by 12 detection rules
  Rule 92052  Suspicious Process Creation        severity 12
  Rule 92053  Mshta Suspicious Execution         severity 12
  ... 10 more

Those 12 rules cover 5 ATT&CK techniques.

Checking surviving coverage for each technique:
  T1059.001 PowerShell     -> Sysmon Event 1 still active. STILL COVERED
  T1053.005 Scheduled Task -> Sysmon Event 1 still active. STILL COVERED
  T1036     Masquerading   -> Sysmon Event 1 still active. STILL COVERED
  T1218.005 Mshta          -> no surviving source. NOW BLIND
  T1543.003 Service Ctrl   -> no surviving source. NOW BLIND

Impact score: 89 of 100
  affected rule severity   high
  rules affected           12
  techniques fully blind   2 of 5
```

The system does not report "5 techniques lost". Three still have working detection through
Sysmon Event 1. Only 2 are genuinely blind. That distinction is what makes the ranking
useful rather than alarming.

---

## Part 4: The report

```
VALIDATION REPORT
Change:   CIS-17.6.2  Disable Audit Process Creation
Host:     WIN-EP-01        Date: 2026-10-05
Manifest: 7f3a9c2e14b8d05f

VERDICT: BLIND SPOTS FOUND.  1 finding.  Highest impact 89.

FINDING 1                    Impact 89           LOST
  Event type   4688 Process Creation
  Rate before  1248.3 per window
  Rate after   0.0 per window
  Confirmed    loss exceeds the measured noise floor of 0.7%

  Rules blinded             12
  Techniques fully blind     2   T1218.005 Mshta
                                 T1543.003 Service Control

  REMEDIATION CANDIDATES
  1. Surviving source     Sysmon Event ID 1 records process creation
                          and is still active. 12 rules can be
                          re-expressed against it.
  2. Compensating control Sysmon config already captures the needed
                          fields. No new telemetry required.

  NOTE: the hardening change stays in place. Remediation restores
        detection, it does not reverse the security control.

NOT REPORTED
  5156  dropped 1.4%, within its 6.2% noise band
  4697  too few occurrences to test. Inconclusive, not cleared.
```

Exports: a CSV of all 213 event types, a JSON of findings for a ticketing system, and an
ATT&CK Navigator layer showing the 2 blind techniques in red.

---

## Part 5: Fix and re-validate

### 5.1 The detection engineer acts

They read the report, accept candidate 1, and rewrite the 12 rules to read Sysmon Event 1
instead of 4688.

### 5.2 Re-validation

The system knows this was a detection rule fix, not a telemetry fix, so it replays the
identical manifest and checks whether the rules now fire. It does not need a fresh capture,
because a rule change does not alter what the host emits.

```
RE-VALIDATION  (mode: detection rule)
Replaying manifest 7f3a9c2e14b8d05f
  12 rewritten rules fired on the stimulus:  12 of 12
  Techniques recovered:  T1218.005, T1543.003

FINDING 1 -> CLOSED AS FIXED
```

A finding cannot reach "closed as fixed" without a passing re-validation. The system enforces
this rather than accepting the engineer's word.

If instead the fix had been a telemetry restoration, such as re-enabling an audit
subcategory, the re-validation would take a fresh capture and compare it against the stored
pre-change profile, because that kind of fix does change what the host emits.

---

## For the defense: three sentences

1. "The system learns how much each log type naturally varies, by running the same test five
   times and changing nothing."
2. "Then it compares before and after, and only reports a loss when the drop is bigger than
   that natural variation."
3. "Then it shows which detection rules depended on the lost log, which attacks are now
   invisible, and which still-working log could replace it."

## The single strongest slide

The Stage D table. It shows the naive method producing a false alarm on the same data where
the proposed method does not. That is the entire contribution in six numbers.

# Expected results, written before any run

Written 2026-11-26 (chat 26343d0f), before any run with the pinned attack list. The commit date of this file is the
proof that each expectation came before its data. Never edit an expectation after its runs exist. If one must change
before the runs, add a dated line that says what changed and why.

Why this file exists:
- The adviser asked for it: "list the hardening changes and the expected results before the demo" (DECISIONS
  2026-11-23, point 8).
- The evaluation needs cases where the right answer is "a loss", or recall cannot be measured (OPEN-QUESTIONS 38 and
  42; DECISIONS 2026-11-26).

---

## 1. The cases

Every case uses the same pinned attack list (DECISIONS 2026-11-18): one Remote Desktop sign-in from the host, then
the LSASS tests T1003.001 tests 1, 2 and 13, then cleanup. Each case is one change, applied alone, after a restore of
`golden-base`.

A **test case** (K1 to K3) is a configuration mistake made on purpose: the opposite of a CIS or DISA item. It is never
called hardening. Its job is to remove evidence that is known in advance, so we can check that the system finds it.

| Case | Kind | Change | Benchmark item | Evidence expected to disappear | Rules expected to stop | Techniques expected to lose all alerts | Does the attack still work? | Expected verdict |
|---|---|---|---|---|---|---|---|---|
| N | control | none | none | none | none | none | yes | no change |
| C1 | hardening | WDigest `UseLogonCredential = 0` | DISA V-253358 | none (the console sign-in did not change, 2026-11-13) | none | none | yes | no blind spot |
| C3 | hardening | LSA Protection, `RunAsPPL = 2` | CIS Windows 11 Enterprise v5.1.0, 18.9.27.2 (`RunAsPPL = 2` is a stated deviation) | part of `Sysmon-10` access to `lsass.exe` (73.3 to 26.3 per run in the spike) and `Sysmon-8[]` | 92403 and 61625 (level 12) | T1055 | **no**: the dump is blocked | **prevention**, not a blind spot (DECISIONS 2026-11-13) |
| C5 | hardening | NLA on for Remote Desktop | CIS 18.10.57.3.9.4 in Windows 10 Enterprise v4.0.0 (the Windows 11 number is not confirmed) | none with the default client (2026-11-12) | none | none | yes | no blind spot: "the predicted effect was not seen" |
| K1 | test case | "Audit Logon" set to No Auditing | breaks DISA WN11-AU-000075 (V-253317, CAT II) and CIS Intune for Windows 11 v2.0.0, 17.5.4 | every 4624 and 4648 event (about 15 and 11 per run) | 92653 and 92657 (the sign-in), 67022 | **T1021.001, T1078.002, T1550.002** | **yes**: auditing does not control access, so the sign-in still opens a session | **blind spot** |
| K2 | test case | "Include command line in process creation events" off | breaks CIS Windows 11 Enterprise v5.0.1, 18.9.3.1 and DISA WN11-CC-000066 | the `CommandLine` field of 4688; the event is still written | none: 67027 matches the event ID only | none | yes | field loss that affects no detection |
| K3 | test case | "Audit Process Creation" set to No Auditing | breaks CIS Windows 11 Enterprise v5.0.1, 17.3.2 | every 4688 event (about 50 per run) | 67027 (level 3, no technique) | none: the Sysmon event 1 rules still fire | yes | detection loss with no technique lost |

**Where each expectation comes from.** Not from the system, so the test is not circular:
- Which events a setting controls: Microsoft's audit documentation (the "Logon" subcategory writes 4624, 4625, 4648
  and 4675; "Process Creation" writes 4688; the command-line setting fills 4688's `CommandLine`).
- Which rules read those events: the rule files themselves (`data/rules/wazuh-4.14.7`, read 2026-11-26;
  OPEN-QUESTIONS 42).
- Event counts per run: the spike runs of 2026-11-16 plus the sign-in measured by hand (OPEN-QUESTIONS 37: two type 3
  NTLM logons with 92657, one 4648, two type 10 logons with 92653). `(unverified)` until the first pinned run.
- C1, C3 and C5 were already measured, so their rows are confirmations, not blind predictions. Only K1 to K3 are new.

**2026-11-26, later: two changes before any run** (DECISIONS 2026-11-26; `docs/GOLDEN-BASE-V2.md`). The expected
results above do not change.
1. **One CIS version:** CIS Microsoft Windows 11 Enterprise Benchmark **v3.0.0**, the version Wazuh 4.14.7's scan
   checks. Its numbers: C1 18.4.8, C3 18.9.26.2, C5 18.10.56.3.9.4, K1 17.5.4, K2 18.9.3.1, K3 17.3.2. The table above
   keeps the numbers as first written.
2. **C5 now sets NLA through the Group Policy key**, and the baseline turns NLA off through the same key, as Group
   Policy would. C5's expected events stay the same. Whether the policy key gives the same events as the listener
   value is checked by the trial run `trial-C5-1`.

---

## 2. What the current system will print for these events (the dry run)

`src/known_answer_dryrun.py` ran the real pipeline on the expected events: real run-to-run noise from 11 spike runs,
with the sign-in and each case's effect added by the script. Output: `data/summaries/known-answer-dryrun-2026-11-26.txt`.
It checks that this file and the code agree. **It is not evidence from the lab.**

| Case | Keys found LOST | Expected keys missed | Top ranked line | "No longer detected" (coverage) | False findings: system / plain subtraction |
|---|---|---|---|---|---|
| N | none | none | none | none | 0 / 1 (`Application-1001[]`, 1 to 0) |
| K1 | the other 4624 key (34 to 0), `Security-4648[]` (33 to 0) | **the two sign-in keys, 6 to 0 each: INCONCLUSIVE** | the other 4624 key: 5 techniques (T1068, T1078, T1110, T1136, T1203), level 15, 12 rules | **T1021.001, T1078.002, T1550.002** | 0 / 1 |
| K2 | `Security-4688[CommandLine,...]` (157 to 0), with the key without `CommandLine` NEW and a FIELD LOSS line | none | that key: 0 techniques, level 3, 1 rule | none | 0 / 1 |
| K3 | `Security-4688[CommandLine,...]` (157 to 0) | none | that key: 0 techniques, level 3, 1 rule | none | 0 / 1 |

What this shows, in order:
1. **K2 and K3 come out exactly as expected.**
2. **K1's blind spot shows in the coverage section**: the three techniques whose alerts fired before and not after.
3. **K1's two sign-in keys are not tested.** A key with fewer than 30 events in the before runs is INCONCLUSIVE
   (`MIN_PRE_COUNT`). The sign-in writes 2 + 2 logon events per run, so 6 in 3 runs. This is the same problem the
   spike found for C3's `Sysmon-8[]` (OPEN-QUESTIONS 25). **The student decides the rule before the runs:
   OPEN-QUESTIONS 43.** With the exact test for a complete loss (option (b) there), the dry run finds all 4 K1 keys
   (q = 0.0087 for each sign-in key) and still no false finding in N.
4. **K1's top ranked line names 5 techniques that never had an alert in the before runs.** The ranking lists the
   techniques of every rule that could read the lost key. The coverage section lists the techniques that really
   fired. The report should say which is which (OPEN-QUESTIONS 43, second point).
5. **K2 and K3 get the same ranking numbers**, although rule 67027 keeps firing in K2 and stops in K3. Only the FIELD
   LOSS line tells them apart (OPEN-QUESTIONS 43, third point).

**2026-11-26, later the same day: the rule changed, before any run.** The student chose option (b) of OPEN-QUESTIONS
43 (DECISIONS 2026-11-26): a key that drops to zero is tested with the exact test at any count. The expectations in
section 1 did not change. The dry run with the new code, `data/summaries/known-answer-dryrun-2026-11-26-after-item-43.txt`:
- **K1 finds 4 of 4 keys**; each sign-in key is LOST with q = 0.0087. The top ranked line is now a sign-in key, and its
  blind techniques include T1021.001, T1078.002 and T1550.002, still mixed with potential ones (point 4).
- N, K2 and K3 are unchanged.
- On the real C3 runs, `Sysmon-8[]` is now LOST too (6 to 0, q = 0.0198), as section 1's C3 row already expects.

---

## 3. How the results are scored (fixed before the runs)

- **Unit:** the event key.
- **Expected LOST keys**, by event ID and field only, among the keys seen in the before runs:
  K1, every 4624, 4625, 4648 and 4675 key; K2, every 4688 key with `CommandLine`; K3, every 4688 key.
  N, C1 and C5: none. C3 is not scored for recall, because its result is already known from the spike.
- **Found:** keys the system classifies LOST or REDUCED.
- **Numbers:** true positives, false positives, false negatives; precision, recall, F1, and the false-positive rate
  (false positives divided by the keys not expected to change). The same numbers for plain subtraction (every key
  whose joined count fell), so the noise floor's benefit is measured.
- **Technique level:** the coverage section's "no longer detected" must equal the expected techniques: K1
  {T1021.001, T1078.002, T1550.002}; C3 {T1055}; every other case, none.
- **Field level:** K2 must show the FIELD LOSS line with `CommandLine` dropped.
- **Verdict level:** the system cannot yet tell a blocked attack from a hidden one (limitation 8). For every case with
  a loss, a person checks whether the attack still worked, and writes it down with the evidence.
- **Reporting:** every number is reported as found. A miss is a result, not something to hide or rerun until it
  passes.

---

## 4. How we show the attack still worked in K1

With "Audit Logon" off there are no logon events, so the proof must come from elsewhere:
1. The step `rdp-signin-30s` exits 0: the client stayed open for 30 seconds.
2. Event 4672 ("special privileges assigned to new logon") belongs to "Audit Special Logon", which K1 does not turn
   off. It is written at each administrator sign-in, so `Security-4672[]` should stay the same while 4624 disappears.
   `(unverified)` that the sign-in's logons write 4672.
3. One hand trial (the student, in the VM window): during a K1 run, `query session` in the guest shows the Remote
   Desktop session.

---

## 5. What must be true before the runs

1. The K1 to K3 scripts are in `C:\telos\` in the guest. They are not in `golden-base` yet (OPEN-QUESTIONS 42).
   **Prepared 2026-11-26:** they go into `golden-base-v2` (`docs/GOLDEN-BASE-V2.md`).
2. Every case runs in one configuration, Config S (Defender off, as for C3 since 2026-11-03), so the before runs can be
   shared: the pipeline needs one parameters hash.
3. The rare-key rule is decided (OPEN-QUESTIONS 43). **Done 2026-11-26:** option (b), the exact test for a key that
   drops to zero (DECISIONS 2026-11-26).
4. K2: whether the value takes effect without a restart is `(unverified)`. Its `-Verify` starts one process and reads
   its 4688; if the command line is still there, the harness voids the run.
   **2026-11-26, Phase A (A5):** seen once: `after:  0` right after the change, with no restart (COMMANDS 2.18). D3's
   trial run tests it again. No expectation changed.

**2026-11-27 (dated line; no expectation changed):** the 5 control runs are done, all valid; **3 runs per phase is
decided**, and item 22's void rule is set (DECISIONS 2026-11-27).

**Run plan (estimate):** 5 control runs, 3 before runs shared by all cases, and 3 after runs for each of C1, C3, C5,
K1, K2 and K3: 26 runs, about 4.3 hours at the spike's 9.8 minutes per run.

---

## 6. Compliance scan, expected before and after (written 2026-11-26, before any scan)

**Scanner:** Wazuh 4.14.7's compliance scan (SCA), file `cis_win11_enterprise.yml`, "CIS Microsoft Windows 11
Enterprise Benchmark v3.0.0". The checks below were read word for word from Wazuh's repository at tag v4.14.7, except
check 26222's condition line, which was not read. **Image:** `golden-base-v2`. **How to scan:**
`docs/GOLDEN-BASE-V2.md`, Phase D.

| State | 26177 WDigest | 26270 LSASS | 26426 NLA | 26148 Audit Logon | 26222 Command line | 26144 Process Creation |
|---|---|---|---|---|---|---|
| Baseline | Failed (`UseLogonCredential = 1`) | Failed (`RunAsPPL = 0`) | Failed (policy value 0) | Passed | Passed | Passed |
| After C1 | **Passed** | Failed | Failed | Passed | Passed | Passed |
| After C3 | Failed | **Failed** (`RunAsPPL = 2`; the check wants 1) | Failed | Passed | Passed | Passed |
| After C5 | Failed | Failed | **Passed** | Passed | Passed | Passed |
| After K1 | Failed | Failed | Failed | **Failed** | Passed | Passed |
| After K2 | Failed | Failed | Failed | Passed | **Failed** | Passed |
| After K3 | Failed | Failed | Failed | Passed | Passed | **Failed** |

**How each prediction was made:** each check's rule text, against the value each state sets.
- 26177 passes when `UseLogonCredential` is missing or 0.
- 26270 passes only when `RunAsPPL` is 1.
- 26426 passes when the policy key or its value is missing, or when the value is 1.
- 26148 needs "Success and Failure", 26144 needs "Success", and 26222 needs the command-line value to be 1.

**What it means:**
- The scan sees C1, C5, K1, K2 and K3.
- It does not see C3, because the lab's stated deviation (value 2) fails the check either way.
- With the old image (`golden-base`, NLA off only at the listener), check 26426 would say Passed before and after C5.
  That is a false pass: the check reads only the policy key, and it counts a missing key as compliant, because Windows
  turns NLA on by default.

`(unverified)` until the scans of `docs/GOLDEN-BASE-V2.md`, Phase D. A different result is reported as found.

**Scan results (dated lines; the table above is not edited):**
- **2026-11-26, Baseline (D1):** 26177 Failed, 26270 Failed, 26426 Failed, 26148 Passed, 26222 Passed, 26144 Passed.
  **As predicted, 6 of 6** (COMMANDS 2.18; export `data\runs\scans-2026-11-26\D1-baseline-checks.csv`). Check 26222's
  condition, read in the export: `all`, so the key, the value and the value 1 must all be present.
- **2026-11-26, After C1 (D2):** 26177 **Passed**, 26270 Failed, 26426 Failed, 26148 Passed, 26222 Passed, 26144
  Passed. **As predicted, 6 of 6**; the totals moved by one check (read from the SIEM archive, COMMANDS 2.18).
- **2026-11-26, After C3 (D2):** 26177 Failed, 26270 **Failed**, 26426 Failed, 26148 Passed, 26222 Passed, 26144
  Passed. **As predicted, 6 of 6**: the totals equal the baseline, so the scan does not see C3. That C3 applied is shown
  by Sysmon 13, `RunAsPPL` set to 2 at 14:18:28 UTC, before the scan.
- **2026-11-26, After C5 (D3, after `trial-C5-1`):** 26177 Failed, 26270 Failed, 26426 **Passed**, 26148 Passed, 26222
  Passed, 26144 Passed. **As predicted, 6 of 6**; one check moved. The no-NLA client was refused (`0xb09`).
- **2026-11-26, After K1 (D3, after `trial-K1-1`):** 26177 Failed, 26270 Failed, 26426 Failed, 26148 **Failed**, 26222
  Passed, 26144 Passed. **As predicted, 6 of 6**; one check moved. In the run: no 4624 and no 4648 key, 4672 unchanged;
  session event 21 at 14:43:56 UTC shows the sign-in worked (section 4).
- **2026-11-26, After K2 (D3, after `trial-K2-1`):** 26177 Failed, 26270 Failed, 26426 Failed, 26148 Passed, 26222
  **Failed**, 26144 Passed. **As predicted, 6 of 6**; one check moved. In the run, the 4688 key had no `CommandLine`
  field (165 events; `trial-C5-1`: 143 with it).
- **2026-11-26, After K3 (D3, after `trial-K3-1`):** 26177 Failed, 26270 Failed, 26426 Failed, 26148 Passed, 26222
  Passed, 26144 **Failed**. **As predicted, 6 of 6**; one check moved. In the run, no 4688 key; Sysmon 1 still present.
- **Summary, 2026-11-26:** 7 states, **42 of 42 results as predicted**. The scan sees C1, C5, K1, K2 and K3, and does
  not see C3, as section 6 says. All read from the SIEM archive, except the baseline, also read from the dashboard
  export (the same results).

---

## 7. Results of the evaluation runs (written after the runs, 2026-11-26/27; nothing above was edited)

**Data:** 26 valid runs on `golden-base-v2`, one parameters hash `9895d0cf...14cd`: 5 control (`eval-ctl-1` to `-5`),
3 before (`eval-pre-1` to `-3`), 3 after per case (`eval-post-<case>-1` to `-3`). **Analysis:** `src/run.py` per case,
analyser `7850847`; output `data\summaries\eval-2026-11-26\<case>\` (report, findings, comparison). COMMANDS 2.19.

**Key level, scored as section 3 says:**

| Case | Expected LOST keys | System: found (LOST or REDUCED) | TP | FP | FN | Plain subtraction: keys that fell | Its FP |
|---|---|---|---|---|---|---|---|
| C1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| C5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K1 | 5 (the 4 `Security-4624` keys, `Security-4648[]`) | the same 5, all LOST | 5 | 0 | 0 | 5 | 0 |
| K2 | 1 (`Security-4688[CommandLine,...]`) | the same, LOST | 1 | 0 | 0 | 2 | 1 |
| K3 | 1 (`Security-4688[CommandLine,...]`) | the same, LOST | 1 | 0 | 0 | 1 | 0 |
| **Total** | **7** | **7** | **7** | **0** | **0** | **8** | **1** |

**System: precision 1.00, recall 1.00, F1 1.00, false-positive rate 0.** Plain subtraction: precision 0.875 (7 of 8),
recall 1.00. Caution for the reading: all 3 before runs fell in the "low" group of the control runs, so in C1 and C5
no key fell at all; plain subtraction had an easy case there.

**Scope of these scores** (added 2026-11-27 after an outside review, WORKLOG 2026-11-27; no number above changed):
- **What they measure:** whether the system finds evidence losses that are known to exist. All 7 expected keys come
  from the three test cases, logging settings turned off on purpose and never called hardening (section 1). K2 and K3
  expect the same key, `Security-4688[CommandLine,NewProcessName,ParentProcessName]`, so the 7 losses are 6 distinct
  keys.
- **What they do not measure:** a recall for blind spots caused by hardening. None of the three hardening changes
  caused one (OPEN-QUESTIONS 38): in C1 and C5 no key fell at all, and C3 is prevention (section 1; OPEN-QUESTIONS 44).
  So C1 and C5 only check that nothing false is reported, and C3 is not scored for recall (section 3).
- **Tested and undecided keys.** "Tested" means classified LOST, REDUCED or UNCHANGED. "Undecided" means INCONCLUSIVE:
  too few events before the change to test, so the key is never counted as safe. No expected key was undecided.
  Counted from the `classification` column of each case's `comparison.csv`:

| Case | Keys | Tested | Undecided (INCONCLUSIVE) | NEW | LOST | REDUCED | UNCHANGED | Expected keys left undecided |
|---|---|---|---|---|---|---|---|---|
| C1 | 35 | 15 | 17 | 3 | 0 | 0 | 15 | none expected |
| C3 | 35 | 15 | 18 | 2 | 0 | 0 | 15 | not scored for recall |
| C5 | 35 | 15 | 17 | 3 | 0 | 0 | 15 | none expected |
| K1 | 36 | 18 | 14 | 4 | 5 | 0 | 13 | 0 of 5 |
| K2 | 36 | 15 | 20 | 1 | 1 | 0 | 14 | 0 of 1 |
| K3 | 36 | 15 | 17 | 4 | 1 | 0 | 14 | 0 of 1 |

- **What the comparison with plain subtraction shows, and what it does not.** Its one false loss is in K2:
  `Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]`, 211 to 209 events over 3 runs each (ratio 0.991).
  The simple rule "a loss must at least halve" also removes it, and all 7 true losses fell to zero. So here the halving
  rule alone gives the same TP 7, FP 0, FN 0 as the full system. Section 3 planned this comparison so that "the noise
  floor's benefit is measured"; this evaluation does not measure it. A run of the analysis without the noise part is
  planned (WORKLOG 2026-11-27, fix 8).

**How the score depends on the test for a key that falls to zero** (added 2026-11-27, fix 2 of the same review, its
point 2; WORKLOG 2026-11-27). The declared test stays the main result: it was fixed before any run (DECISIONS
2026-11-26), and the other four were chosen after the runs. `src/zero_loss_sensitivity.py` first reproduces the official
class, totals and q of every key in all 6 cases. Then it swaps only the test for the keys that fell to zero and redoes
the correction; everything else stays the code's. Output: `data/summaries/eval-2026-11-26/zero-loss-sensitivity.txt`.
Only the 7 expected keys fell to zero, in any case. For a key with `a` events in the 3 before runs and none in the 3
after runs:

| Test | What it assumes | K1 found (of 5) | K2 (of 1) | K3 (of 1) | TP | FP | FN |
|---|---|---|---|---|---|---|---|
| **Declared:** the chance of no event after if the rate stayed at the before rate, `exp(-a)` here (phi was 1 for all 7 keys) | the before rate is known | 5 | 1 | 1 | **7** | **0** | **0** |
| Split of events: the chance that all `a` events fall in the before runs if nothing changed, `(1/2)^a` | events are independent; no rate is assumed | 3 | 1 | 1 | 5 | 0 | 2 |
| The same, with the 5 control runs counted as before runs (8 against 3): `(8/11)^(a + control events)` | also: the control runs are like the before runs | 5 | 1 | 1 | 7 | 0 | 0 |
| Runs with the key (Fisher's exact test on runs, not events): at best `1/C(6,3) = 1/20 = 0.05` | only runs are independent | 0 | 0 | 0 | 0 | 0 | 7 |
| The same, 8 against 3: at best `1/C(11,3) = 1/165 = 0.0061` | also: the control runs are like the before runs | 5 | 0 | 1 | 6 | 0 | 1 |

What this shows, in order:
1. **No test found a false loss:** FP is 0 under all five.
2. **Among the tests that count events, only K1's two sign-in keys change.** They have 6 events each, 2 per run: LOST
   under the declared test (q 0.0089) and with the control runs added (q 0.022), INCONCLUSIVE with 3 against 3
   (q 0.056). The other 5 keys have 9 to 417 events and are LOST under all three.
3. **A test that counts runs finds nothing with 3 runs against 3.** Its best p is 0.05, and the correction over the 15
   to 18 tested keys raises q to 0.13 to 0.75. This is a limit of 3 runs per phase (DECISIONS 2026-11-27), not a
   property of the changes.
4. **The same key can get a different q in two cases.** With 8 against 3, the 4688 key has p 0.0061 in K2 and in K3.
   In K2 no other tested key has a smaller p, so q = 0.0061 × 15 / 1 = 0.091: not LOST. In K3 two other keys rose and
   had smaller p values (`Security-5379[]`, q 0.026, and `Sysmon-10[GrantedAccess=other,SourceImage,TargetImage]`,
   q 0.0048, in `comparison.csv`), so q = 0.0061 × 15 / 3 = 0.030: LOST.
5. **The technique result uses no test.** K1's "no longer detected" list comes from the alerts: the techniques of
   rules that fired at least once before and never after (`report.py`, `coverage_change`).
6. **Found on the way:** under the run tests, keys that fell from 39, 60 or 417 events to none are classed UNCHANGED.
   The reason is a rule in `classify()`: a key with 30 or more events before that falls to zero but fails the
   correction becomes UNCHANGED, not INCONCLUSIVE. UNCHANGED claims that the key survived. No key reached this rule in
   the official analysis. Proposed for fix 4 (WORKLOG 2026-11-27).

**Technique level:** K1 "no longer detected" = **T1021.001, T1078.002, T1550.002, exactly as expected**. C1, C5, K2,
K3: none, as expected. **C3: none, against the expected {T1055}: a miss** (below).

**Field level:** K2 shows **FIELD-LEVEL LOSS, lost field `CommandLine`**, as expected.

**K1's sign-in (section 4):** step `rdp-signin-30s` exit 0 in all 3 K1 runs; `Security-4672[]` UNCHANGED (27.0 to 30.3
per run) while every 4624 key was lost; session event 21 seen in `trial-K1-1` (14:43:56 UTC). So the sign-in worked:
**K1 is a blind spot, as expected.**

**C3, not as expected at the key and technique level (a result, reported as found):**
- The dump was blocked: rules 92403 and 61625 (T1055, level 12) fired in all 8 control and before runs (2 and 1 per
  run) and in none of the 3 C3 runs, as section 1 expects.
- `Sysmon-10` fell from 107.7 to 72.3 per run (rate ratio 0.672, 95% CI 0.566 to 0.798, q = 8.8e-5), but the system
  reports REDUCED only at a ratio of 0.5 or less: "not reported: ratio 0.672 above 0.5". In the spike (trial stimulus,
  no sign-in) it fell from 73.3 to 26.3.
- `Sysmon-8[]` fell from 3 to 1 per run: INCONCLUSIVE (9 before, below 30; not a drop to zero).
- T1055 still counts as detected after C3, through rules 61632 and 61634, which fire in every run.
- So the system says "no blind spot" for C3. The truth, by the rules that stopped, is **prevention** (section 1).
  OPEN-QUESTIONS 44.

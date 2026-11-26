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

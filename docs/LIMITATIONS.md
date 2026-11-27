# Limits of the study, for chapter 3

Written 2026-11-28 (chat 26343d0f). Fix 8 of the 9 fixes after the outside review (WORKLOG 2026-11-27 and 2026-11-28).
Each limit gives the fact, the evidence in this repository, and one sentence the thesis can use. The student writes the
chapter; this file is the checked list to write it from. Every number here comes from an output in the repository.

---

## A. What the evaluation measures

1. **Recall is measured on deliberate logging mistakes, not on hardening.** All 7 expected losses come from the test
   cases K1 to K3, which turn a logging setting off on purpose. None of the three hardening changes caused a blind spot
   (OPEN-QUESTIONS 38). Evidence: EXPECTED-RESULTS section 7, "Scope of these scores". *In the thesis:* "The system found
   every evidence loss we created on purpose; this study had no hardening change that caused one, so it gives no
   measured rate for blind spots caused by hardening."
2. **Every real loss was complete.** The 7 losses (6 distinct keys) all fell to zero. No real loss was partial, so the
   rules for a partial drop were never tested on real data; only made-up partial losses were (D below). *In the
   thesis:* "Every real loss in the evaluation was a complete loss; partial losses were tested only on made-up effects."
3. **Many keys could not be decided.** In each case 14 to 20 of the 35 or 36 event keys are INCONCLUSIVE: too few events
   to test. They are never counted as safe. Evidence: EXPECTED-RESULTS section 7, the table of tested and undecided
   keys. *In the thesis:* "About half the keys in each case had too few events to decide, and the report says so."
4. **The system cannot tell prevention from a blind spot on its own.** When alerts stop, the cause may be lost evidence
   or a blocked attack. C3 was prevention: its dump programs ran but never opened `lsass.exe` (`src/independent_evidence.py`).
   This came from a check outside the system. *In the thesis:* "Whether an attack still worked was checked from the raw
   events, outside the system; the system itself cannot make that call."

## B. The statistics

5. **The result depends on the test for a key that falls to zero.** The declared test finds 7 of 7. Four other tests,
   chosen after the runs, find 7, 6, 5 and 0; none finds a false one. A test that counts runs cannot pass the
   correction with 3 runs against 3: its best p is 1/20. Evidence: `data/summaries/eval-2026-11-26/zero-loss-sensitivity.txt`.
   *In the thesis:* "With only three runs per side, K1's two smallest keys are found by the declared test but not by
   every reasonable test."
6. **What the noise part adds, on this data** (`src/noise_ablation.py`; `data/summaries/eval-2026-11-26/noise-ablation.txt`;
   chosen after the runs). In 70 comparisons of unchanged runs:
   - the halving rule alone gives 62 false findings, and plain subtraction 347;
   - the full system gives 0;
   - plain Poisson statistics without the measured noise give 3, all one key, `Application-1001[]` (6 to 0), which
     appears only in the busier of the two groups the control runs fall into. Its measured dispersion, 1.50, stops it.
   - The noise band (a drop must exceed 3 times the key's CoV) changes nothing in those 70. On made-up partial losses
     to 40 percent, it finds 22 of 30 cut keys, against 25 of 30 without it: it costs a little recall on the noisiest
     keys.

   On the real cases all five ways with or without the noise part give TP 7, FN 0; only plain subtraction has a false
   loss. *In the thesis:* "The statistics remove the false findings; the measured noise removed one more; the noise
   band added nothing measurable on this data and cost some recall on made-up partial drops."
7. **The thresholds.** Changing alpha (0.01, 0.10), the halving ratio (0.3, 0.7), the minimum count (10, 60) or the
   noise sigmas (2, 4) one at a time leaves the score at TP 7, FP 0, FN 0, and the 70 unchanged comparisons at 0 false
   findings. Only a halving ratio of 0.7 would report C3's Sysmon 10 drop (OPEN-QUESTIONS 44). Evidence: the ablation's
   part C. *In the thesis:* "The score did not change under any single threshold change we tried."
8. **Technique-level coverage can hide a rule-level loss.** After C3, T1055 still counts as detected through rules
   61632 and 61634, although its dump-specific rules stopped (OPEN-QUESTIONS 44). *In the thesis:* "A technique can
   lose its most specific rules and still look covered."

## C. The design

9. **Small and single.** One lab: one Windows 11 virtual machine, one Wazuh 4.14.7 SIEM with its shipped rules, one user
   account, one pinned attack list (a Remote Desktop sign-in and three LSASS dump tests), 3 runs per phase, 26 runs in
   one session of about 6 hours (2026-11-26, 17:55 to 23:58 UTC; `data/summaries/eval-2026-11-26/run-times.txt`). *In the thesis:* "The
   results hold for this lab, this rule set and this attack list."
10. **The run order mixes time and change** (the review's point 4). The 3 before runs are shared by all six cases and
    all fell in the quieter of the two groups the control runs showed; the after runs came in case blocks, C1 first and
    K3 last, with no random order and no unchanged runs between them. C3 also restarts the endpoint once more than the
    other cases. So a time or batch effect cannot be separated from a change effect for a partial drop. It cannot
    explain the complete losses: each lost key is lost only in its own case's runs and present in the others. *In the
    thesis:* "The run order was fixed, so a slow drift over those six hours could look like a small change; it could
    not make a key vanish in one case only."
11. **Some rules were set after some data was seen** (`docs/FREEZE-DATES.md`). The test for a key that falls to zero
    was chosen with K1's expected answer in view (a dry run on made-up effects); the void rule was set from the 5
    control runs. The expected outcomes and the scoring were fixed before any of it. *In the thesis:* "The expected
    results were fixed before the runs; one statistical rule was chosen after a dry run that showed K1's answer."
12. **The control runs serve three purposes.** The noise model, the void rule's range, and the 70 comparisons of
    unchanged runs all come from the same 5 runs; 50 of the 70 use a noise model built from the runs being compared.
    *In the thesis:* "The false-finding check reused the control runs; 20 of its 70 comparisons were out of sample."

## D. The evidence and its sources

13. **One sensor.** All evidence, also the evidence that K1's sign-in worked and that C3 blocked the dump, comes from
    the endpoint's own Security and Sysmon logs, through one Wazuh agent. It is independent of the system's findings and
    of the detection rules, not of the sensor. *In the thesis:* "The outside checks used the same logs, read in a
    different way."
14. **The harness writes its own events.** Each guest call logs on as `eli` (OPEN-QUESTIONS 26), so every window holds
    the harness's own logons; they are the same in every run (the guest calls are counted). *In the thesis:* "The
    measuring tool's own logons are in the data, equally in every run."
15. **What can be reproduced from the repository.** The 26 runs record no code version (`docs/FREEZE-DATES.md` section
    5). The rule export and the Sysmon config are checked against their files; the fence program and the Atomic Red
    Team commits cannot be checked from the repository (DECISIONS 2026-11-28). *In the thesis:* "The capture code of
    the 26 runs is known from commit times, not from the runs themselves."
16. **The lab is not production.** Defender is off in every run (Config S, DECISIONS 2026-11-03). C1 is checked only
    through the Remote Desktop sign-in: rule 60118 needs a console sign-in, which the runs do not make (DECISIONS
    2026-11-18). C5 uses the default client, and its predicted effect was not seen (DECISIONS 2026-11-13).
    *In the thesis:* "Some checks of a change rest on one way of signing in, the one the runs use."
17. **Not built or not done.** The graphical interface and the percentage are not built; the evaluation by security
    engineers (ISO/IEC 25010) has not started (STATUS). *In the thesis:* state what is built, and plan the rest.

---

**Where this list came from:** the outside review's 14 points (WORKLOG 2026-11-27) and the checks of fixes 1 to 8.
Fix 9 (the figures, 2026-11-28) adds no limit. The new activity diagram draws the window and the percentage as design;
limit 17 already says they are not built.

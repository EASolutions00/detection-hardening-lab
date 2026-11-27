# Freeze dates: what was fixed before the evaluation data, and what came after

Written 2026-11-28 (chat 26343d0f). Fix 5 of the 9 fixes after the outside review (point 11; WORKLOG 2026-11-27 and
2026-11-28).

**Why this file exists.** `docs/EXPECTED-RESULTS.md` says that its first commit date proves each expectation came
before its data. That holds for the expected outcomes and the scoring. It does not hold for every rule of the
evaluation. The rule for a key that falls to zero was chosen after a dry run that showed the expected K1 answer. The
void rule was decided after the five control runs, and the count of 3 runs per phase, planned in advance as an
estimate, was confirmed after them. This file gives each kind of rule its own date, and says for each one which data
had been seen and which had not.

**The short answer** (all times UTC):

| Kind of rule | Last change before the data | Data it had seen | Data it had not seen |
|---|---|---|---|
| Expected outcomes and scoring | 2026-11-25 19:12 (`420720f`) | the spike, the hand trials, the rule files, a dry run on made-up effects | the 4 trial runs, the 6 scans, all 26 evaluation runs |
| Analysis rules | 2026-11-25 20:06 (`c654440`) | the same, and the dry run's expected K1 answer | the same |
| Capture rules | 2026-11-26 19:29 (`b0c6770`: the void rule), before the first before run | the 5 control runs | the 3 before runs and the 18 after runs |

**How to read it.**
- Git prints commit times in +08:00, the student's clock. They are converted to UTC here, because the run records use
  UTC.
- A commit time proves that the text existed by then. It does not prove that nobody had seen data earlier. The order of
  the data is in each run's own `run_manifest.json`. `data/summaries/eval-2026-11-26/run-times.txt` lists it
  (`tools/run_times.py`), because the run folders are not on GitHub.
- "Made-up effects" means a dry run: real noise from the spike runs, with the effect of each case added by a script
  (`src/known_answer_dryrun.py`). It is not lab evidence.

---

## 1. The data, in order

| Data | Captured (UTC) | What it was used for |
|---|---|---|
| Hand trials of C1, C3 and C5 | 2026-11-12 and 2026-11-13 | The C1, C3 and C5 rows of EXPECTED-RESULTS section 1: confirmations, not blind predictions |
| The spike: 19 runs, and `test-pre-1` | 2026-11-16, 07:32 to 12:19 | Time per run, noise, the C3 effect, the noise of the dry run. A different stimulus, so a different hash: never compared with the evaluation |
| 4 trial runs (`trial-C5-1`, `trial-K1-1`, `trial-K2-1`, `trial-K3-1`) | 2026-11-26, 14:25 to 15:25 | One C5, K1, K2 and K3 effect each, seen before the evaluation. Same parameters hash as the evaluation. Not evaluation data |
| 6 compliance scans (Phase D) | 2026-11-26, from 14:10; Phase D passed at 15:29 | 42 of 42 results as written in EXPECTED-RESULTS section 6 |
| **5 control runs** | 2026-11-26, 17:55 to 18:49 | The noise model, the void rule's range, and the decision of 3 runs per phase |
| 3 before runs | 2026-11-26, 19:39 to 20:19 | The baseline of all six cases |
| 18 after runs, 3 per case, in the order C1, C3, C5, K1, K2, K3 | 2026-11-26, 20:21 to 23:58 | The results |

## 2. Expected outcomes and scoring

| What | Frozen at | Where | Data seen | Data not seen |
|---|---|---|---|---|
| The expected result of each case. K1 to K3 are new; the C1, C3 and C5 rows were already measured | 2026-11-25 19:12 (`420720f`) | EXPECTED-RESULTS section 1 | The spike, the hand trials, Microsoft's audit documentation, the rule files, the dry run | The trials, the scans, the evaluation runs |
| How the results are scored: the unit (the event key), the expected keys by event ID and field, TP, FP and FN, the technique level, the field level, C3 not scored for recall | Same commit | EXPECTED-RESULTS section 3 | Same | Same |
| The scan predictions | 2026-11-26 04:53 (`bfdad21`), before any scan | EXPECTED-RESULTS section 6 | Same, and the SCA check texts | The scans |

Later lines in EXPECTED-RESULTS are dated and appended. No expectation was edited after its runs existed.

## 3. Analysis rules

| Rule | Frozen at | Where | Data seen | Data not seen |
|---|---|---|---|---|
| Alpha 0.05; REDUCED needs a ratio of 0.5 or less and a drop above 3 times the key's CoV; Benjamini-Hochberg correction; a minimum of 30 events before a key is tested (since 2026-11-25 for a partial drop only: see the last row) | 2026-08-31 (`78f41f4`) | `src/telos/differential.py` | None: no lab data existed | Everything |
| The event key; the whole-profile chi-square as a summary only; a key never seen in the control runs is not tested | 2026-09-04 to 2026-09-29 (DECISIONS; OPEN-QUESTIONS 29) | `eventkey.py`, `differential.py` | None | Everything |
| The impact ranking by three measured numbers; coverage counts alerts that did fire | 2026-11-13 (DECISIONS) | `impact.py` | The hand trials | The spike and later |
| Myers' algorithm as step 3 of the pipeline. It reports edits and classifies no key | 2026-11-25 16:51 (`e6b9235`) | `myers.py` | The spike | The trials and later |
| **A key that falls to zero is tested exactly at any count.** A rare one that fails the correction is INCONCLUSIVE | **2026-11-25 20:06 (`c654440`)** | DECISIONS 2026-11-26; OPEN-QUESTIONS 43 | The spike (C3's `Sysmon-8[]` became LOST) and **the dry run, where K1's two sign-in keys were INCONCLUSIVE under the old rule** | The trials, the scans, the evaluation runs |

The last row is the one to state plainly. The student chose this rule knowing what the dry run said about K1's expected
keys. It was made on made-up effects and the spike, before any evaluation run, but K1's key-level result is not a blind
test of it. Fix 2 shows how much K1's score depends on the choice (EXPECTED-RESULTS section 7).

**No analysis code changed between that rule and the official analysis.** `git diff --stat c654440 7850847 -- src lab`
lists only the capture code (`capture.py`, `evaluate.py`, `catalog.py`, `evaluation.py`, `harness.py`) and guest scripts.
No file of `src/telos` that classifies or reports (`differential.py`, `variance.py`, `pipeline.py`, `report.py`,
`impact.py`) is in the list. Between `7850847`, the commit named as "analyser version" in the official reports, and
the results commit `4198e38`, no file under `src` changed.

**Changed after the results** (none changed a result):

| What | When | Effect |
|---|---|---|
| Scope of the claims (fix 1) | 2026-11-27 12:11 (`8bcce09`) | Documents only |
| Four other tests for a key that falls to zero, chosen after the runs (fix 2) | 2026-11-27 12:30 (`8943024`) | A check. The declared test stays the main result |
| Evidence from the raw events (fix 3) | 2026-11-27 14:47 (`5ba66bb`) | A check. No verdict changed |
| The verdict's wording; seen versus potential techniques; a failed complete loss is INCONCLUSIVE at any count (fix 4) | 2026-11-27 15:08 (`eeee1a1`) | The 6 `comparison.csv` files are identical to the official ones (SHA256) |

## 4. Capture rules

| Rule | Frozen at | Where | Data seen | Data not seen |
|---|---|---|---|---|
| A capture window has a fixed length | 2026-11-13 | DECISIONS 2026-11-13 | The LSASS trial | The spike and later |
| The pinned attack list: a 30 s Remote Desktop sign-in, then LSASS tests 1, 2 and 13 | 2026-11-18 12:12 (`3b6303d`) | DECISIONS 2026-11-18 | The spike; the sign-in by hand | The trials and later |
| Window 180 s, settle 180 s, drain 120 s | Not recorded in one place `(unverified)`. Set after the spike measured the time per run. The dry run of 2026-11-25 already used 180 s | Hashed in every run's parameters | The spike | The evaluation |
| The image `golden-base-v2` | Taken 2026-11-26 13:31:48 | COMMANDS 2.18 | The spike; Phase A and B checks | The trials, the scans, the evaluation |
| The harness's wait for VMware Tools | 2026-11-26 17:53 (`d16d3bf`), 2 minutes before `eval-ctl-1` started | DECISIONS 2026-11-27 | Two stopped starts of `eval-ctl-1`, with no data | All evaluation data |
| 3 runs per phase: 5 control, 3 before shared by all cases, 3 after per case | **Planned 2026-11-25 19:12 (`420720f`), as an estimate. Confirmed about 2026-11-26 19:20**, after the controls | EXPECTED-RESULTS section 5; DECISIONS 2026-11-27 | The 5 control runs and the 70 comparisons of control runs against control runs, which gave the reason | All 21 before and after runs |
| **The void rule** (Sysmon 1 fingerprint from 79.8 to 141.8; `rdp-signin-30s` must exit 0) | **Decided about 2026-11-26 19:20; built into the harness at 19:29 (`b0c6770`); the first before run started at 19:39** | DECISIONS 2026-11-27 | **The 5 control runs**: their fingerprints give the range | All 21 before and after runs |

The last row is the second one to state plainly. The five control runs had been captured before the rule existed, so no
rule was applied to them. The range is computed from them, so they are inside it by construction. The rule voided none
of the 21 later runs. No run that produced data was left out of the 26.

## 5. Which code captured the runs

The run records do not name the code. Since fix 6 of the review (2026-11-28) they do, for new runs only. For the 26
evaluation runs, the only evidence is commit times against run start times. The guest change scripts are the exception:
each after run records its change script's SHA256 (`change_script_sha256`).

| Runs | Started (UTC) | Capture code, by commit time |
|---|---|---|
| `eval-ctl-1` to `-5` | 17:55 to 18:41 | `d16d3bf` (17:53): the harness's wait for VMware Tools. No void rule yet |
| `eval-pre-1` to `-3`, `eval-post-C1-1` | 19:39 to 20:21 | `b0c6770` (19:29): the void rule, in `harness.py`, `catalog.py` and `capture.py` |
| `eval-post-C1-2` (by hand) | 20:42 | COMMANDS 2.19 names code `b3c3bca`, committed at 20:47, after this run began. The working tree at 20:42 is not proven equal to that commit |
| `eval-post-C1-3` on (the batch) | 20:56 on | `b3c3bca` (20:47): `src/evaluate.py` and `src/telos/evaluation.py` added, `capture.py` rewritten to use `lab_config()`. Its settings give the same hash, `9895d0cf` |

## 6. What was decided after seeing data

1. **The void rule**, after the five control runs; and the count of 3 runs per phase, confirmed after them (it was
   planned in advance as an estimate, section 4).
2. **After `eval-pre-3`** (20:19), it was seen that all 3 before runs fell in the quieter of the two groups the control
   runs showed (COMMANDS 2.19). The plan was not changed. This is why plain subtraction had an easy case in C1 and C5.
3. **After the results**, fixes 1 to 4 (section 3) and fixes 5 to 9. The official output stays in
   `data/summaries/eval-2026-11-26/` (analyser `7850847`). Fix 4's re-run is in `eval-2026-11-26-fix4/`.
4. **The ablation of fix 8** is a new analysis chosen after the runs. It is labelled so where it is reported.

## 7. What this proves, and what it does not

**It proves:**
- The expected outcomes and the scoring were in git before any trial, scan or evaluation run.
- Every threshold of the analysis was in git before any lab data. The one rule added later, the exact test for a key
  that falls to zero, was committed before any trial, scan or evaluation run.
- No analysis code changed between that rule and the official analysis, and none between the official analysis and the
  recorded results.

**It does not prove:**
- That the rule for a key that falls to zero was chosen without the expected K1 answer. It was chosen with it.
- That the run count was fixed before the noise was seen. It was planned in advance as an estimate, and confirmed after
  the control runs. The void rule was set after them.
- That each run's capture code equals its commit. The runs did not record it (section 5).
- That nobody had seen data before a commit time. The commit time proves only that the text existed.

## 8. How to check

| Command (in `E:\Claude general`) | Correct result |
|---|---|
| `git show -s --format="%h %ad" --date=iso-strict 420720f` | `420720f 2026-11-26T03:12:53+08:00` |
| `git diff --stat c654440 7850847 -- src` | Only `src/capture.py`, `src/evaluate.py`, `src/telos/catalog.py`, `src/telos/evaluation.py` and `src/telos/harness.py` |
| `git diff --stat 7850847 4198e38 -- src` | No output |
| `.venv\Scripts\python.exe tools\run_times.py` | Needs the run folders. The saved output is `data/summaries/eval-2026-11-26/run-times.txt` |

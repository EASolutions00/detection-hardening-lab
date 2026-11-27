# src - the analyser

Python. The analysis core and the capture harness are written, tested, and used on the real lab:
all 26 evaluation runs of 2026-11-26 and 2026-11-27 went through them (`docs/EXPECTED-RESULTS.md`
section 7).

## What it produces

This is the actual output of `src/demo.py`, the part that matters. One hardening change
was simulated. One event key was removed outright, one lost a field while the event kept
firing, one was genuinely cut to 29 percent, and seven quiet keys drifted on their own.

```
STAGE D  proposed method versus naive differencing
==============================================================================

  ground truth (keys the change really removed or reduced): 3

  method                       TP   FP   FN  precision   recall      F1
  -------------------------- ---- ---- ---- ---------- -------- -------
  naive differencing            3    7    0     30.0%  100.0%   0.462
  proposed system               3    0    0    100.0%  100.0%   1.000

  false alarms raised by the naive method only (7):
    Security-5156[Application,DestPort] fell 4.33%, which is inside its own noise
    Sysmon-11[Image]                   fell 1.88%, which is inside its own noise
    Sysmon-13[Image]                   fell 2.07%, which is inside its own noise
    Sysmon-1[Image]                    fell 0.21%, which is inside its own noise
    Sysmon-22[Image]                   fell 0.16%, which is inside its own noise
    Sysmon-25[Image]                   fell 2.77%, which is inside its own noise
    Sysmon-3[Image]                    fell 0.81%, which is inside its own noise
```

Both methods found all three real losses. The difference is the seven false alarms. Each is
an event key that moved on its own, within the range it was already measured to move in. An
engineer comparing raw counts would investigate every one of them.

The demo is deterministic. `demo_scenario(seed=7)` fixes the generator, so these numbers
reproduce exactly on any machine.

Full output: [docs/demo-output.txt](../docs/demo-output.txt)

**These numbers are synthetic.** They demonstrate that the code works. They are not
measurements and are not a result of the study.

## Run it

```
.venv/Scripts/python.exe src/demo.py
.venv/Scripts/python.exe -m pytest tests -v
```

The demo runs end to end on synthetic counts. It needs no lab, no Wazuh, and no VMs,
because the analyser consumes event counts and does not care where they came from.

## What is built

| Stage | Module | Status |
|---|---|---|
| 1. Acquisition: reading the archive into counts per window | `archive.py` | done 2026-11-13; checked on real windows |
| 1. Acquisition: snapshots, stimulus, export (the harness) | `harness.py` | written 2026-11-13, tested with a fake `vmrun`; **first real run 2026-11-16** (`test-pre-1`, valid after one reader fix, COMMANDS 2.17); then the spike's 19 runs (2026-11-16) and the evaluation's 26 (2026-11-26 to 2026-11-27), all valid |
| 2. Event keying | `eventkey.py` | done; value classes for `GrantedAccess`, `LogonType` and `AuthenticationPackageName` since 2026-11-03 (`VALUE_KEYED_FIELDS`) |
| 3. Myers' difference algorithm | `myers.py` | done 2026-11-26: step 3 of the pipeline, each phase's runs joined into one sorted list; D for every pair of single runs as context (DECISIONS 2026-11-26) |
| 2. Profiling and variance model | `variance.py` | done |
| 3. Differential analysis | `differential.py` | done |
| 4. Rule-to-key index (which Wazuh rules read a key) | `index.py` | done 2026-11-13; checked on the real rule export |
| 4. Impact ranking (blind techniques, highest severity, number of rules) | `impact.py` | done 2026-11-13; surviving coverage counts rules that did fire after the change (DECISIONS 2026-11-13) |
| 5. Reporting | `report.py` | text sections: verdict, telemetry comparison, ranked blind spots with remediation level 1, coverage change, evaluation (2026-11-13). Exports: JSON of findings, CSV of the comparison. **Added later 2026-11-13:** the reproducibility record (parameters and hash, analyser version = git commit, every run and its folder) and the ATT&CK Navigator layer (format 4.5, checked against MITRE's specification) and remediation level 2 (curated list `lab/knowledge/compensating-controls.json`, matched by change and blind technique; two first entries from lab measurements, not tested). All seven of FINAL's sections and four exports now exist |
| Lab catalogue and capture command | `catalog.py`, command `src/capture.py` | done 2026-11-16: the changes C1, C3, C5 (scripts in `C:\telos\`, `-Verify`, script SHA256), Config S after every boot, the trial stimulus (T1003.001 tests 1, 2, 13 last, cleanup), the pinned parameters; `capture.py` runs one window on the real lab. **The student runs it**. **2026-11-18:** the pinned attack list, `pinned_stimulus()` (the Remote Desktop sign-in from the host, then the trial's tests), is `capture.py`'s default (DECISIONS 2026-11-18) |
| Spike plan and batch runner | `spike.py`, command `src/spike.py` | done 2026-11-16: 19 runs (runbook Phase 7), resumable; the harness gained `extra_reboot` (Q6) and each run's start, end and duration (Q2). `analyse_spike()` and `src/spike.py --analyse` answer Q1 to Q6 and run the C3 comparison, writing `data/summaries/cov_control_runs.csv`, `run_timings.csv` and `spike_answers.txt` |
| Pipeline: run folders to report and exports | `pipeline.py`, command `src/run.py` | done 2026-11-13: checks the runs belong together (one parameters hash, one change, at least 3 valid runs per phase, voided runs left out), runs the whole method, writes `report.txt`, `findings.json`, `comparison.csv`, `navigator_layer.json` |
| Run checks, item 22's void rule | `harness.RunChecks`, `catalog.RUN_CHECKS` | done 2026-11-27: a run is voided when its Sysmon 1 count is outside the control runs' mean ± 3 sd (79.8 to 141.8) or `rdp-signin-30s` did not exit 0 (DECISIONS 2026-11-27) |
| Evaluation batch | `evaluation.py`, command `src/evaluate.py` | done 2026-11-27: the 26 runs of the plan in order, unattended; runs already on disk are skipped, so it resumes after a stop |
| Dry run of the test cases | `src/known_answer_dryrun.py` | done 2026-11-26: the pipeline on real spike noise with synthetic effects; checks `docs/EXPECTED-RESULTS.md` against the code; not lab evidence |
| Baseline for comparison | `baseline.py` | done |
| Data shapes | `model.py` | done |
| Synthetic data for testing | `synth.py` | done |

## The method, in the order it runs

`pipeline.compare` first checks the runs (valid runs only, at least 3 per phase, one parameters hash,
one change), then runs **Myers' difference algorithm** (`myers.py`, step 3 since 2026-11-26) on the
sorted event lists, each phase's runs joined into one list. Myers lists every difference, noise
included; on sorted lists it equals subtracting the counts per key, and the module checks this on
every run. The steps below then decide which differences are larger than the noise.

1. **Noise floor** (`variance.py`). From the control runs, measure each event key's
   coefficient of variation and dispersion. Once per environment.
2. **Capture check, then a whole-profile summary** (`differential.capture_problem`,
   `differential.global_gate`). A repetition that recorded no events at all makes the run
   NOT_TESTABLE. Otherwise one chi-square over the whole profile: did anything change at
   all? **Reported, never a filter, since 2026-09-28**: among 299 steady keys, one key that
   fell from 198 events to 0 gave p = 0.999, and the old code then tested no key at all. A
   profile with a single key skips the chi-square.
3. **Per-key rate ratio, every key** (`differential._test_key`). Quasi-Poisson, using the
   measured dispersion rather than assuming variance equals mean. A key the control runs never
   saw (`VarianceModel.measured()` is false) has no noise measurement and is INCONCLUSIVE.
   The profile outcome follows from the keys: CHANGED if any key is LOST or REDUCED, else
   UNCHANGED, or NOT_TESTABLE if no key had enough events to test.
4. **Correction** (`differential.classify`). Benjamini-Hochberg across all tested keys.
5. **Classification.** LOST, REDUCED, UNCHANGED, NEW, or INCONCLUSIVE.

## Design choices worth defending

**A failed capture is NOT_TESTABLE, never a finding.** Until 2026-09-14 an agent that sent
nothing after the change passed the gate, and every key with enough events before was
reported LOST. A dead agent looked like a hardening change that blinded detections, which
is the exact error this thesis exists to catch. "This change was safe" and "this run could
not be tested" are opposite claims, so they are now separate outcomes.

**Chi-square runs once, globally, and is only reported.** Per event type it fails twice:
expected counts for rare events break the approximation, and the p value duplicates what the
rate ratio already gives. Applied once it answers a question nothing else answers. It is not a
gate, because a gate hides the usual shape of a blind spot, one key among many
(`docs/DECISIONS.md` 2026-09-28). Benjamini-Hochberg is what holds false findings down.

**The rate ratio is dispersion-aware, not Poisson.** Poisson assumes variance equals
mean. The study measures variance from the control runs, so using a test that assumes
it away would be inconsistent. Dispersion is floored at 1.0: with only 5 control runs
the estimate is itself uncertain, and understating it would manufacture significance.
The unfloored coefficient of variation is still used for the effect-size guard.

**REDUCED needs three conditions together**: the corrected q value, the effect size
(the rate must at least halve), and the measured noise floor (the drop must exceed
three times that type's own coefficient of variation). Requiring all three is the
point of the method. A p value alone flags event types whose ordinary swing is larger
than the drop being reported.

**INCONCLUSIVE is reported, not folded into UNCHANGED.** An event type seen too few
times cannot be tested. Calling it unchanged would claim it survived, which the data
does not support, and would inflate the reported recall. The exception is a key that
disappears completely: it gets the exact test whatever its count (DECISIONS 2026-11-26).

## Tests

**170 tests** (2026-11-27), in 12 files under `tests/`: `test_differential.py`, `test_eventkey.py`,
`test_archive.py`, `test_index.py`, `test_impact.py`, `test_report_sections.py`, `test_harness.py`,
`test_pipeline.py`, `test_catalog.py`, `test_spike.py`, `test_myers.py` and `test_evaluation.py`.
The count grew from 58 (2026-10-15) to 118 (2026-11-13), 143 (2026-11-18), 150 with Myers
(2026-11-26), 160 with the harness's wait for VMware Tools, 165 with item 22's void rule, and 170 with
the evaluation batch (all 2026-11-27). WORKLOG has each step.
The three that matter most:

- `test_drop_inside_the_noise_band_is_not_reported`
- `test_same_drop_on_a_stable_key_is_reported`

Together those two are the whole statistical argument: the same percentage fall means
different things for different event keys, and only a measured noise floor tells them
apart.

- `test_field_loss_is_invisible_to_event_type_keying`

That one demonstrates the failure the composite key exists to prevent. **It must not be
deleted.** If it goes, the reason for the key format goes with it.

`test_phase_that_emitted_nothing_does_not_crash` is a regression test for a real bug
found by the suite: an all-zero post-change phase used to raise from `chi2_contingency`.

## The unit of analysis, decided 2026-09-04

An analysis key is the event type **plus which tracked fields were populated**, written
`Security-4688[CommandLine,NewProcessName]`. See `eventkey.py` and the decision entry in
`docs/DECISIONS.md`. The lab endpoint audits process creation with the command line since 2026-11-03
(`docs/OPEN-QUESTIONS.md` item 20), and both golden snapshots keep it on. Test case K2 turns the command
line off, and the evaluation found exactly this signature (`docs/EXPECTED-RESULTS.md` section 7).

Keying on the event type alone cannot see a field-level loss. Emptying CommandLine leaves
4688 firing at its former rate, so the profile reports UNCHANGED while every rule matching
on CommandLine is blind. Under the composite key the same change produces a LOST key and a
NEW key at the same rate, which is the signature of a stripped field.

**The honest limit, in the code today.** For most fields the key records *that* a tracked field
carried a value, never *which* value. A change that alters such a field's contents while leaving it
populated moves neither the key nor its rate.

**Value classes, built 2026-11-03** (decided 2026-09-29, `docs/DECISIONS.md`, item 18). For the short
list of fields that detection rules match by specific value, the key also records the value, grouped
into the classes the rules look for, and `other` for every value no rule looks for
(`VALUE_KEYED_FIELDS` in `eventkey.py`). Under Wazuh's shipped rules the list is `GrantedAccess`
(Sysmon 10), and `LogonType` and `AuthenticationPackageName` (4624). Each class holds the rule's own
pattern, so the key and the rule cannot disagree (OPEN-QUESTIONS 35). The `key-values` check in
`tools/check_docs.py` describes this.

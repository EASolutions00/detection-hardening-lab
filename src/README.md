# src - the analyser

Python. The analysis core is written and tested. Acquisition from live VMs is not.

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
| 1. Acquisition (snapshots, stimulus, event retrieval) | not written | **needs the lab** |
| 2. Event keying | `eventkey.py` | done |
| 2. Profiling and variance model | `variance.py` | done |
| 3. Differential analysis | `differential.py` | done |
| 4. Impact scoring and coverage mapping | not written | needs the dependency index |
| 5. Reporting | `report.py` | text only. No CSV, JSON or Navigator export yet |
| Baseline for comparison | `baseline.py` | done |
| Data shapes | `model.py` | done |
| Synthetic data for testing | `synth.py` | done |

## The method, in the order it runs

1. **Noise floor** (`variance.py`). From the control runs, measure each event type's
   coefficient of variation and dispersion. Once per environment.
2. **Global gate** (`differential.global_gate`). One chi-square over the whole profile.
   Did anything change at all? Applied once, not per event type.
3. **Per-type rate ratio** (`differential._test_key`). Quasi-Poisson, using the measured
   dispersion rather than assuming variance equals mean.
4. **Correction** (`differential.classify`). Benjamini-Hochberg across all tested types.
5. **Classification.** LOST, REDUCED, UNCHANGED, NEW, or INCONCLUSIVE.

## Three design choices worth defending

**Chi-square runs once, globally.** Per event type it fails twice: expected counts for
rare events break the approximation, and the p value duplicates what the rate ratio
already gives. Applied once it answers a question nothing else answers.

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
does not support, and would inflate the reported recall.

## Tests

**49 tests**, 20 in `tests/test_differential.py` and 29 in `tests/test_eventkey.py`.
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
`docs/DECISIONS.md`.

Keying on the event type alone cannot see a field-level loss. Emptying CommandLine leaves
4688 firing at its former rate, so the profile reports UNCHANGED while every rule matching
on CommandLine is blind. Under the composite key the same change produces a LOST key and a
NEW key at the same rate, which is the signature of a stripped field.

**The honest limit.** The key records *that* a tracked field carried a value, never *which*
value. A change that alters a field's contents while leaving it populated moves neither the
key nor its rate. Whether a small set of fields should also be keyed by value is
OPEN-QUESTIONS item 18, and one lab capture settles it.

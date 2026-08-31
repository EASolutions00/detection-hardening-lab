# src - the analyser

Python. The analysis core is written and tested. Acquisition from live VMs is not.

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
| 2. Profiling and variance model | `variance.py` | done |
| 3. Differential analysis | `differential.py` | done |
| 4. Impact scoring and coverage mapping | not written | needs the dependency index |
| 5. Reporting | `report.py` | text only, no web interface yet |
| Baseline for comparison | `baseline.py` | done |
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

20 tests in `tests/test_differential.py`. The two that matter most:

- `test_drop_inside_the_noise_band_is_not_reported`
- `test_same_drop_on_a_stable_key_is_reported`

Together they are the whole argument: the same percentage fall means different things
for different event types, and only a measured noise floor tells them apart.

`test_phase_that_emitted_nothing_does_not_crash` is a regression test for a real bug
found by the suite: an all-zero post-change phase used to raise from `chi2_contingency`.

## Not yet decided, and it changes the schema

OPEN-QUESTIONS item 1b: is the unit of analysis the event type alone, or
(event type, required field present)? Removing the CommandLine field from 4688 does not
change the 4688 rate, so field-level losses are invisible to the current design.
**Decide before the acquisition stage is written**, because it changes every stored run.

# lab/scripts - Hardening change scripts

One script per hardening change. These are applied by the harness after reverting to a
config snapshot, and they must be version controlled.

## Why scripts instead of snapshots

Do not create 16 post-change snapshots. Revert to `cfg-suppressed` or `cfg-natural`, then
apply the change by running the script.

Two reasons. The change itself becomes auditable and reproducible, which is what the
proposal's reproducibility claim needs. And 16 branching snapshot delta chains would fill F:.

## Naming

`change-NN-short-name.ps1`, for example `change-01-disable-audit-process-creation.ps1`.
The number matches the catalogue in `../blueprint.md` section 8.

## Every script must carry its source

At the top of each script, in a comment:

```
# Change 01: Disable Audit Process Creation subcategory
# Source: <specific CIS Benchmark or DISA STIG control ID>
# Expected telemetry effect: removes Windows Security EventID 4688
```

The control ID is not optional. T1's proposal states the 16 changes come from CIS Benchmarks
and DISA STIGs. A panelist can ask for the ID of any one of them, and several in the current
catalogue are still generic domain knowledge. See `docs/OPEN-QUESTIONS.md` item 4.

## Expected effect is a prediction, not a fact

Some changes will produce no measurable telemetry change. That is a valid finding and gets
reported, not hidden.

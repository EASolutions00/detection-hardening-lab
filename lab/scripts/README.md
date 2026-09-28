# lab/scripts - Hardening change scripts

One script per hardening change. These are applied by the harness after reverting to a
config snapshot, and they must be version controlled.

## Why scripts instead of snapshots

Do not create 16 post-change snapshots. Revert to `cfg-suppressed` or `cfg-natural`, then
apply the change by running the script.

Two reasons. The change itself becomes auditable and reproducible, which is what the
proposal's reproducibility claim needs. And 16 branching snapshot delta chains would fill F:.

## Naming

`change-ID-short-name.ps1`, for example `change-C1-disable-wdigest.ps1`. The ID matches the
catalogue in `../blueprint.md` section 8 (C1 to C8, B1 to B6). **No change script exists yet.**

## Every script must carry its source

At the top of each script, in a comment. The example uses C1, whose control ID is verified:

```
# Change C1: Disable WDigest (UseLogonCredential = 0)
# Source: DISA V-253358 (Windows 11 STIG)
# Expected telemetry effect: 4624 logon-type distribution shifts (a value change, OPEN-QUESTIONS 18)
```

Write the benchmark name and version beside every CIS number, because the numbering changes
between versions: the LSASS protected-process control is 18.9.25.2 in CIS Windows 11 Enterprise
v2.0.0 and 18.9.27.2 in v5.1.0 (OPEN-QUESTIONS 4 and 18).

This file's example used to be "Disable Audit Process Creation". That change was removed from the
catalogue on 2026-09-08, because CIS requires the setting **on**, so turning it off is de-hardening.

The control ID is not optional. T1's proposal states the 16 changes come from CIS Benchmarks
and DISA STIGs. A panelist can ask for the ID of any one of them, and several in the current
catalogue are still generic domain knowledge. See `docs/OPEN-QUESTIONS.md` item 4.

## Expected effect is a prediction, not a fact

Some changes will produce no measurable telemetry change. That is a valid finding and gets
reported, not hidden.

## `telos-fence.cs` is not a hardening change

It is the capture-window fence required by runbook rule 5 and blueprint run-protocol steps 4
and 7. It lives here because it is lab tooling that must be version controlled, not because it
is a change script.

**What it is.** A program that prints one line and exits. That is all it does, on purpose. Any
extra work would emit extra events.

**What it is for.** Running it creates exactly one process, so Sysmon records exactly one
Event ID 1 whose `CommandLine` carries the run identifier. That marks one boundary of a capture
window **from inside the telemetry**, which is more reliable than host wall-clock time.

**Build it on the host, then copy the binary in.** Do not build it inside the guest, or every
rebuild produces different bytes.

```powershell
Add-Type -TypeDefinition (Get-Content .\telos-fence.cs -Raw) `
         -OutputAssembly .\telos-fence.exe -OutputType ConsoleApplication
```

**Run it the way the harness does**, directly through `vmrun`, never through `cmd` or
`powershell`. Those create their own processes and each one is another Event ID 1.

```
vmrun -T ws -gu eli -gp <pw> runProgramInGuest <vmx> C:\telos\telos-fence.exe START <run-id>
```

**Verified 2026-09-02** on WIN-EP-01: one invocation produced exactly one Sysmon Event ID 1, no
other event ID mentioned the run identifier, `ParentImage` was `vmtoolsd.exe`, and the SHA256
recorded inside the event matched the pinned binary. The pinned hash is in
`docs/DECISIONS.md`.

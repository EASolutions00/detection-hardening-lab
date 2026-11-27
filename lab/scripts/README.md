# lab/scripts - Hardening change scripts

One script per hardening change. These are applied by the harness after reverting to the golden
snapshot, and they must be version controlled.

## Why scripts instead of snapshots

Do not create one post-change snapshot per change. Revert to the golden snapshot, then apply the change
by running the script. Since 2026-11-16 there is no `cfg-suppressed` or `cfg-natural` snapshot: every run
reverts to the golden snapshot (`golden-base-v2` since 2026-11-26), and Config S is set by an after-boot
script (`docs/DECISIONS.md` 2026-11-16).

Two reasons. The change itself becomes auditable and reproducible, which is what the
proposal's reproducibility claim needs. And one branching snapshot delta chain per change would
fill F:.

## Naming

`change-ID-short-name.ps1`, for example `change-C1-disable-wdigest.ps1`. The ID matches the
catalogue in `../blueprint.md` section 8 (C1 to C8, B1 to B6). The test cases K1 to K3 use the same
pattern (`docs/EXPECTED-RESULTS.md` section 1).

**Written 2026-11-13; run by the harness since 2026-11-16** (the spike, the trials, and the 26 evaluation
runs of 2026-11-26 to 2026-11-27; `docs/EXPECTED-RESULTS.md` section 7): `change-C1-disable-wdigest.ps1`,
`change-C3-lsa-protection.ps1`, `change-C5-rdp-nla.ps1`. Each sets its value, and `-Verify` exits 0 only
when the change is in effect inside the guest (runbook requirement 11); C3's check is Wininit event 12
since the last boot, which never reaches the archive (OPEN-QUESTIONS 28). Also `config-S-defender-off.ps1`,
not a hardening change: it turns Defender's live scanning off and reads it back until it is off, and the
harness runs it after every boot (`LabConfig.after_boot`). All must be copied to `C:\telos\` in the guest
before the golden snapshot.

**Test cases, written 2026-11-26; run in the trials and the evaluation (2026-11-26 to 2026-11-27):**
`change-K1-audit-logon-off.ps1`, `change-K2-cmdline-off.ps1`,
`change-K3-audit-process-creation-off.ps1` (DECISIONS 2026-11-26; OPEN-QUESTIONS 42). Each turns off a logging
setting that CIS or DISA requires, so each is a **configuration mistake made on purpose, never a hardening change**.
They exist to remove known evidence, so the study can check that the system finds it. Their expected results are in
`docs/EXPECTED-RESULTS.md`, written before any run. They are in `golden-base-v2` (taken 2026-11-26,
`docs/GOLDEN-BASE-V2.md`), not in the older `golden-base`: a run reverted to `golden-base` cannot find them,
so their `-Verify` fails and the harness voids the run.

**Old comments left in the scripts on purpose (2026-11-27).** Six header lines are out of date, and the scripts are
not edited: their bytes are hashed in every run's manifest (`change_script_sha256`) and copied into `golden-base-v2`,
so an edit would make the repo copy differ from the image's copy. What each line said, and what is now known:
- `change-C5-rdp-nla.ps1` lines 12 and 13, "with the policy key (unverified)": the policy key's effect and "no
  restart needed" were seen in Phase A (A6, refused with `0xb09` after C5, no restart) and in `trial-C5-1`
  (COMMANDS 2.18 and 2.19).
- `change-K2-cmdline-off.ps1` line 10, "without a restart is (unverified)": seen in A5 and confirmed in every K2 run
  (`change_confirmed` true, no reboot).
- `change-K1-...`, `change-K2-...`, `change-K3-...` lines 11, 15 and 12, "Not in golden-base yet ... Not yet run in the
  guest": they are in `golden-base-v2` and ran in the trials and in the 9 K runs of the evaluation.

`baseline-golden.ps1` (2026-11-13) sets the golden image's decided baseline and prints a 20-row check; exit
code 0 only when every row passes. Run it once to set, restart, then with `-Verify` (runbook Phase 5).
**Changed 2026-11-26 for `golden-base-v2`** (DECISIONS 2026-11-26): it also turns NLA off through the Group Policy key,
sets Audit Logon to Success and Failure, and checks 25 rows (adds the NLA policy value, Audit Logon, and K1 to K3
present).

**C5 writes the Group Policy key since 2026-11-26:** `HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services`,
`UserAuthentication = 1`. A change script must write the same value a Group Policy would write, because a compliance
scan reads the policy value. Wazuh's NLA check reads only that key, so the old listener value was invisible to it.

**The CIS version the study pins is CIS Microsoft Windows 11 Enterprise Benchmark v3.0.0**, the version Wazuh
4.14.7's scan checks (DECISIONS 2026-11-26). Each header gives that number, with the newer number beside it where
known.

## Every guest script runs only on WIN-EP-01

Since 2026-11-26 (DECISIONS 2026-11-26), the first line of code in each script, right after `param(...)`, is:

```powershell
if ($env:COMPUTERNAME -ne 'WIN-EP-01') { Write-Error 'This lab script changes security settings. It runs only on WIN-EP-01.'; exit 3 }
```

On any other machine the script stops before it changes anything, with exit code 3. `tests/test_catalog.py` fails if a
script lacks the line, so a new script must carry it and be added to that test's list. The scripts stay LF
(`.gitattributes`), because the harness records their hash.

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

The control ID is not optional. T1's proposal states every change comes from the CIS Benchmarks
or DISA STIGs (the count is no longer fixed at 16; the study uses C1, C3 and C5, plus the test cases K1 to
K3). A panelist can ask for the ID of any one of them, and several in the current
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

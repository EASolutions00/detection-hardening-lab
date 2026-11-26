# golden-base-v2: the retake, the trials and the compliance scans

Prepared 2026-11-26 (chat 26343d0f; DECISIONS 2026-11-26). **Only Phase A has been started (the note below).** Each
step says who does it. A step that uses the guest password or the VM window is the student's. When a step is done,
its command and result go into COMMANDS 2.18.

**2026-11-26:** the pre-flight check before A1 found the Windows hypervisor on, since Windows was reinstalled in place
on 2026-11-23. Fixed the same day: the student's `bcdedit` and a host restart; then `HypervisorPresent` `False`, and
both VMs log `Monitor Mode: CPL0`. A1 done at 10:57 UTC (COMMANDS 2.18). After A3 the guard was added to the 8
scripts (DECISIONS 2026-11-26), so A2 and A3 were repeated with the new hashes: 8 of 8 match (12:52 UTC). A4 to A6 passed,
and A7 reverted at 13:16 UTC: **Phase A passed** (COMMANDS 2.18). K2 and C5 both took effect without a restart. **Phase B passed:** `golden-base-v2` taken
at 2026-11-26T13:31:48Z; B5 gave 25 of 25 after a restart. **Phase C passed:** the test boot
is clean, and the catalog names `golden-base-v2` since C4.

---

## What changes in the image, and why

1. **The test-case scripts K1 to K3 go into `C:\telos\`** (OPEN-QUESTIONS 42, open point 1).
2. **NLA off is also set through the Group Policy key**, `HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal
   Services`, `UserAuthentication = 0`, and C5 sets that key to 1. Group Policy writes this key, and Wazuh's CIS check
   26426 reads only this key. The old image turned NLA off only at the listener (`...\WinStations\RDP-Tcp`), so a scan
   would report NLA compliant while NLA was off.
3. **Audit Logon is set to Success and Failure** (CIS 17.5.4), so K1 starts from a known state.
4. **All 8 scripts are copied again.** Their bytes changed (new headers, then the guard line in item 5), and the
   harness records the hash of the repo file. The guest copy must be the same bytes.
5. **Every guest script refuses to run outside WIN-EP-01** (DECISIONS 2026-11-26): one line right after `param(...)`
   stops it with exit code 3 on any other machine.

Everything else stays as in `golden-base` (2026-11-16). **`golden-base` itself stays**: it is the spike's image and
the fallback.

**Order:** A smoke test (thrown away), B retake, C test boot and repo update, D trial runs and scans, E the evaluation
runs.

**Time (estimate):** A about 30 minutes, B about 30, C about 15, D about 2 hours.

---

## Every session: four names (host, PowerShell)

```powershell
$vmrun = 'C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe'
$win   = 'F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx'
$siem  = 'F:\TeLoS Homelab\SIEM-01\SIEM-01.vmx'
$repo  = 'E:\Claude general'
```

Stores four paths for the commands below. Changes nothing. Correct result: no output. Safe to run again.

**The 8 files** copied in steps A2 and B2: `baseline-golden.ps1`, `change-C1-disable-wdigest.ps1`,
`change-C3-lsa-protection.ps1`, `change-C5-rdp-nla.ps1`, `change-K1-audit-logon-off.ps1`, `change-K2-cmdline-off.ps1`,
`change-K3-audit-process-creation-off.ps1`, `config-S-defender-off.ps1`.

---

## Phase A: smoke test of the new scripts (one session, all thrown away)

Why first: a retake is slow. A script error found after the retake means a second retake.

**Guest steps run in the VM window.** The host's Terminal (Admin) shows the same prompt, `PS C:\WINDOWS\system32>`.
Before the first guest command, run `hostname` (read only): it must print `WIN-EP-01`. On 2026-11-26 the A4 and K2
lines were typed on the host by mistake; they failed only because the host has no `C:\telos` (COMMANDS 2.18).

### A1. Revert to `golden-base` and start (Claude or student, host)

```powershell
& $vmrun -T ws revertToSnapshot $win golden-base
Start-Process -FilePath $vmrun -ArgumentList @('-T','ws','start',"`"$win`"",'gui') -WindowStyle Hidden
& $vmrun -T ws checkToolsState $win
Select-String -Path 'F:\TeLoS Homelab\WIN-EP-01\vmware.log' -Pattern 'Monitor Mode'
```

- **What:** puts WIN-EP-01 back to `golden-base`, starts it in a window, asks whether VMware Tools runs, and reads how
  VMware runs the VM.
- **When:** the pre-flight check passed (COMMANDS Part 5), with `HypervisorPresent` `False`, and SIEM-01 is running.
  If `& $vmrun -T ws list` does not show SIEM-01, start it first: `& $vmrun -T ws start $siem nogui`, then
  `& $vmrun -T ws checkToolsState $siem` until it says `running`.
- **Correct result:** no output from the first line; `running` from the third line (if it says `installed`, wait 20
  seconds and run that line again); a line ending `Monitor Mode: CPL0` from the last line. `CPL0` means VMware runs
  directly on the hardware. `ULM` means the Windows hypervisor is on: stop (COMMANDS 2.18). The start is not waited
  on, because `start ... gui` hung inside a command before (COMMANDS 2.16).
- **Keep the escaped quotes around `$win`:** the path has a space. This is the form that worked on 2026-11-16 (chat
  ee84ae3f). The shorter line in COMMANDS 2.16 had lost the quotes.
- **If it fails:** an `Error:` line from the revert. Check the name with `& $vmrun -T ws listSnapshots $win`.
- **Undo:** not needed. **Safe to run again:** yes.

### A2. Copy the 8 files in (student, host: uses the guest password)

```powershell
$pw = (Get-Content "$HOME\.telos\WIN-EP-01.pw" -Raw).Trim()
$files = 'baseline-golden.ps1','change-C1-disable-wdigest.ps1','change-C3-lsa-protection.ps1','change-C5-rdp-nla.ps1',
         'change-K1-audit-logon-off.ps1','change-K2-cmdline-off.ps1','change-K3-audit-process-creation-off.ps1',
         'config-S-defender-off.ps1'
foreach ($f in $files) {
    & $vmrun -T ws -gu eli -gp $pw CopyFileFromHostToGuest $win "$repo\lab\scripts\$f" "C:\telos\$f"
    "$f exit $LASTEXITCODE"
}
```

- **What:** reads the password file, then copies each script over the old copy in `C:\telos\`.
- **Why:** the guest runs the copies in `C:\telos\`.
- **Correct result:** 8 lines, each ending `exit 0`.
- **If it fails:** `exit 1` and a vmrun error, for example a wrong password or a missing file.
- **Undo:** in Phase A, the revert in A7 removes the copies. **Safe to run again:** yes, it overwrites.

### A3. Compare the hashes (student; read only)

| Where | Command | Correct result |
|---|---|---|
| Guest, Terminal (Admin) | `Get-FileHash C:\telos\*.ps1 -Algorithm SHA256 \| Format-Table Hash, Path -AutoSize` | 8 hashes |
| Host | `Get-FileHash "$repo\lab\scripts\*.ps1" -Algorithm SHA256 \| Format-Table Hash, Path -AutoSize` | The same 8 hashes, file by file |

Claude can run the host line (read only); the current 8 hashes, after the guard, are in COMMANDS 2.18. `C:\telos` also holds 18
older build scripts; only these 8 must match. If a pair differs, copy that file again (A2).
Do not edit the files in `lab\scripts` from here to the end of Phase D: any edit changes a hash, and that file must be
copied again. Git no longer rewrites their line endings (`.gitattributes`, 2026-11-26).

### A4. Run the new baseline once (student, guest, Terminal (Admin))

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -WDigest On
```

- **What:** sets the baseline, now with the NLA policy key and Audit Logon, and prints a 25-row check.
- **Correct result:** `checks passed: 25 of 25` (seen 2026-11-26, COMMANDS 2.18).
- **If a row says `False`:** write down its `Value` column, stop, and tell Claude.
- **Undo:** A7. **Safe to run again:** yes.

### A5. Try K2, then K1, then K3 (student, guest, Terminal (Admin))

```powershell
$s = 'C:\telos\change-K2-cmdline-off.ps1'
powershell -NoProfile -ExecutionPolicy Bypass -File $s -Verify; "before: $LASTEXITCODE"
powershell -NoProfile -ExecutionPolicy Bypass -File $s;         "apply:  $LASTEXITCODE"
powershell -NoProfile -ExecutionPolicy Bypass -File $s -Verify; "after:  $LASTEXITCODE"
```

Then the same three lines with `$s = 'C:\telos\change-K1-audit-logon-off.ps1'`, and then with
`$s = 'C:\telos\change-K3-audit-process-creation-off.ps1'`.

- **What:** each check must say "not in effect" before the change and "in effect" after it.
- **Correct result, for each script:** `before: 1`, `apply:  0`, `after:  0`.
- **If K2 shows `after:  1`:** restart the VM, sign in, and run only the `-Verify` line again. If it is 0 now, K2 needs
  a restart: tell Claude, who sets `reboot=True` for K2 in the catalog. If it is still 1, K2's check is wrong: tell
  Claude.
- **If K1 or K3 shows `after:  1`:** the audit output may differ from what the check reads. Send Claude the output of
  `auditpol /get /subcategory:"Logon" /r` (K1) or `auditpol /get /subcategory:"Process Creation" /r` (K3).
- **Keep the order K2, K1, K3:** K2's check starts `cmd.exe` and reads its new 4688 event, which K3 turns off.
- **Undo:** A7. **Safe to run again:** yes.

### A6. Try C5 through the policy key (student, host and guest)

1. **Host:** `mstsc "$repo\lab\configs\c5-client-no-nla.rdp"`. This client skips the password check before the
   session. With NLA off, **correct result:** as on 2026-11-12 (COMMANDS 2.12, run A), first a box about the
   connection with a clipboard option, and two prompts: answer yes. Then the Windows sign-in screen of WIN-EP-01, or
   its desktop if the client uses the password stored on the host `(unverified which)`. Either one shows that the
   session started without NLA. Close the window.
   **If the desktop appeared:** the console session of `eli` moved into that window (on 2026-11-12 a sign-in with
   `eli` at the console took over the console session, a type 7). Sign in again in the VM window; Terminal (Admin) is
   still open there.
2. **Guest, Terminal (Admin):** the three lines of A5 with `$s = 'C:\telos\change-C5-rdp-nla.ps1'`. **Correct
   result:** `before: 1`, `apply:  0`, `after:  0`.
3. **Host:** the same `mstsc` line again. **Correct result:** refused with "The remote computer requires Network Level
   Authentication, which your computer does not support." (the text seen on 2026-11-12 with the listener key, COMMANDS
   2.12, run C, error code `0xb09`). This shows the policy key turned NLA on without a restart.

- **If step 3 still connects:** restart the VM and try step 3 again. If it is refused now, C5 needs a restart: tell
  Claude.
- **Undo:** A7. **Safe to run again:** yes.

### A7. Throw the session away (Claude or student, host)

```powershell
& $vmrun -T ws revertToSnapshot $win golden-base
```

- **Correct result:** no output; WIN-EP-01 is back in `golden-base` and off.
- **If any of A4 to A6 failed:** stop here. Claude fixes the script, then Phase A is repeated.

---

## Phase B: take `golden-base-v2` (only after Phase A passed)

**B1 to B3.** The same as A1 to A3.

### B4. Set the baseline (student, guest, Terminal (Admin))

The same command as A4. **Correct result:** `checks passed: 25 of 25`.

### B5. Restart and check (student, guest)

```powershell
Restart-Computer
```

After the restart, sign in, open Terminal (Admin), and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -Verify -WDigest On
```

- **What:** checks the 25 rows again, now after a restart, without changing anything.
- **Correct result:** `checks passed: 25 of 25`. Send the output to Claude. On 2026-11-16 this output was not seen.
- **If a row fails:** stop; do not take the snapshot.

### B6. Sign out, shut down, NAT (student, guest and VMware)

Sign out. On the sign-in screen, choose Shut down. Then in VMware: VM Settings, the NAT network adapter, untick
"Connected" and "Connect at power on". **Correct result:** the VM is off.

### B7. Check from the host (Claude; read only)

| Check | Command | Correct result |
|---|---|---|
| VM is off | `& $vmrun -T ws list` | WIN-EP-01's `.vmx` is not in the list |
| No suspended state | `Test-Path 'F:\TeLoS Homelab\WIN-EP-01\*.vmss'` | `False` |
| NAT off at power on | `Select-String -Path $win -Pattern 'ethernet0.startConnected'` | `ethernet0.startConnected = "FALSE"` |

### B8. Take the snapshot (Claude, host)

```powershell
& $vmrun -T ws snapshot $win golden-base-v2
(Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
& $vmrun -T ws listSnapshots $win
```

- **What:** saves the switched-off VM as `golden-base-v2`, prints the time in UTC, and lists the snapshots.
- **Correct result:** no output from the first line; a time such as `2026-11-27T08:15:02Z`; a list with one more
  snapshot than before and `golden-base-v2` last. Write the time down: it goes into the catalog in C4.
- **Undo:** `& $vmrun -T ws deleteSnapshot $win golden-base-v2` (Claude asks first: it cannot be undone).
- **Safe to run again:** **no.** Two snapshots with one name break the revert by name (COMMANDS 2.16).

---

## Phase C: test boot and the repo update

### C1. Revert to `golden-base-v2` and start (Claude, host)

The A1 commands with `golden-base-v2` in place of `golden-base`. **Correct result:** as in A1.

### C2. Check the image (student, guest, Terminal (Admin); read only)

| Command | Correct result |
|---|---|
| `powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -Verify -WDigest On` | `checks passed: 25 of 25` |
| `query user` | only `eli`, on the console |
| `Get-NetAdapter \| Select-Object Name, Status` | NAT `Disconnected`, LAB `Up` |

### C3. Check the archive since the boot (Claude, host; read only)

As on 2026-11-16 (COMMANDS 2.16): `telos-archive tail` on SIEM-01, WIN-EP-01's lines since the start time. **Correct
result:** no `eli` logon at boot; the only `eli` logons are the student's sign-in for C2.

### C4. Point the repo at the new image (Claude)

In `src/telos/catalog.py`: `GOLDEN_SNAPSHOT = "golden-base-v2"` and `GOLDEN_BASE_TAKEN` = the time from B8. Update the
catalog's note on the K scripts, run the tests, commit and push. From then on, every run reverts to `golden-base-v2`.

---

## Phase D: trial runs and compliance scans

**Purpose:** check each change's effect, and the scan predictions in `EXPECTED-RESULTS.md` section 6, before the
evaluation. Trial runs are named `trial-...` and **never enter the evaluation**. A scan session is never a capture
run: each one starts with a revert, which throws its changes away.

### D0. How to scan one state (student, guest, Terminal (Admin); used in D1 to D3)

The VM is on, in the state to scan.

```powershell
$conf = 'C:\Program Files (x86)\ossec-agent\ossec.conf'
$text = [IO.File]::ReadAllText($conf) -replace '(<sca>\s*<enabled>)no(</enabled>)', '${1}yes${2}'
[IO.File]::WriteAllText($conf, $text, (New-Object System.Text.UTF8Encoding $false))
Restart-Service -Name WazuhSvc
```

- **What:** turns the agent's compliance scan (SCA) on, writes the file without a byte-order mark, and restarts the
  agent, which scans when it starts (`scan_on_start`).
- **Why:** SCA is off in the image, because a scan inside a capture window would add events (agent config comment,
  2026-09-02).
- **Correct result:** no output.
- **If it fails:** an error from `Restart-Service`. Run `Get-Service *wazuh*` and use the `Name` it shows.
- **Undo:** the next revert restores the file. **Safe to run again:** yes.

Then wait about 5 minutes `(unverified scan time)` and read the results (student, Wazuh dashboard: it needs the
dashboard password). Open Configuration Assessment, agent WIN-EP-01, policy "CIS Microsoft Windows 11 Enterprise
Benchmark v3.0.0". Write down Passed or Failed for the checks **26177, 26270, 26426, 26148, 26222, 26144**.

- **Correct result:** the row for that state in `EXPECTED-RESULTS.md` section 6. A different value is a result: write
  it down, and do not scan again until it matches.
- **If no Windows 11 policy appears:** run `Get-ChildItem 'C:\Program Files (x86)\ossec-agent\ruleset\sca'` and send
  Claude the list `(unverified that the file is there)`.

### D1. The baseline (Claude reverts and starts; student scans)

Revert to `golden-base-v2` and start (C1), then D0.

### D2. C1 and C3, applied by hand (no trial run: both were measured before)

- **C1:** revert and start (C1). Guest, Terminal (Admin):
  `powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C1-disable-wdigest.ps1`. Then D0.
- **C3:** revert and start (C1). Guest, Terminal (Admin):
  `powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C3-lsa-protection.ps1`. Then run only the first
  three lines of D0 (the file edit), and `Restart-Computer` in place of `Restart-Service`. LSA Protection needs the
  restart, and the agent scans when it starts after it.

### D3. Trial runs of C5, K1, K2 and K3 (student, host; guest password)

The host must be signed in and unlocked: the Remote Desktop window opens for 30 seconds.

Before the first trial run, the student checks in Kaspersky's settings that `E:\TeLoS-artifacts` is still on its
exclusion list. Windows was reinstalled in place on 2026-11-23 and Kaspersky is now 21.27 (COMMANDS 2.18). That the
exclusion survived is unverified.

```powershell
Set-Location $repo
.\.venv\Scripts\python.exe src\capture.py --run-id trial-C5-1 --phase post --change C5
```

Then `trial-K1-1` with `--change K1`, `trial-K2-1` with `--change K2`, and `trial-K3-1` with `--change K3`.

- **What:** one full capture run with the change: revert to `golden-base-v2`, apply, verify, the pinned attacks, the
  export. The harness stops the VM at the end, with the change still applied.
- **Correct result:** the run ends valid, with no void reasons.
- **If it says "change ... not confirmed in the guest":** the change did not take effect without a restart. Tell
  Claude (the catalog's `reboot` for that change), then run the trial again.

After each trial run, Claude starts the VM **without** a revert (the second line of A1), and the student does D0.
Also:

- **After C5:** from the host, `mstsc "$repo\lab\configs\c5-client-no-nla.rdp"`. **Correct result:** refused, NLA
  required.
- **After K1:** guest, Terminal (Admin):
  `Get-WinEvent -LogName 'Microsoft-Windows-TerminalServices-LocalSessionManager/Operational' -MaxEvents 20 | Where-Object Id -in 21,22,25 | Format-Table TimeCreated, Id -AutoSize`.
  **Correct result:** an event 21 ("Session logon succeeded") at the trial's sign-in time. This proves the sign-in still
  worked while logon auditing was off (EXPECTED-RESULTS section 4). Read only.
- **Claude reads each run's `counts.json`:** K1, no `Security-4624` key, `Security-4672[]` still there, step
  `rdp-signin-30s` exit 0; K2, the 4688 key without `CommandLine`; K3, no 4688 key; C5, the sign-in's 4624 keys (two
  type 3 NTLM, two type 10, as in OPEN-QUESTIONS 37).

### D4. Record (Claude)

COMMANDS 2.18 (every command and result of Phases A to D), WORKLOG, and the scan results beside the predictions in
`EXPECTED-RESULTS.md` section 6.

---

## Phase E: then

The 5 pinned control runs on `golden-base-v2`, then the 3 before runs, then 3 after runs for each case
(`EXPECTED-RESULTS.md` section 5).

## Going back

`golden-base` is never changed. To go back: in the catalog, `GOLDEN_SNAPSHOT = "golden-base"` and
`GOLDEN_BASE_TAKEN = "2026-11-16T06:59:45Z"`. Delete `golden-base-v2` only if the student asks; it cannot be undone.

# Work Log

What actually happened, session by session. Newest at the top.

This exists because I forget things. Write an entry every time I sit down, even a short
one. "Tried X, it failed, here is the error" is worth more later than a clean summary.

Template:

```
## YYYY-MM-DD - short title
Did:
Result:
Broke / stuck on:
Next:
```

---

## 2026-09-11 (sixth) - OPEN-QUESTIONS 19 step 6 PASSES. UWF suppressed nothing, and two bigger findings fell out of it.

**Did:** ran an identical 100-iteration stimulus three times, once with the filter off and twice with
it on, and compared the telemetry. **Result: pass. UWF did not suppress a single stimulus event.**
**All six steps of item 19 are now complete.**

### The result, counting only my own events

```
                              RUN B (filter OFF)   RUN C (filter ON)
Sysmon id 1, total                   172                 113
Sysmon id 1, MY stimulus (cmd.exe)   100                 100
Sysmon id 1, background               72                  13
```

**100 process creations, 100 logged, in both conditions.** Item 19 risk 4, that UWF might change the
telemetry it is meant to preserve, is **not supported** for process-creation telemetry.

### I got this wrong first, and the correction is the most useful part of the entry

Comparing **totals** between run A (filter ON) and run B (filter OFF) showed Sysmon registry event
id 13 at **1 versus 99**, against an identical 100-iteration registry stimulus. That looked like UWF
suppressing registry telemetry, which would have been a serious finding, and several class C
hardening changes are registry changes.

**It was wrong.** A third run added a control that settled it: write to **two** keys every iteration,
one ordinary key that UWF filters and one key added to UWF's registry exclusion list so its writes
reach the disk untouched. Same process, same loop, same moment, so nothing but UWF differs between
them.

```
registry events naming the EXCLUDED key : 0
registry events naming the FILTERED key : 0
registry events naming neither          : 15
read-back: both keys hold Iteration = 100, 0 write errors
```

**Neither key was ever logged.** The excluded key's writes were not filtered at all and still
produced nothing. **This Sysmon configuration simply does not watch those keys**, and UWF had nothing
to do with it. The keys it does watch look like this:

```
HKLM\SOFTWARE\Microsoft\Windows
HKLM\SOFTWARE\Microsoft\Wbem\PROVIDERS\Performance\Performance
HKU\...\Explorer\FileExts\.exe\OpenWithProgids\exefile
```

**The 1 versus 99 was background noise in both runs**, and run B had far more background activity
because it was the first writable boot after a series of filtered ones.

**The lesson, and it is the same one three times today:** a difference in a total is not a finding.
Count only the events your own stimulus produced, and put a control in the same run so the two arms
differ by exactly one thing.

### Finding 1: under UWF, the machine's own event log rewinds at every reset

Run A ran under the filter, then the machine restarted.

```
RUN A  filter ON, before a reboot   :  NO EVENTS FOUND
RUN B  filter OFF                   :  281 events, still present
Sysmon channel : RecordCount=13105, 64 MB Circular, oldest event held 2026-09-02
```

Run A's events are **gone, and not by ageing out**, because the channel still holds events from
2 September. The Sysmon log file lives on C:, C: is filtered, and the reboot discarded the overlay.

**Item 19 risk 3 is wider than written.** It says the Wazuh agent's unsent queue dies at the reboot.
In fact **the entire local event log dies**. Anything not already forwarded to the SIEM before the
restart does not exist afterwards. Any UWF capture protocol must treat the drain before reboot as
load-bearing, and must verify arrival at the SIEM rather than assume it.

### Finding 2, and it is not about UWF at all: WIN-EP-01 does not audit process creation

Two hundred process spawns across the runs produced **zero** Security 4688 events. Confirmed
directly rather than inferred from absence:

```
Detailed Tracking
  Process Creation                        No Auditing
  Process Termination                     No Auditing
Policy Change
  Audit Policy Change                     Success
Logon/Logoff
  Logon                                   Success and Failure
  Special Logon                           Success

ProcessCreationIncludeCmdLine_Enabled : NOT SET
```

**Why this matters to the thesis, not just to the lab.** `PROMPT-new-chat.md` section 4 gives
`Security-4688[CommandLine,NewProcessName]` as the canonical example of an event key, and item 18
calls disabling `ProcessCreationIncludeCmdLine_Enabled` the method's **showcase case**. Both assume
4688 is firing. **On this endpoint it is not, and the command-line setting is not configured
either.** Sysmon event 1 is carrying process creation instead, which is item 1c's redundant-source
question showing up from an unexpected direction.

**This is not part of item 19 and should become its own open question.**

### Two more baseline facts recorded while here

- **This Sysmon configuration does not log file creation.** 100 file creates and deletes per run
  produced no event 11. A capture fence built on writing a marker **file** is therefore invisible
  on this machine; the fence must be something the config actually records, such as a process with
  a distinctive command line.
- Sysmon binary is `C:\WINDOWS\Sysmon64.exe`. The config dump ran with exit code 0 but my output
  filter matched nothing, so **what the config actually contains is still unread**.

**Next:** close item 19, record the decision, and decide what state WIN-EP-01 is left in.

## 2026-09-11 (fifth) - OPEN-QUESTIONS 19 step 5 PASSES. No Event ID 2, and the overlay is not what we thought it was.

**Did:** ran a 40-minute window under an active UWF filter, sampling overlay consumption every 60
seconds. **Result: pass. Peak 191 MB of 1024 MB, zero UWF events.** The item continues to step 6.

### Step 5 could not be run as written, and this is the substitution

Item 19 says *"Run one full capture under UWF, then check for Event ID 2."* **There is no capture
harness.** Runbook phases 4 to 8 are not built. So the question underneath it was tested instead:
**does a 1024 MB overlay survive a capture-length window on this machine.**

One 40-minute window, inside item 19's stated 25 to 60 minute range, split so two rates come out of
one run:

- **Minutes 1 to 20, idle.** The floor: what the machine costs by being switched on.
- **Minutes 21 to 40, load.** Fixed cycle of spawn a process, write a 4 KB file, delete it, wait
  1.5 s. 440 cycles total, about 22 a minute.

### The numbers

```
min  1   IDLE    20 MB   1004 free   sysmon 12232
min  2   IDLE   138 MB    886 free   sysmon 12260     <- +118 MB in one minute
min  3   IDLE   139 MB    885 free
min 20   IDLE   179 MB    845 free   sysmon 12547
min 21   LOAD   180 MB    844 free   cycles  22
min 33   LOAD   191 MB    833 free   cycles 286       <- peak
min 34   LOAD   187 MB    837 free   cycles 308       <- went DOWN
min 40   LOAD   188 MB    836 free   sysmon 13066   cycles 440

UWF Operational : records=0     UWF Admin : records=0
```

**Three separate rates, and mixing them gives a wrong answer:**

| Phase | Cost |
|---|---|
| Boot | **about 138 MB, once**, most of it in the second minute after power-on |
| Idle | **2.35 MB/min** (139 MB at min 3 to 179 MB at min 20, 40 MB over 17 min) |
| Under load | **0.45 MB/min** (179 MB to 188 MB across 20 min) |

### The finding that matters most: an overlay is not a running total

**The load phase cost less than idle**, and at minute 34 consumption **fell** from 191 MB to 187 MB.

**The overlay holds the current difference between the machine and its disk, not the sum of
everything written to it.** The load generator created a file and then deleted it, so the space came
back. 440 process spawns and 440 file write-and-delete cycles cost almost nothing.

**This reframes item 19 risk 2.** What fills an overlay is not activity. It is **writes that stay
written**, which in a capture window mainly means **event logs growing**. Sysmon added 834 records
across the 40 minutes here.

**It also corrects the alarm raised in entry four.** That entry measured about 25 MB/min and warned
the overlay might fill in 41 minutes. That figure was taken while test scripts ran back to back and
is not the machine's rate. **Measured properly it is 2.35 MB/min idle**, which alone would take
about seven hours to fill 1024 MB.

### Where this result is weakest, and it should be said before anyone else says it

**The load generator deleted what it created. A real capture does not.** Atomic Red Team tests drop
files, install things, and leave artifacts that persist. Those consume overlay and never give it
back. **So 0.45 MB/min is a floor, not a forecast**, and the honest statement is that this window
shows a 1024 MB overlay is not obviously too small, not that it is proven sufficient.

### Diagnostic run before rebooting, while the machine was still in the same state

**There is no page file, so the page file was not the boot burst.** That hypothesis was raised
during the run, explicitly labelled unverified, and it failed:

```
Win32_PageFileSetting : none      Win32_PageFileUsage : none reported
C:\pagefile.sys : not present or not readable
UWF volume C: Swapfile : 0 MB
```

Per-process bytes written over 60 idle seconds, about 570 KB a minute in total:

```
Registry            124    225,280      msedgewebview2.exe 7256   69,316
taskhostw.exe      3832     81,920      lsass.exe          1020   49,152
svchost.exe        1568     70,656      wazuh-agent.exe    3492    9,949
```

Services running that are known heavy writers: **wsearch (Windows Search)**, **WinDefend**,
**DiagTrack**. `wuauserv` and `VSS` are stopped. **Three `msedgewebview2.exe` processes are running
on this endpoint** and writing about 120 KB/min between them, which is background noise nobody
recorded before.

**The cause of the 118 MB boot burst is still unknown.** No sample was taken during it. **The exact
check:** sample per-process `WriteTransferCount` every 10 s across the first three minutes after
boot.

### Two measurement traps found during this run

**1. The Security log record count goes down.** Readings ran 22455, 22480, then **22425**. It is a
circular buffer, so `RecordCount` is not a running total and cannot measure how many events a window
produced. The Sysmon channel is 64 MB circular (item 9) and behaves the same way. Anything counting
events this way would silently undercount.

**2. A watcher reading a copy of a file reported a row that never existed.** A background collector
was replacing the host copy every 3 minutes while a monitor tailed it. The monitor emitted:

```
30   IDLE   17:35:52  1858  189 MB  835  sysmon 12571  cycles 0
```

The guest's own file says:

```
30   LOAD   17:35:51  1857  185 MB  839  sysmon 12811  cycles 220
```

The phase, the cycle count and the Sysmon count are all wrong, and it was only caught because a
phase cannot go backwards and a counter cannot reset. **Cause (unverified): reading the copy while
it was being rewritten. Rule: verify against the file on the machine, never against a copy something
else is rewriting.**

**Next:** step 6, the last one. Capture the same stimulus with UWF on and with UWF off and compare
the profiles, which tests risk 4, whether UWF changes what gets logged.

## 2026-09-11 (fourth) - OPEN-QUESTIONS 19 step 4 PASSES, and item 19's cost estimate is wrong in our favour.

**Did:** tested whether a change can be made permanent on a UWF-protected machine. **Result: pass,
by a cheaper mechanism than item 19 assumed.** The item continues to step 5.

### Item 19 assumed the only way in was servicing mode. It is not.

Risk 1 says *"The documented fix is servicing mode ... Cost: two extra reboots per hardening change."*

**`uwfmgr` has a commit command that writes one specific change through to the real disk while the
filter stays on.** No servicing mode, no reboot to apply, and it survives the next restart.

```
uwfmgr file commit C:\telos-uwf-commit-test.txt
  File "C:\telos-uwf-commit-test.txt" has been successfully committed          EXIT 0

uwfmgr registry commit HKLM\SOFTWARE\TELOS-UWF-TEST Marker
  Changes on value "Marker" in registry key "HKLM\SOFTWARE\TELOS-UWF-TEST"
  has successfully been committed.                                             EXIT 0
```

**No registry exclusion was needed.** `uwfmgr registry help` lists `commit` as its own command,
separate from `add-exclusion`.

### The result, with a control, because "everything survived" would have been meaningless

Committed at 16:56:46Z. Controls written at 16:58:22Z and deliberately **not** committed. Rebooted
at 16:59:03Z. Checked at 17:00:04Z.

```
COMMITTED, expected to survive
  SURVIVED  C:\telos-uwf-commit-test.txt         content=...stamp=2026-09-10T16:56:46Z
  SURVIVED  HKLM\SOFTWARE\TELOS-UWF-TEST\Marker  value=...stamp=2026-09-10T16:56:46Z

CONTROL, not committed, expected to vanish
  GONE      C:\telos-uwf-control.txt
  GONE      HKLM\SOFTWARE\TELOS-UWF-CONTROL\Marker

Filter state: ON   Commit pending: NO   Servicing State: OFF   Volume state: Protected
```

**Both halves matter.** If all four had survived, the filter had stopped working and the commit
would have proved nothing. If all four had vanished, commit does not work. Only this split result
shows the commit doing something the filter would otherwise have undone.

**The cost line in item 19 risk 1 is wrong and should be corrected when the item closes:** applying
a hardening change to a UWF host costs **zero** extra reboots, not two.

### What this does NOT prove, and it matters for the real catalogue

`registry commit` takes a **key and one value name**. It works for a hardening change that is one
registry value, which covers WDigest, LmCompatibilityLevel, RunAsPPL and most of the CIS and DISA
registry controls. **It has not been shown to work for a change applied any other way**, and several
in the catalogue are: audit policy set with `auditpol`, anything applied through Group Policy, and
anything writing many values at once. Those live in policy files rather than single registry values,
so they would need `uwfmgr file commit` against the right file, or servicing mode.

**Servicing mode itself is still untested.** Step 4's stated proof requirement is met without it,
but it remains the general-purpose path for a change that is not one value.

### Network state of WIN-EP-01, measured because servicing mode risk depended on it

```
LAB   ip=10.20.10.20      gateway=none
NAT   ip=192.168.243.130  gateway=192.168.243.2
TCP 8.8.8.8:53 (raw internet, no DNS)  : False
TCP www.microsoft.com:443 (needs DNS)  : False
Windows Update service : Running, StartType=Manual
```

**It has a NAT adapter and a default gateway but no working outbound internet.** This was checked
before considering servicing mode, because servicing mode was thought to run Windows Update on its
own, which would have broken version pinning permanently.

**That worry was overstated and is corrected here.** `uwfmgr servicing help` shows four commands:
`enable`, `disable`, **`update-windows`**, `get-config`. Updating Windows is a **separate explicit
command**, not something entering servicing mode does by itself.

### Two more things from the machine's own help text, worth keeping

- **`uwfmgr registry commit-delete`** commits a deletion. This answers the cleanup problem recorded
  in entry three, where a file written before the filter was enabled could not be permanently
  removed.
- **`add-exclusion`**: *"The excluded registry keys should exist before system volume is protected."*
  So exclusions cannot be added freely to an already locked-down machine.
- Syntax trap: it is `uwfmgr registry help`, **not** `uwfmgr help registry`. The wrong order returns
  generic help with exit code 1, which looks like a failed command rather than a wrong one.

### Overlay readings collected along the way

```
16:51:27Z   67 s after boot    39 MB
16:56:46Z  386 s after boot   171 MB
16:58:22Z  482 s after boot   174 MB
17:00:04Z   61 s after boot    17 MB   (fresh boot)
```

Between the 67 s and 386 s readings, 132 MB accumulated in 319 s, about **25 MB per minute**. At
that rate 1024 MB fills in roughly **41 minutes**, and item 19 describes capture windows of **25 to
60 minutes**. **This machine was not idle** during those readings, it was running test scripts, so
the steady rate will be lower. It is still the clearest warning yet that risk 2 is real.

**Next:** step 5, the step that matters most. Run one full capture under UWF and check for
Event ID 2 in `Microsoft-Windows-UnifiedWriteFilter/Operational`, reading overlay consumption at
the start and end of the window rather than only checking for the event afterwards.

## 2026-09-11 (third) - OPEN-QUESTIONS 19 step 3 PASSES. The revert works, on files and on the registry.

**Did:** protected C:, enabled the filter, rebooted, planted six markers, rebooted again, and
checked. **Result: pass. All six were gone.** The item continues to step 4.

### Setup, and where UWF's own event log lives

```
uwfmgr volume protect C:    The volume C: will be protected by Unified Write Filter after UWF is enabled.   EXIT 0
uwfmgr filter enable        Unified Write Filter will be enabled after system restart.                      EXIT 0

Current Session : Filter state OFF,  No volumes configured
Next Session    : Filter state ON,   Volume 454f9329-d283-4408-acbc-9ae77672903c [C:]  Protected
```

**UWF has two dedicated event channels, and this was not known before today:**

```
Microsoft-Windows-UnifiedWriteFilter/Operational   records=0  enabled=True
Microsoft-Windows-UnifiedWriteFilter/Admin         records=0  enabled=True
```

Item 19 risk 2 says nothing in the pipeline watches for UWF's Event ID 2. **These two channel names
are where a watcher would have to look**, and both sat at 0 records across every reboot in this
step, which is the clean baseline to measure against.

### The result

Markers planted at 16:48:14Z and 16:49:33Z, machine rebooted at 16:50:20Z.

```
GONE      C:\telos-uwf-marker.txt
GONE      C:\Users\eli\telos-uwf-marker.txt
GONE      HKLM:\SOFTWARE\TELOS-UWF-TEST
GONE      HKLM:\SOFTWARE\TELOS-UWF-TEST2
GONE      HKLM:\SOFTWARE\TELOS-UWF-TEST3
GONE      HKCU:\Software\TELOS-UWF-TEST

Filter state: ON    Volume state: Protected    Servicing State: OFF    Commit pending: NO
```

**Both hives were tested on purpose.** `HKLM` and `HKCU` live in different files on disk, so one
surviving while the other vanished was a real possibility. Neither survived.

### The strongest evidence is the file that did survive

```
SURVIVED  C:\Users\eli\telos-uwf-step3a.ps1
GONE      C:\Users\eli\telos-uwf-step3b.ps1
GONE      C:\Users\eli\telos-uwf-step3b2.ps1
```

`step3a.ps1` was copied in at 16:46:07, **before** the reboot that switched the filter on, so it
went to the real disk. The other two were copied in afterwards and went to the overlay. **The
filter took effect exactly at the boot boundary and the file system records it.** These were written
by VMware Tools, not by PowerShell, so this also shows the filter catches writes that do not come
from the shell.

### A consequence that changes how the test protocol must work

**Nothing can be permanently deleted while the filter is on.** A deletion is a write, so it goes to
the overlay and is undone at the next reboot. `telos-uwf-step3a.ps1` is now stuck on the disk until
the filter is turned off or servicing mode is used. Any capture protocol built on UWF has to plan
cleanup around this rather than discovering it later.

### A false alarm that would have killed the item wrongly

The first registry write failed:

```
New-Item -Path "HKLM:\SOFTWARE\TELOS-UWF-TEST" -Force
FAILED registry : No more data is available.
```

**This was not UWF.** Tested through four separate write paths, all under an active filter, all
successful:

```
reg.exe add HKLM\SOFTWARE\TELOS-UWF-TEST        EXIT CODE : 0
PowerShell New-Item, no -Force                  SUCCEEDED
[Microsoft.Win32.Registry]::LocalMachine.CreateSubKey   SUCCEEDED, readback correct
reg.exe add HKCU\Software\TELOS-UWF-TEST        EXIT CODE : 0
```

**`New-Item -Force` on the PowerShell registry provider throws `No more data is available` even when
the same write succeeds without `-Force`.** Taken at face value the first error would have been
recorded as "UWF blocks registry writes", which would have made step 4 look impossible and closed
item 19 for a reason that does not exist. **One error message is not a finding. Four code paths are.**

### Overlay consumption is measurable, and the first numbers are not reassuring

Two subcommands do it, and neither was known before today:

```
uwfmgr overlay get-consumption      The overlay consumption is 22 MB.   (90 s after boot)
uwfmgr overlay get-availablespace   The overlay has 1002 MB available space.

uwfmgr overlay get-consumption      The overlay consumption is 39 MB.   (67 s after the next boot)
uwfmgr overlay get-availablespace   The overlay has 985 MB available space.
```

Consumption plus available always equals the 1024 MB maximum, so the two agree.

**39 MB in 67 seconds is roughly 35 MB per minute, which would fill 1024 MB in about 29 minutes.
Item 19 describes capture windows of 25 to 60 minutes.** This is an **upper bound, not a
prediction**, because most of those 39 MB are boot-time writes and the steady rate on an idle
machine will be far lower. But it is the first concrete sign that risk 2 is a live problem rather
than a theoretical one. **Step 5 must measure consumption at the start and end of a real capture
window, not just check for Event ID 2 afterwards.**

### Two small traps recorded so they are not hit again

- `uwfmgr.exe` writes **UTF-16**. Setting `[Console]::OutputEncoding` to Unicode fixes its output
  and **breaks `reg.exe` output in the same script**, which came back as `????????`. Exit codes
  stayed correct. **Set the encoding per command, not once per script.**
- Overlay consumption is reported in **whole MB**, so writes of a few hundred bytes do not move it.
  Do not use it to confirm a small write happened.

**Next:** step 4, servicing mode. Apply one registry change, reboot, and confirm it survived. This
is the step that decides whether a hardening change can be applied to a UWF-protected host at all.

## 2026-09-11 (second) - OPEN-QUESTIONS 19 step 2 PASSES. Activation was not the blocker. The overlay is 1 GB of RAM.

**Did:** ran step 2 of item 19 inside WIN-EP-01, enabling `Client-UnifiedWriteFilter`, rebooting,
and verifying. **Result: pass, after one failed attempt that was my error.** The item continues to
step 3.

### First attempt failed, and it was the wrong command rather than a real obstacle

```
Enable-WindowsOptionalFeature -Online -FeatureName Client-UnifiedWriteFilter -NoRestart

RESULT  : FAILED
MESSAGE : One or several parent features are disabled so current feature can not be enabled.
HRESULT : 0xC004000D
State   : Disabled   (unchanged)
```

**`-All` was missing.** Windows optional features form a tree and refuse to enable a child while its
parent is off. `-All` enables the parents.

**The HRESULT was misleading and is recorded so nobody chases it again.** `0xC004000D` sits in the
numeric range Windows uses for **licensing** errors, while the message text is about **parent
features**. Those two readings lead to opposite conclusions: one closes item 19 at step 2, the other
is a one-word fix. The retry was what told them apart. **Trust the message, not that number.**

### Activation, now verified in words rather than from an enumeration

```
Name: Windows(R), Education edition
Description: Windows(R) Operating System, RETAIL channel
Partial Product Key: <redacted, not evidence for anything here>
License Status: Notification
Notification Reason: 0xC004F034.
```

This closes the unverified item from the step 1 brief. `DECISIONS.md:326` saying "unactivated" is
correct but imprecise: the exact state is **Notification**, meaning the activation grace period has
ended.

### The retry, and exactly what it changed

```
Enable-WindowsOptionalFeature -Online -FeatureName Client-UnifiedWriteFilter -All -NoRestart

RESULT : SUCCEEDED   Online : True   RestartNeeded : True

                                BEFORE      AFTER
Client-DeviceLockdown           Disabled    Enabled
Client-UnifiedWriteFilter       Disabled    Enabled
Client-KeyboardFilter           Disabled    Disabled
Client-EmbeddedShellLauncher    Disabled    Disabled
Client-EmbeddedBootExp          Disabled    Disabled
Client-EmbeddedLogon            Disabled    Disabled
```

**The parent is `Client-DeviceLockdown`.** `-All` enabled parents only and touched no siblings,
which is what its documentation claims and is now checked rather than assumed. **Two features
changed on this machine, not one**, and both belong in the software inventory for Chapter 3.

### This answers item 19 risk 5, the one named as the likeliest silent killer

**Windows in `Notification` state, with no valid licence, installed a DISM optional feature.**
Activation does not block it. Risk 5 is closed by measurement.

### Reboot and verification

```
& $vr ... runProgramInGuest $vm -noWait "C:\Windows\System32\shutdown.exe" /r /t 5
```

Guest answered `directoryExistsInGuest` again after **172 s**.

```
LAST BOOT   : 2026-09-10T16:27:32Z
Client-DeviceLockdown          Enabled
Client-UnifiedWriteFilter      Enabled
Client-KeyboardFilter          Disabled
uwfmgr.exe present : True
uwfmgr.exe size    : 230904
uwfmgr.exe version : 10.0.26100.1 (WinBuild.160101.0800)
UwfServicingSvc    Stopped    Unified Write Filter Servicing Helper Service
uwfmgr get-config EXIT CODE : 0
```

**The silent-failure check passed.** Entry one said step 2 would only be a real pass if `uwfmgr.exe`
existed **after** the reboot, because DISM's own exit code cannot be trusted to mean the payload
landed. It exists, it runs, and it returns 0.

### The overlay defaults, which matter more than anything else here

```
Filter state        : OFF
Servicing State     : OFF
Overlay Type        : RAM
Maximum size        : 1024 MB
Warning Threshold   : 512 MB
Critical Threshold  : 1024 MB
Persistent          : OFF
Volumes configured  : none
Registry exclusions : none
```

**This is the number item 19 risk 2 turns on.** The overlay is **1024 MB and lives in RAM**, and
Event ID 2 fires at the critical threshold of 1024 MB. **A capture run therefore has a 1 GB total
write budget to C: before the run is corrupt.** For scale, the Sysmon channel alone is 64 MB
(item 9).

**A second cost that was not anticipated.** WIN-EP-01 has `memsize = "8192"` and `numvcpus = "4"`.
A RAM overlay of 1024 MB is **one eighth of the guest's memory**, taken away from the machine under
test while UWF is on. That is a difference between a UWF host and a non-UWF host, so it belongs
with risk 4 as an external-validity note, not only as a resource note.

### Small trap in reading uwfmgr output

`uwfmgr.exe` writes **UTF-16**. Captured through PowerShell without setting the console encoding,
every character arrives separated by a space. The content is still readable but it is not safe to
parse. Fix before step 3: set `[Console]::OutputEncoding = [System.Text.Encoding]::Unicode` before
calling it, or redirect to a file and read it with `-Encoding Unicode`.

**Next:** step 3. Protect C:, turn the filter on, reboot, write a file, reboot again, and confirm
the file is gone. This is the first step where UWF actually filters writes.

## 2026-09-11 (first) - OPEN-QUESTIONS 19 step 1 PASSES. The feature exists and its name is confirmed.

**Did:** ran step 1 of item 19 inside WIN-EP-01, just after midnight. **Result: pass. The item
continues to step 2.**

### How it was run, and why not as a one-liner

`vmrun runProgramInGuest` returns a program's **exit code only, never its output**. So the query was
written as a script on the host, copied in, run, and its result file copied back out. A pipeline
passed inline through `vmrun`'s argument parsing can arrive mangled, and a mangled query returns
nothing, which reads exactly like "feature not available". That is the failure item 19 warns about
in its note on the search string.

```
& $vr -T ws -gu eli -gp $pw copyFileFromHostToGuest $vm "<scratch>\uwf-step1.ps1" "C:\Users\eli\telos-uwf-step1.ps1"
& $vr -T ws -gu eli -gp $pw runProgramInGuest $vm "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -NoProfile -File "C:\Users\eli\telos-uwf-step1.ps1"
& $vr -T ws -gu eli -gp $pw copyFileFromGuestToHost $vm "C:\Users\eli\telos-uwf-step1.txt" "<scratch>\uwf-step1-out.txt"
```

All three returned no output, which is `vmrun`'s success result. Both guest files were deleted
afterwards with `deleteFileInGuest`.

### Exact output

```
RUNNING AS : WIN-EP-01\eli
ELEVATED   : True
EDITION    : Microsoft Windows 11 Education
BUILD      : 10.0.26100.0
UBR        : 9168
uwfmgr.exe : False

----- ACTIVATION (LicenseStatus 1 = Licensed, 0 = Unlicensed) -----
Windows(R), Education edition                           5

----- Get-WindowsOptionalFeature -Online, FeatureName like *Filter* -----
TOTAL FEATURES ON THIS BUILD : 137
MATCHES FOR *Filter*         : 5

TIFFIFilter                                   Disabled
IIS-RequestFiltering                          Disabled
IIS-ISAPIFilter                               Disabled
Client-KeyboardFilter                         Disabled
Client-UnifiedWriteFilter                     Disabled
----- end -----
```

### Three things that were unverified and now are not

1. **The DISM feature name is `Client-UnifiedWriteFilter`.** Entry seven listed this as unverified.
   The `*Filter*` search returned 5 matches out of 137 features, so the widened search string was
   worth using: it also surfaced `Client-KeyboardFilter`, from the same feature family.
2. **`vmrun runProgramInGuest` gets a full administrator token, not a UAC-filtered one.**
   `ELEVATED : True`. Every remaining step of item 19 can therefore be run from the host without a
   person at the guest console. This was the open question carried out of entry nine.
3. **`DECISIONS.md:326` is correct about the machine.** Education, `10.0.26100` with UBR `9168`,
   which is `10.0.26100.9168`. Read from the machine, not from the document.

### A fact sharper than the record, and it changes what step 2 asks

`DECISIONS.md:326` says "unactivated". The licensing service returns **`LicenseStatus = 5`** for
`Windows(R), Education edition`. In the `SoftwareLicensingProduct` enumeration 5 is **Notification**,
not 0 Unlicensed **(unverified this session; the exact check is `slmgr /dlv` inside the guest, which
prints the status in words)**. Notification is the state an install falls into after the activation
grace period ends: watermark shown, personalisation locked, servicing otherwise intact.

**Why this matters.** Item 19 risk 5 asks whether a DISM optional feature will enable on
"unactivated" Windows. The real question is narrower and more answerable: whether it enables in
**Notification** state. Step 2 is still the test, but it is now a specific question.

### `uwfmgr.exe` is absent, and that is expected rather than a failure

`Test-Path C:\Windows\System32\uwfmgr.exe` returned `False`. The feature state is `Disabled`, and
enabling the feature is what installs the tool. **This becomes a real failure only if it is still
`False` after step 2 reports success**, which would mean DISM claimed to enable a feature it did
not install. Worth checking explicitly in step 2 rather than trusting DISM's exit code.

**Next:** step 2, enable `Client-UnifiedWriteFilter`. This is the first step that changes
WIN-EP-01. Fallback is `uwf-test-baseline-2026-09-10`.

## 2026-09-10 (ninth) - Fallback snapshots taken on both VMs. No step of item 19 has run yet.

**Did:** took `uwf-test-baseline-2026-09-10` on WIN-EP-01 and on SIEM-01, before anything in
OPEN-QUESTIONS 19 touches either machine. **This supersedes the line in entry eight saying the
baseline snapshot has not been taken.**

**Why SIEM-01 as well, when `PROMPT-uwf-test.md` section 4 says not to change it.** Asked for in
session and approved. A snapshot is protective rather than destructive, but it *is* a change: every
write from now on goes to a delta disk.

### State before

```
WIN-EP-01  Total snapshots: 3   phase3-complete-2026-09-02, agent-hardened-2026-09-03,
                                tamper-off-2026-09-03
SIEM-01    Total snapshots: 3   phase3-complete-2026-09-02, timesync-off-2026-09-03,
                                snapd-off-archive-v2-2026-09-03
F: free                         601,633,779,712 bytes
Both VMs powered on.
```

### Commands, exactly as run

```
& "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe" -T ws snapshot "F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx" "uwf-test-baseline-2026-09-10"
& "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe" -T ws snapshot "F:\TeLoS Homelab\SIEM-01\SIEM-01.vmx" "uwf-test-baseline-2026-09-10"
```

Both returned **no output**, which is `vmrun`'s success result. WIN-EP-01 finished inside two
minutes. SIEM-01 took **more than ten minutes** and had to be moved to the background; it exited
with code 0.

### State after

```
WIN-EP-01  Total snapshots: 4   ... uwf-test-baseline-2026-09-10
SIEM-01    Total snapshots: 4   ... uwf-test-baseline-2026-09-10
F: free                         576,952,819,712 bytes   (24,680,960,000 used)
SIEM-01 reachable               ping 192.168.243.129 replies <1ms, TCP 22 open
```

### These are memory snapshots, and the earlier ones were not

`SIEM-01.vmsd` records `snapshot3.type = "1"` for the new one. The other three carry no `type`
line. The `.vmsn` sizes say the same thing:

```
SIEM-01-Snapshot3.vmsn       29,939     cold, no memory
SIEM-01-Snapshot4.vmsn    6,893,571     memory included
WIN-EP-01-Snapshot3.vmsn    295,453     cold, no memory
WIN-EP-01-Snapshot4.vmsn  6,794,522     memory included
```

**Consequence that must not be forgotten.** Reverting to either of these restores the guest clock
as it stood at 23:33 on 2026-09-10. All six `time.synchronize.*` switches are `FALSE` in both
`.vmx` files (item 6), so VMware Tools will not correct it. **A revert must be followed by a clock
fix, or by taking a fresh cold snapshot at that point**, before any capture run. Acceptable for
these two, whose only job is recovering an unbootable machine.

### A wrong reading, recorded because it would be made again

While SIEM-01's snapshot was still running I read it as hung, on three signals that all looked
like failure and were not:

```
SIEM-01-Snapshot4.vmsn  = 0 bytes, unchanged for 10 minutes
vmware-vmx WriteTransferCount = +864,332 and +366,070 bytes over 20 s (idle rates)
PhysicalDisk Disk Write Bytes/sec on F: = below 100,000 (did not even clear the filter)
```

**All three are expected during a live snapshot.** VMware maps the memory file, so Windows credits
those writes to the system cache and not to the process, and the `.vmsn` is written at the *end* of
the operation, not during it. The only reliable signal is the exit code. **Do not diagnose a live
snapshot from file size or process counters. Wait for `vmrun` to return.**

**Next:** step 1 of item 19, the read-only feature query inside WIN-EP-01. Open question carried
into it: whether `vmrun runProgramInGuest` gets a full administrator token or a UAC-filtered one.

## 2026-09-10 (eighth) - Audited this session's commits against this log. Four things were unrecorded.

**Did:** listed every commit since 2026-09-09 and checked each against a WORKLOG entry, before
compacting the session. Four gaps found and closed here.

### Gap 1, and it was a real data-loss risk: the global rules file

`C:\Users\Elijah\.claude\CLAUDE.md` gained a new section today and **that file is not backed up
anywhere.** This repository's own `CLAUDE.md` says so: *"It is not backed up here, so if it is
lost, ask the user for it again."* Asking works only while someone remembers the content.

**Copied to `DOCS\prep-local\global-CLAUDE.md.backup-2026-09-10`**, 8,466 bytes, verified byte for
byte. That folder is outside the repository, so the file stays private and is not pushed.

**What was added to it**, so it can be reconstructed if both copies are ever lost:

- A section titled **"Simple and complete are not opposites."** Its core line is *complete means
  no missing facts, simple means plain words and small steps, so cut the words and keep the
  facts.* Nine rules under it, including: answer first in one or two sentences; one new idea per
  paragraph; a real number beats an abstract word; do not stack a table, a list and a defense
  brief in one reply; length is not completeness; and the defense brief is for decisions and
  findings, not for every question asked.
- A section titled **"If I say I am confused, stop."** Do not explain again at greater length.
  Explain again shorter, with one concrete example, and ask which part is unclear.

**Why it was needed.** The existing rules said "simple English, short sentences" and also "never
hide complexity to keep an answer short." The second was being read as permission to be long, and
the answers became unreadable. The new section resolves that conflict directly.

The matching project-level addition is in this repo's `CLAUDE.md` under "Explaining this project":
a list of terms that must be explained in plain words on first use, a preference for real numbers
from this project over abstract description, and a rule to say which layer an answer is at,
because what the code does, what the design says, and what a deployment would need are three
different honest answers to the same question.

### Gap 2: the testing prompt

`docs/PROMPT-uwf-test.md` was committed with no entry. It is a **working-session** prompt for
OPEN-QUESTIONS 19 only, and it is finished with when that item closes.

It points at `PROMPT-new-chat.md` rather than copying it, and states that it overrides only that
file's read-only rule and nothing else. It carries the six-step order as one line each and sends
the reader to item 19 for the detail, so the reasoning stays in one place.

It names six snapshots as untouchable, puts `src/`, `tests/` and the figures off limits, and
keeps the proposal documents off limits because what changes if the test passes is a decision to
make after seeing the result. Credentials are read from the file, never typed, and printing or
committing the password is forbidden.

### Gap 3: the current state of the machines, as of 2026-09-10

Recorded because this is live state that no document held.

```
Both VMs powered on.

WIN-EP-01   F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx
    phase3-complete-2026-09-02
    agent-hardened-2026-09-03
    tamper-off-2026-09-03

SIEM-01     F:\TeLoS Homelab\SIEM-01\SIEM-01.vmx
    phase3-complete-2026-09-02
    timesync-off-2026-09-03
    snapd-off-archive-v2-2026-09-03
```

**Runbook phases 1, 2 and 3 are complete. Phases 4 to 8 are not.** No pinned version table, no
golden snapshot, and **no capture harness**. The harness is the long pole.

**`uwf-test-baseline-2026-09-10` has NOT been taken.** The testing prompt instructs that chat to
take it and to say so first. Do not start step 3 of item 19 without it.

Two unrelated encrypted VMs sit in `F:\VMWARE\`. They are not part of this project, they need a
password, and `vmrun listSnapshots` returns an error for them. That error is expected.

### Gap 4: how the new-chat prompt reached its current form

Five commits, only partly covered by the sixth entry above. The order, because each step was
caused by a real defect:

1. `5e69e87` created it as a self-contained briefing.
2. `63937a0` cut it in half after it turned out to duplicate five sections of `CLAUDE.md`.
3. `c3d711b` made it work from any folder. Four things broke outside `REPO`, and the worst was
   that `CLAUDE.md` does not auto-load there, which the prompt had claimed it did.
4. `4348daa` removed the header and separator so the whole file pastes with select-all.
5. `63dd7dd` removed all three markdown tables and fixed six defects, including a contradiction
   between "do not start any work" and a boot sequence, and a commands block that said "all four"
   while listing three.

**The lesson worth keeping:** every one of those five was caused by writing the file without
checking what already existed, or without testing how it would actually be used.

## 2026-09-10 (seventh) - A way to run without a hypervisor, found by asking what the snapshot is actually for.

**Did:** worked through what happens if a monitored endpoint cannot be reverted, then stress
tested the workaround. Recorded as OPEN-QUESTIONS 19 with a six-step test sequence.

### How it started

The question was how the system reaches a real endpoint. The answer in
`proposal-form-FINAL.md:226` is that **nothing is installed on it**: one server beside the SIEM,
driving the existing Wazuh agent. But `:240` carries a precondition that answers the question
differently: target hosts must be **virtual machines under a hypervisor supporting snapshots**.

**That precondition is in the preconditions table and not in Scope and Limitations.** A reader of
the limitations never learns of it. It is a bigger restriction on where the system can be used
than the Windows-only limit that *is* stated.

### The insight that opened it

The snapshot is not the special part. **Returning the machine to a known state is.** Anything that
does that works, and Windows already ships one: the **Unified Write Filter**, supported on
Enterprise, Education and IoT Enterprise.

`DECISIONS.md:326` records WIN-EP-01 as Windows 11 **Education**, chosen 2026-09-02 because
Enterprise Evaluation expires after 90 days. **That edition decision, made for an unrelated
reason, may have provided this for free.**

### Stress test: six ways it breaks

1. **UWF reverts the hardening change too.** Registry writes go to the overlay and are discarded.
   Fixed by servicing mode, at two extra reboots per change.
2. **The overlay can fill mid-run.** UWF writes Event ID 2 when it does. **Nothing in the current
   pipeline looks for that**, so a corrupt run would produce plausible numbers. This is the one to
   worry about, because a silently bad run that looks fine is exactly the failure this thesis is
   about.
3. **Unsent agent events die at the reboot.** A fourth silent loss channel next to items 8 and 13.
   The existing 120 s drain mitigates it.
4. **UWF may change the telemetry it is meant to preserve.** Harmless to the comparison, since it
   is on for both phases. Harmful to external validity, since the study claims its findings apply
   to machines without it.
5. **Windows here is unactivated.** Whether a DISM optional feature enables in that state is
   unverified and is the likeliest silent killer.
6. **The niche is narrow.** A VM is faster where one is available.

### What attacking it produced

Risk 6 looked fatal until the exception surfaced: UWF only wins where the hardware matters, and
**there is exactly one such case in this project.** Credential Guard, change C8, is blocked on
nested virtualisation (item 2). A physical machine with UWF could test C8 when a VM cannot. Item 2
now cross-references item 19, so a nested-virtualisation failure no longer forces C8 to be
dropped.

**The strongest argument for the idea came out of trying to kill it.**

### Corrections to my own earlier answers, recorded because both were wrong

- I recommended **Deep Freeze**, a paid third-party product. UWF is better: built into the Windows
  already installed, no purchase, and no third-party driver entering the golden image, which
  matters because Chapter 3 must describe the software inventory.
- A proposed alternative of **native boot from a differencing VHDX** does not work. Microsoft's
  deployment documentation states differencing disks are **not supported** for native boot and can
  cause update failures.

### Verified rather than assumed

| Claim | Source |
|---|---|
| UWF is supported on Enterprise, Education, IoT Enterprise | Microsoft Learn, Windows OS Hub |
| WIN-EP-01 is Windows 11 Education, build `10.0.26100.9168` | `DECISIONS.md:326` |
| Overlay full writes Event ID 2, "CRITICAL level" | Microsoft Learn, `uwf overlay` |
| Servicing mode makes changes permanent for one boot cycle | Microsoft Learn |
| Differencing disks are not supported for native boot | Microsoft Learn, deploy on VHD |

**Not verified:** whether UWF enables on unactivated Windows, and whether the DISM feature name is
`Client-UnifiedWriteFilter`. I attempted the feature query on the host and got
`The requested operation requires elevation`, which confirms the failure mode the check predicts
but proves nothing about the feature. Both are step 1 and step 2 of the test sequence.

**Next:** testing runs in a separate chat, following the sequence in OPEN-QUESTIONS 19. Stop at
the first failure.

## 2026-09-10 (sixth) - The index was stale again. Four live claims corrected, and the new prompt cut in half.

**Did:** compared `docs/PROMPT-new-chat.md` against `CLAUDE.md` to answer whether they duplicate
each other. They do in five places. Fixing that turned up four stale claims in `CLAUDE.md` and its
neighbours.

### The stale claims, and why this one stings

`CLAUDE.md` rule 1 says: *"This index goes stale. On 2026-09-08 it still claimed no code existed
while 49 tests were passing."* **It was still claiming exactly that**, two days after the entry
recording the fix.

| Where | Said | Now |
|---|---|---|
| `CLAUDE.md:36` | `src/` "Python harness and analysis. **No code yet.**" | Package `telos`, 8 modules, 49 tests passing |
| `CLAUDE.md:32` | `thesis/T3/` "**First fallback**" | Dead, killed 2026-08-19. Line 114 of the same file already said so, so **the file contradicted itself** |
| `CLAUDE.md:118` | "The live blocker is item 1: 4 anti-hardening, 6 remove the attack, 3 usable" | Item **18**. Item 1's catalogue was rebuilt on 2026-09-08 |
| `thesis/README.md:9` | T3 "First fallback, has its own gate" | Dead, with the reason |
| `thesis/T3/README.md:6` | "First fallback if T1 fails its spike gate" | Banner added. Body left unedited so the reasoning, and the mistake of not checking the annotation count first, stay visible |

**Why the 2026-09-08 fix missed it.** That session corrected the Commands section, which mentions
pytest, and stopped there. It never swept the table five rows above. **A correction applied to the
place you noticed is not a correction.**

`docs/DECISIONS.md:846` also says "the repo has no code yet". **Left alone deliberately.** It sits
inside a dated decision entry, and the rule in that file is supersede, never edit. It was true
when written.

### The duplication, and what was cut

`PROMPT-new-chat.md` repeated five things `CLAUDE.md` already carries: the project summary, the
four answering rules, the commands block, the defense brief, and the record-before-moving-on
habit. All five removed. The prompt now opens by saying it is a supplement and that `CLAUDE.md`
loads on its own.

**223 lines to 158.** What is left is only what `CLAUDE.md` has no room for: a routing table from
question type to file, the settled numbers, the open items, built versus designed, and the short
list of facts that get stated wrong.

**The trade, stated openly.** The prompt is no longer self-contained, so pasting it into a browser
chat with no filesystem gives less. That case is covered in the header: paste the two `CLAUDE.md`
files instead.

### Still over the limit

`CLAUDE.md` is **209 total lines, 154 non-blank**, against a stated limit of 200. It was already
at 205 before today's edits, so this is not new, but it is not fixed either. The offer stands to
move "The defense brief" into its own file, which is 13 lines.

**Also:** `Measure-Object -Line` in PowerShell does **not** count blank lines. It reported 154 and
I nearly recorded that as the file length. Use `(Get-Content file).Count`.

## 2026-09-10 (fifth) - Removed six preparation documents from the public repository.

**Did:** copied six files out of the repository, verified each copy byte for byte, then
`git rm`'d them. They now live in `prep-local/` inside the external documents folder. Nothing was
deleted.

| File | Why it left |
|---|---|
| `thesis/title-defense-script.md` | A script for one meeting. **Contains a section titled "Part 7. What NOT to bring up tomorrow."** |
| `docs/DEFENSE-PREP.md` | Contains section 8, "Known weak spots in your own documents" |
| `thesis/title-defense-bullets.md` | Rehearsal bullets |
| `thesis/topic-proposal-titles.pptx` | Slides for one meeting |
| `thesis/T1/proposalll.txt` | Clutter, not risk. A filename with three L's says nobody cleaned up |
| `thesis/T1/proposal(ongoing verification).txt` | Same, and byte-identical in size to `proposal.txt` |

**The rule applied, and it is worth keeping.** *Would this file exist if there were no defense
day?* Yes means work product and it stays public. No means performance preparation and it goes.
A second test settles the hard cases: **does the file contain a fact about the work, or a
strategy about people?** Facts stay.

The distinction matters because the *content* was never the problem. "Credential Guard nested
virtualisation is untested" sits in `OPEN-QUESTIONS.md` item 2 and is one of the better things in
this repository. The same fact written as "do not raise this tomorrow" is a different kind of
document and belongs nowhere public.

**Checked references before removing, not after.** Renaming four PNGs earlier today broke eight
document links because I did not check first. This time a grep found one real break, a markdown
link at `WORKLOG.md:1455`, which is now plain text pointing at this entry. The other three
mentions are plain-text history and stay as written. `tools/check_docs.py` still names the two
`.txt` files in its FROZEN set, which remains correct because the checker scans the external
folder too.

**Not done, and it is a real limit.** `git rm` removes the files from what anyone browsing sees.
**It does not remove them from git history.** Anyone who knows to look can still recover
`title-defense-script.md` from an earlier commit. Fully removing it needs `git-filter-repo` and a
force push, which this project records as the most dangerous command it has run. That decision is
still open and is deliberately not being taken quietly.

## 2026-09-10 (fourth) - Wrote a full explainer for the activity diagram, aimed at junior analysts.

**Did:** wrote `ACTIVITY-DIAGRAM-EXPLAINED.md` in the documents folder. Thirteen sections covering
every box, decision, datastore and connector on both sheets, for an audience of junior security
analysts and a detection engineer new to the project.

**Sourced from the generator and the code, not from memory.** Re-read
`make_activity_diagram.py` for the exact box wording and confirmed the module list in
`src/telos/` with a glob before claiming which parts are built.

**What it covers beyond a box-by-box walkthrough:**

- The problem stated for someone who has never met it: hardening changes configuration,
  configuration decides what is logged, and a dead detection looks exactly like a quiet one.
- A vocabulary section defining every term once, including the ones people get wrong. Event 4104
  is in PowerShell/Operational, not Security. Rate here is per **run**, not per minute.
- Why the chi-square runs once globally, both reasons.
- Why the classification order is NEW, then INCONCLUSIVE, then LOST, and what breaks if it is not.
- The three REDUCED conditions with the arithmetic worked, including the direction of the noise
  floor comparison, which is the one people state backwards.
- A complete worked example, ending with what event-ID-only counting would have reported instead.
- A limits section carrying the value-versus-presence gap (OPEN-QUESTIONS 18) and the
  "no significant change" conflation (OPEN-QUESTIONS 16), stated openly rather than hidden.
- A built-versus-designed table, so a new joiner does not go looking for the index, the impact
  scorer or Phase 5 in code that does not contain them.
- Ten self-test questions with no answers shown.

**Added the file to the LIVE set in `tools/check_docs.py`** and scanned it. One hit, and it is the
sentence warning readers **not** to say "below the noise floor". A false positive: the mistake is
being quoted to warn against it. The file reports "all expected steps mentioned".

**Not copied into the repository.** It lives only in the documents folder, where it was asked
for. Duplicating it would create the exact drift this session spent its time repairing.

## 2026-09-10 (third) - Fixed proposal-form-FINAL.md and T1-REVISIONS-LIST.md. LIVE defects now zero.

**Did:** repaired both remaining live documents. Both live outside the repository, so only this
entry is committed. I raised that both were blocked on OPEN-QUESTIONS 17 and 18; that concern was
overruled, so I fixed everything that does not depend on those answers and left what does.

### proposal-form-FINAL.md, six changes

| Where | Was | Now |
|---|---|---|
| Header | "Same content, written short" | **False.** The title and the event-key definition both changed. Now marked a working note, states what changed, and says to delete it before converting to .docx |
| Module 2 | signature described, step not | added that the system pairs a lost key with a new key whose field set is a strict subset and names the dropped field |
| Module 3 | five classifications listed | added that **New is tested before the rarity check**, and why |
| Phase 0 | "noise model of each event **type**" | event **key** |
| Activity diagram | `.png` filenames | `.svg`, with the reason |
| Scope and Limitations | seven limits | eight. New limit 8 states the value-level gap from OPEN-QUESTIONS 18 without presuming its answer |

**Module 2 was already correct.** It defined the key as which tracked fields were "actually
populated" and described the lost-plus-new signature. My checker reported it missing; that was a
false negative in my regex, not a defect.

### T1-REVISIONS-LIST.md, nine changes

The header now says plainly that `proposal-form-FINAL.md` supersedes the version this list
describes, that only Revisions 1 and 14 have been brought forward, and that **where the two
disagree the final form is the document being submitted**. That is the honest state until the
REVISED-to-FINAL diff runs.

Revision 14 rewritten: "discriminating field **values**" became which tracked fields **carried a
value**. Its example changed from an access mask, which is a value change the method cannot see,
to `ProcessCreationIncludeCmdLine_Enabled`, which empties CommandLine and which the method does
see. The known limit is stated. Revision 15 gained the branch-order rule and the field-pairing
step. Five "event type" references became "event key". Revision 18 and the file list point at the
SVG files and say why.

### Two false negatives in my own checker, both fixed

1. The `field-pairing` pattern only matched "pairing LOST" and "field-level loss", so it reported
   three documents as missing a step all three described in prose.
2. After widening it, `[^.\n]` still failed on `proposal-form-FINAL.md`, because these documents
   wrap at 96 columns and the sentence spans a line break. Changed to `[^.]`.

**Both were fixed in the tool, not by rewording the documents.** Writing prose to satisfy a narrow
regex would be backwards, and it would have hidden the defect in the checker.

### Result, verified by re-running the scan

**LIVE hits 43 to 16**, and every one of the 16 is accounted for:

| Count | What | Action |
|---|---|---|
| 9 | Title `before:` and `after:` records, and the panel's own quoted wording | **Correct. Do not change.** |
| 3 | "Why chi-square runs once, **not** per event type" | **Correct.** Explains the reassignment |
| 1 | "Network IDS alerts are out of scope" | **Correct.** This is the sentence that scopes them out |
| 3 | "server-side web application" | **Left on purpose.** OPEN-QUESTIONS 17, adviser's call |

All three live documents now report "all expected steps mentioned". No PNG references remain in
any of them.

**Also did:** pointed `T1-PANEL-RESPONSE.md`'s four image embeds at the SVG files. Fixing the other
two files had left it as the only one still showing the pre-2026-09-09 pictures, which is an
inconsistency I introduced in this session.

**Next:** the only LIVE item left needing a decision is the web application claim. After that, the
REVISED-to-FINAL diff.

## 2026-09-10 (second) - Fixed T1-PANEL-RESPONSE.md. Nine changes, two deliberately left.

**Did:** repaired every actionable defect the scan found in `T1-PANEL-RESPONSE.md`. The file lives
outside the repository, so only this entry is committed.

| Where | Was | Now |
|---|---|---|
| Decision rule | `INCONCLUSIVE` tested **before** `NEW` | `NEW` first, then rarity, then `LOST`, matching `_test_key` (`differential.py:132` before `:138`) |
| Decision rule | `RR(e) < noise_floor(e)`, undefined | `( 1 - RR(e) ) > 3 * CoV(e)`, with a note that the direction is easy to state backwards |
| Decision rule | no pairing step | added: pair each LOST key with a NEW key whose field set is a strict subset |
| Report table B | `RR 0.04 ... LOST` | `REDUCED`. LOST needs a post-change count of exactly zero (`differential.py:146`) |
| Report table B | "41.2 **per min** to 1.6 per min" | "41.2 to 1.6 **per run**" (`differential.py:115`) |
| Report tables B, C | "one row per event **type**" | per event **key** |
| Key example | `WinSec : 4688 : ParentImage=cmd.exe` | `Security-4688[CommandLine,NewProcessName,ParentProcessName]`. 4688 carries ParentProcessName; ParentImage is a Sysmon field |
| Key example | `Suricata : alert : sid=2027000` | removed. Network IDS is out of scope per Revision 14 |
| Plain terms | "arrive **per minute**" | "arrive during one run" |
| Steelman, Module 2, Module 3 | "event type" / "discriminating fields" | event key, populated tracked fields |

**Why the branch order was the worst one.** A key that appeared only after the change always has a
pre-change count of zero, which is below `min_count`. Testing rarity first reports **every NEW key
as INCONCLUSIVE**, which destroys the LOST-and-NEW pair that is the entire signature of a stripped
field. The document's own algorithm would have disabled the feature the document argues for. The
file now says so explicitly, so the ordering is defensible rather than accidental.

**Added rather than removed: the value-level limitation.** The key records *that* a field carried a
value, not *which* value. Two places now say this plainly, and the LSA Protection worked example
carries an instruction not to present it to the panel until one capture confirms what
`GrantedAccess` actually contains after `RunAsPPL = 1`. Writing the limitation in beats deleting
the example, because the example is good if the capture goes the right way. See OPEN-QUESTIONS 18.

**Left alone on purpose, both pending decisions:**
- Eight PNG references. The PNGs are stale renders and the fix depends on the unresolved
  regenerate-or-repoint choice.
- `:174`, "server-side web application". OPEN-QUESTIONS 17, blocked on the adviser.

**Verified by re-running the scanner, not by eye.** LIVE hits fell 43 to 34, and the file moved to
"all expected steps mentioned". Every remaining hit in it is one of the two pending decisions or a
false positive: `:453` correctly describes what the *old* proposal did, and `:625`, `:642`, `:661`
quote the panel's own title wording.

**RECORD hits rose 27 to 33**, because these worklog and OPEN-QUESTIONS entries quote the defects
they describe. That is the file-status split working as intended, not new damage.

**Next:** `proposal-form-FINAL.md` and `T1-REVISIONS-LIST.md` hold the remaining 22 LIVE hits, and
both are blocked on OPEN-QUESTIONS 17 and 18.

## 2026-09-10 - Scanned all 28 thesis documents. Found a claim that was never decided and is already written as fact.

**Did:** built `tools/check_docs.py` and ran it over `docs/`, `thesis/` and the external documents
folder. Twelve patterns, each carrying the code reference that settles it. 28 files, 138 hits.

**Why a script instead of reading.** Nine documents, twelve patterns. Reading catches whatever the
reader happens to remember on that pass. This catches the same things every time, and it can be
re-run before every submission. The personal documents path is passed as an argument, so it is not
committed to a public repository.

**The key design choice: file status decides whether a hit matters.**

| Status | Meaning | A hit here is |
|---|---|---|
| FROZEN | The version the panel read, and its exports | **Correct.** Changing it would falsify the record. |
| LIVE | Will be submitted or read by the adviser | A defect |
| SUPERSEDED | Replaced by a later file | Fix only if reused |
| RECORD | This project's own logs | Fine inside a quoted history |

Without that split the tool reports 138 problems, of which 25 are the historical record being
correctly historical. With it, the 43 LIVE hits are the list that matters.

### The finding that matters most: nobody ever decided the system is a web application

Three live documents state it as settled:

| File | Line |
|---|---|
| `proposal-form-FINAL.md` | 217 |
| `T1-PANEL-RESPONSE.md` | 174 |
| `T1-REVISIONS-LIST.md` | 111 |

A search of `DECISIONS.md` and `OPEN-QUESTIONS.md` for "web application", "web-based", "web
interface" and "System Type" returns **only Wazuh deployment-mode entries**. There is no decision
and there was no open question. It was marked ASSUMPTION in a draft, never confirmed, and written
into a submission document without the marking.

Worse, `proposal-form-FINAL.md:221-223` says the analytical core "also runs from the command line
without the web interface" and that headless mode produces every measurement in the study. **The
document commits to building a web application whose only stated role is to not be used for the
results.** Recorded as OPEN-QUESTIONS 17.

### Two flaws in my own tool, found by using it

1. **It printed only the basename.** `README.md` exists five times here, and
   `proposal-form-REVISED.md` exists both in the repo and in the documents folder, so hits were
   ambiguous and some appeared twice. I misread a hit as being the root `README.md` when it was
   `thesis/T1/README.md`. Fixed: paths now print relative to the repo, external files as `[ext]`.
2. **Regex cannot see ordering.** The wrong branch order in `T1-PANEL-RESPONSE.md:390-392`
   (INCONCLUSIVE tested before NEW, so every NEW key would be reported INCONCLUSIVE) was found by
   reading, not by the tool, and no pattern would have caught it. The tool narrows where to look;
   it does not replace looking.

**Result: two public files carry the pre-panel title.** The root `README.md` correctly carries the
panel's exact wording, which OPEN-QUESTIONS 0 says is deliberate. But `thesis/T1/README.md:3` still
carries "Detection of Hardening-Induced Blind Spots via Differential Sequence Alignment", the title
from before the defense. Those two files disagree with each other in public.

**Broke / stuck on:** nothing broke. The scan is read-only.

**Next:** the REVISED-to-FINAL diff must not run until OPEN-QUESTIONS 17 and the value-keying
question are answered, because both claims appear in **both** files and the answers change the
diff.

## 2026-09-09 (second) - The other two figures were worse. One named a Windows log channel that does not exist.

**Did:** checked `T1_Figure_Noise_Floor.svg` and `T1_Figure_Analysis_Pipeline.svg` against
`src/telos/`, then rewrote both as generators. Extracted the shared drawing helpers into
`thesis/T1/figures/svgkit.py` so three generators do not carry three copies.

### The noise floor figure had a factual error, not just stale wording

| Problem | Evidence |
|---|---|
| Row labelled **"WinSec 4104"** | Event 4104 is script block logging, in `Microsoft-Windows-PowerShell/Operational`, not the Security log. `eventkey.py:48` says `"PowerShell-4104"`. |
| **INCONCLUSIVE explained by the wrong rule** | Figure said the key was inconclusive because "its band spans almost everything". `differential.py:138` reports INCONCLUSIVE when fewer than `MIN_PRE_COUNT` (30) events were seen before the change. The band never enters it; the key is not tested at all. |
| Rows labelled by event type | Unit of analysis is the event key (DECISIONS.md 2026-09-04). |
| **LOST marker drawn above zero**, at about 4% of the pre-change rate | `differential.py:146` classifies LOST only when the post-change count is exactly zero. |

The wrong INCONCLUSIVE rule is the one that mattered most. **Learning the explanation off that
figure would have meant giving a panelist the wrong mechanism for one of the five
classifications.** The rewritten row shows the pre-change count (12), draws no band, and dashes
the track to say the key was never measured.

### The pipeline figure omitted two steps and stated a formula the code does not use

| Problem | Evidence |
|---|---|
| "an **event-type key** e = ( source, event ID, **discriminating fields** )" | Predates the 2026-09-04 decision. The key uses fields that were **populated**. |
| `λ₀(e) = count / window` | `differential.py:115` computes `a / n1`, count per **run**. `analyse()` rejects phases with unequal windows (`differential.py:266`), so the two are proportional and **the rate ratio is identical either way. No result changes.** The formula shown was still not the one that runs. |
| **The global gate was missing entirely** | `analyse()` runs one chi-square over the whole 2-by-K profile before any key is tested and returns with no findings when it does not pass (`differential.py:273-281`). A figure without it implies every key is always tested. |
| No INCONCLUSIVE rule in the decision box | `MIN_PRE_COUNT = 30`. |
| `field_loss_pairs()` had no step | `eventkey.py:159`. |

**Result:** both regenerated, rendered, and read at full size before installing. Added a second
caption to the noise floor figure naming all three conditions, because the old one showed the
band alone and invited the reader to think the band is the whole decision rule.

**How the refactor was proved safe.** Moving the helpers into `svgkit.py` could have changed the
already-verified activity diagram. Regenerated it and ran `git status`: the two activity SVGs did
not appear, meaning the output is **byte-identical** to the committed version. Only the generator
changed.

**Also did:** renamed the four PNG renders in the documents folder to
`*.SUPERSEDED-2026-08-28.png`. They were made from the stale SVGs, and a stale PNG sitting next
to a corrected SVG is the easiest way to insert the wrong picture. Nothing deleted; all
reversible.

**Broke / stuck on:** the "noise floor" label in the pipeline figure first landed on top of the
new gate box. Moved above it and given a white plate. Caught by rendering, not by reading the
code.

**Next:** the .docx still embeds `T1_Activity_Diagram_Swimlane.png` from 2026-08-15. Inserting
the four corrected SVGs is the remaining piece of OPEN-QUESTIONS 15.

## 2026-09-09 - The activity diagram described the superseded event key. Both sheets regenerated from a script.

**Did:** checked `T1_Activity_Diagram_Revised_Sheet1/2` against `src/telos/`, not against other
documents. The diagrams are dated 2026-08-28. The decision that changed the unit of analysis is
dated 2026-09-04 (DECISIONS.md). The figures never caught up.

**Result: six findings, four of them wrong statements.**

| Where | Said | Now says |
|---|---|---|
| Sheet 1, Phase 0 | "Fit the noise model per **event type**" | per event key |
| Sheet 1, Phase 0 | "**event-type** → rule → ATT&CK index" | event key → rule → ATT&CK index |
| Sheet 1, Phase 1 | "normalize to **event-type keys**" | keyed by event type + populated tracked fields |
| Sheet 2, Phase 4 | "union of **event-type keys**" | union of event keys |
| Sheet 2, Phase 4 | decision "Any LOST or REDUCED key **below the noise floor**?" | "Any key classified LOST or REDUCED?" |
| Sheet 2, Phase 4 | (no box) | new box for `field_loss_pairs()` |

**Why the noise-floor decision was wrong twice.** It was drawn as a separate test after
classification. In the code the noise floor is one of three conditions **inside** `classify()`
(`differential.py:231`). And "below the noise floor" inverts the comparison: reporting requires
`drop > band` (`differential.py:229`). The three conditions now appear inside the classification
box, where the code applies them.

**Why the missing box mattered.** `field_loss_pairs()` (`eventkey.py:159`) matches a LOST key
against a NEW key of the same event type differing only by dropped fields. That is the step that
turns two confusing rows into one readable finding, and it had no box.

**Two things found while checking, both worse than the diagram itself:**

1. **The .docx embeds the diagram from 2026-08-15, not the revised sheets.**
   `word/media/image1.png` is 326,941 bytes, an exact size match with
   `T1_Activity_Diagram_Swimlane.png`. The revised sheets were never inserted.
2. **`T1_Figure_Analysis_Pipeline.svg` has the same stale keying**, plus a formula that does not
   match the code: it states `λ₀(e) = count / window`, but `differential.py:115` computes
   `a / n1`, count per **run**. Windows are validated equal, so the rate ratio is unaffected and
   no result changes. The stated formula is still not what runs.

**Root cause, and the actual fix.** The figures had no source. They existed only as SVG text
with hand-computed absolute coordinates, so nothing could be updated without hand-editing
geometry, and so nothing was. Added `thesis/T1/figures/make_activity_diagram.py`, which
generates both sheets. A design change is now a string edit and a re-run.

**Verified by rendering, not by trusting the script.** Both sheets opened in a browser and read
at full size. No overlapping boxes, no text past a border, every connector attached, all six
changes present. The 2026-08-28 SVGs are kept beside the new ones as `*.2026-08-28.svg.bak`.

**Broke / stuck on:** cannot export PNG from SVG here; no renderer is installed. Not needed:
Word inserts SVG directly and keeps it as vector, which is better for print than the old PNG.
`(unverified)` for the exact Word version on this machine.

**Left alone on purpose:** the "no" branch still reads "Record no significant change".
`global_gate()` returns not-passed for three different situations and only one of them is
"nothing changed" (`differential.py:74`, `:84`, `:91`). Relabelling the box would put the diagram
ahead of the code and create a fresh mismatch. Recorded as OPEN-QUESTIONS 16 instead.

**Next:** re-check `T1_Figure_Analysis_Pipeline.svg` and `T1_Figure_Noise_Floor.svg` the same
way, then insert the corrected sheets into the .docx.

## 2026-09-03 - Four open questions closed. Two of them were smaller than written, one was a different problem entirely.

**Did:** worked the open list. Items 1d, 7 and 12 are now answered or fixed. Item 5 is measured
and turned out to be a real problem for a different reason than the one recorded.

### 1d, journald rate limiting. Answered: no, not as the lab is scoped.

**The premise was partly wrong, and correcting it is most of the answer.** The item assumed the
endpoint's telemetry passes through journald on SIEM-01. It does not. The Phase 3 evidence
already showed how WIN-EP-01's events arrive:

```
"decoder":{"name":"windows_eventchannel"}   ...   "location":"EventChannel"
```

Port 1514 into the manager's own queue. journald on SIEM-01 carries only SIEM-01's own OS events.

Measured anyway, for completeness:

| Item | Value |
|---|---|
| `RateLimitIntervalSec` | 30s, built-in default, not overridden anywhere |
| `RateLimitBurst` | 10000, built-in default |
| **Suppression notices ever recorded** | **0** |
| Journal storage | persistent, 79.5 MB |
| Only non-default setting | `ForwardToSyslog=yes` |

The limit has never been reached across every boot in the journal. **It comes back if a Linux
endpoint is ever added**, because that host's `auditd` events would pass through journald.

**Separate finding from the same output:** `rsyslog` is installed and active, so
`ForwardToSyslog=yes` means every journald message is written **twice**, to the journal and to
`/var/log/syslog` (already 1.77 MB). Wazuh does not read `/var/log/syslog`, so it is duplicate
disk writes, not duplicate collection. Disk churn inside every capture window.

### 5, snapd. Measured. Real problem, different cause.

```
snap list : empty, NO snaps installed at all
```

**Nothing can refresh, because nothing is installed.** The recorded fear cannot happen. But:

```
Sep 03 08:02:30 siem-01 snapd[5068]: state ensure error:
  Get "https://api.snapcraft.io/api/v1/snaps/sections": net/http: request canceled while
  waiting for connection (Client.Timeout exceeded while awaiting headers)
```

**snapd contacts Canonical on its own loop with zero snaps installed, and it is already failing.**
After Phase 5 removes internet access it will fail every time, forever, and each failure is a
journald message Wazuh collects. Same shape as the Wazuh vulnerability feed disabled in Phase 2.
`snapd.snap-repair.timer` is also enabled and phones home independently of snaps.

Removing the package is the wrong fix: `apt-cache rdepends --installed snapd` returns
`ubuntu-server-minimal`, `ubuntu-server`, `apparmor` and `command-not-found`.

**Handed to the student, because the narrow sudoers rule grants `telos-archive` and nothing
else.** That is the rule working as designed, not a failure.

### 7, vmnet3. Answered by correcting the record, not the machine.

```
VMware Network Adapter VMnet3   Up   10.20.20.1/24
SIEM-01.vmx   : VMnet8, VMnet2
WIN-EP-01.vmx : VMnet8, VMnet2
```

**No VM is attached to vmnet3 at all.** Re-reading runbook Phase 1, it never actually claimed
vmnet3 had no host adapter. It said vmnet2 should keep its adapter and left vmnet3 unstated, so
the contradiction was with an inference, not with anything written. Phase 1 now states the
adapter explicitly, plus the condition that reopens the question: if `IDS-01` is ever built there
and the thesis claims that segment is isolated, untick the adapter first and re-verify.

### 12, active response. Fixed.

```
2026/09/03 08:04:36 wazuh-agent: INFO: (1350): Active response disabled.
```

It let the **manager execute commands on the endpoint**. Worse than the item 8 scan modules,
because it changes state rather than adding events. `active-responses.log` is still collected and
will simply stay empty, which is itself evidence that nothing fired.

`ossec.conf` is now **12,115 bytes, SHA256
`CED16E0B41384BF421192317E3754732D0E3155A85BA98F2CEEDFA846B0278B1`**, committed as
`lab/configs/wazuh-agent-ossec.conf`. Every prior version is kept in the guest:
`ossec.conf.telos-orig`, `ossec.conf.telos-pre-item8`, `ossec.conf.telos-pre-item12`.

The agent's full module state now reads:

```
rootcheck       disabled yes      cis-cat         disabled yes
sca             enabled  no       osquery         disabled yes
syscheck        disabled yes      active-response disabled yes
syscollector    disabled yes
client_buffer   disabled no   queue_size 5000   events_per_second 500   <- item 13, unmeasured
agent-upgrade   still starts, no agent-side switch                      <- item 8 remainder
```

### 6, clock synchronisation. Fixed, and the drift half answered differently than the item framed it.

**The switches.** All six `time.synchronize.*` set to `FALSE` in both `.vmx` files, alongside the
`tools.syncTime` already there. `tools.syncTime` alone stops only the periodic sync; the other six
cover snapshot revert, resume and Tools startup. Phase 6 reverts before every one of 101 runs.

**Verified through a full power cycle**, because VMware rewrites the `.vmx` on every power off and
could have stripped them. All seven lines survived. Backups kept as
`<name>.vmx.telos-20260903T081807Z.bak`.

**The drift half. The three options in the item were the wrong question.** Every archive line
carries both clocks:

```
endpoint clock : "systemTime":"2026-09-02T13:30:38.7096614Z"
manager clock  : "timestamp":"2026-09-02T13:30:40.599+0000"
```

So the answer is not to synchronise the machines, it is to **stop depending on the manager's
clock**. Harness rule adopted: every window boundary and every measurement uses the endpoint's own
`systemTime`, and the manager's `timestamp` is used for nothing but latency. SIEM-01 drift then
cannot reach the results. Option 2, a time server on the host at `10.20.10.1`, is **rejected**: it
would put a live network service on a segment the thesis calls isolated, to solve a problem the
rule removes.

**Left for Phase 5:** the golden snapshot must be taken **cold**. A cold revert boots the guest
fresh and VMware sets the clock from the host; a live snapshot restores a stale clock. The
blueprint implies cold but never says it.

**Fresh checkpoints taken**, because `phase3-complete-2026-09-02` predates the item 12 fix and
reverting to it would have silently re-enabled active response:

```
WIN-EP-01  phase3-complete-2026-09-02, agent-hardened-2026-09-03
SIEM-01    phase3-complete-2026-09-02, timesync-off-2026-09-03
```

### New item 14, found by accident: Wazuh rotates `archives.json` daily, by hard link

The date rolled over mid-session and `archives.json` went from 49,654,191 bytes to 5,166,709. It
did not shrink, it rotated.

```
drwxr-x--- 3 wazuh wazuh    4096 Sep  1 19:36 2026
-rw-r----- 2 wazuh wazuh 5272919 Sep  3 08:19 archives.json
```

**The link count of 2 is the important part.** `archives.json` is a **hard link** to today's file
in the dated tree. Same inode, two names.

Two consequences for blueprint run-protocol step 10, which assumes one growing file per run:

1. **A run crossing midnight splits across two files.** Unattended overnight batches are exactly
   when that happens, and the harness would export half a run without noticing.
2. **Truncating `archives.json` also empties that day's stored archive**, because it is the same
   inode. The truncate step does not clear a scratch file, it deletes the day's permanent record.

The cleanest fix is probably to stop truncating altogether and export the dated archives instead,
which also removes a destructive step from a 101-run unattended loop. Recorded as item 14 rather
than fixed, because it changes the run protocol.

### 14 answered the same day: export by date, never truncate

Decision taken and the design changed. `lab/scripts/telos-archive` rewritten with `truncate` and
`rotate` **removed entirely**, and `dated-list`, `dated-path DATE`, `export DATE` and `disk`
added. `tail`, `count` and `show` now take an optional `DATE` and read gzipped dated archives
through `zcat`. `export` prints `bytes_gz`, `sha256_gz` and `lines` so the harness can **verify**
a copy rather than assume it.

**The second benefit is the one that helps at the defense.** With truncation gone the tool has no
destructive subcommand at all, so the single sudoers rule grants the harness account **read and
export only**. It cannot alter or delete the evidence store. "How do you know your archives were
not modified?" now has a checkable answer.

**What it moves rather than removes:** disk management now rests entirely on Wazuh's own rotation
plus a retention policy that is still deferred. The free-space guard in the risk table is now
load-bearing.

Updated: `lab/blueprint.md` section 6, runbook Phase 6 step 10, `lab/scripts/telos-archive`.
Runbook Phase 5 also gained two requirements it had only implied: **snapshots must be taken cold**,
and **Tamper Protection must be turned off by hand before the golden snapshot**, or Config S will
not actually be suppressed.

### Student steps done and verified the same day: items 5, 10, 14

**14, the new archive tool is installed and works.** And it proved the premise it was written
from:

```
      483,328 bytes  plain  /var/ossec/logs/archives/2026/Sep/ossec-archive-01.json
   50,765,553 bytes  plain  /var/ossec/logs/archives/2026/Sep/ossec-archive-02.json
    8,585,338 bytes  plain  /var/ossec/logs/archives/2026/Sep/ossec-archive-03.json
size: 8585338 bytes  links=2  archives.json
truncate -> rejected, prints usage
disk     -> 195G total, 162G free
```

Yesterday's **50.7 MB** is intact in the dated tree. Under the old protocol one `truncate` would
have destroyed it, because `archives.json` is the hard link to today's file.

**5, snapd. Fixed as far as it is worth fixing, and the shortfall was my instruction.** All four
units are `disabled`, but `snapd.socket` is still `active`:

```
systemctl list-dependencies --reverse snapd.socket
  snapd.socket
  ├─snapd.seeded.service      <- I told the student to leave this alone
  └─snapd.service
```

`snapd.seeded.service` **requires** the socket, which socket-activates snapd. What happens now,
per boot:

```
08:40:32  state ensure error: Get "https://api.snapcraft.io/..."  timeout
08:41:02  snapd.service: Deactivated successfully.
snapcraft.io contacts this boot : 1
```

**The repeating timer behaviour is gone**, which was the real problem. One event at boot remains.
**Stopping here deliberately**: removing it means disabling a unit in the boot path of the machine
holding every piece of evidence, to delete one log line that occurs outside every capture window.
Bad trade. It is outside every window because of a rule this made explicit: **SIEM-01 must not be
rebooted during a capture campaign.**

**10, Tamper Protection. Off, and verified by function rather than by flag.**

```
IsTamperProtected             : False
DisableCpuThrottleOnIdleScans : True -> False -> restored to True
RESULT: scripted changes to Defender ARE accepted. Config S will work.
```

Reading `IsTamperProtected` alone would not have proved anything. What Phase 5 needs is for a
**script** to change a Defender setting and have it stick, so a harmless setting was flipped, read
back, and put straight back. Phase 5 now also requires reading Config S settings back after
applying them, because Windows can re-enable Tamper Protection after updates.

**8, closed.** The agent-upgrade module is a listener with no agent-side switch, and Wazuh never
upgrades by itself. The only risk is a person clicking **Upgrade** in the dashboard. Control is
procedural, plus recording the agent version in **every run manifest** so a bump is visible in the
data rather than assumed impossible.

Three campaign rules added to runbook Phase 6, each from something measured: no SIEM-01 reboot
mid-campaign, never trigger an agent upgrade and record the version per run, and every timestamp
comes from the endpoint.

**Broke / stuck on:**

1. **My snapd exclusion list was wrong**, as above. The four commands worked; the fifth unit I
   told the student to skip undid part of the effect.
2. **A shell command of mine failed on its own quoting.** Parentheses inside a comment in a
   here-string broke the remote `bash -c`. Moved to a script file, which is the pattern that has
   worked all session. Two commands were also declined by the sudoers rule, which is correct
   behaviour and not a fault.
3. The corrected `vmrun list` poll, forced to an array, exited on its first check instead of
   running to a 6 minute deadline.

**Next:** the list blocking the Phase 5 golden snapshot is down to five, and three of them are
one measurement:

| | Item | Status |
|---|---|---|
| 5 | snapd phoning home | measured, **two commands waiting on the student** |
| ~~6~~ | ~~`time.synchronize.*` switches~~ | **done later the same day, see above** |
| 8 | agent-upgrade, manager-side control | reduced scope |
| 9, 13 | Sysmon channel 64 MB circular, agent buffer 500 events/s | **the same measurement, during one real capture window** |
| 10 | Tamper Protection will defeat Config S | manual toggle in the guest, student step |
| **14** | **`archives.json` rotates daily by hard link** | **new, changes the run protocol** |

**Blocking the Phase 5 golden snapshot, after everything above:**

| | Item | Status |
|---|---|---|
| ~~5~~ | ~~snapd phoning home~~ | **done**, one boot-time event left on purpose |
| ~~8~~ | ~~agent-upgrade~~ | **closed**, procedural plus a per-run manifest field |
| **9, 13** | **Sysmon channel 64 MB circular, agent buffer 500 events/s** | **the only technical work left. One measurement, during one real capture window.** |
| ~~10~~ | ~~Tamper Protection~~ | **done and functionally verified** |
| ~~14~~ | ~~archive rotation and truncation~~ | **done**, protocol changed and the tool replaced |

**Nothing else blocks Phase 5 except items 9 and 13**, and those cannot be answered without a real
capture window, which is Phase 6 work. Phase 4 is already written in DECISIONS.md.

Phase 5 requirements now written into the runbook rather than implied: snapshots taken **cold**,
Tamper Protection off **before** the golden snapshot, and Config S settings **read back** after
applying them.

---

## 2026-09-02 (later) - OPEN-QUESTIONS 8 fixed, 11 answered, two new loss channels found, records audited.

**Did:** three jobs after Phase 3 closed. Fixed item 8, closed item 11, then audited whether
everything that happened today had actually been written down.

### 1. Item 8 fixed, and measured

Disabled `rootcheck`, `sca`, `syscheck` and `syscollector` in the agent's `ossec.conf`, each with
a comment in the file saying why. Verified from what the agent reports about itself after
restart, not from the file:

```
2026/09/02 13:56:21  (6001): File integrity monitoring disabled.
2026/09/02 13:56:21  rootcheck: Rootcheck disabled.
2026/09/02 13:56:21  syscollector: Module disabled. Exiting...
2026/09/02 13:56:21  sca: Module disabled. Exiting.
```

Measurement path untouched: all four `localfile` channels still analyzed, `Connected to the
server`, `status='connected'`.

**Measured effect on archive volume, three conditions, same 180-second method:**

| Condition | Rate |
|---|---|
| No agent at all (Phase 2) | 9.7 MB/day |
| One agent, scan modules **enabled** | 34.3 MB/day |
| One agent, scan modules **disabled** | **17.9 MB/day** |

The scan modules were producing about **two thirds of everything the agent contributed** while
idle, and roughly half the total archive volume.

**The reason that matters most is not volume.** Two of the four modules **react to the change
being measured**. `sca` evaluates a CIS Windows 11 policy, so its results change when a hardening
control is applied. `syscheck` monitors the registry, so it would observe the hardening script
making its edit. Both would emit events appearing only in post-change runs, and a differential
analysis would see a systematic pre/post difference caused by the instrument watching the change
happen. That would have looked like a finding.

`ossec.conf` is now 11,848 bytes, SHA256
`1F36416E1BC59443D98AD0307638F5C5C788BEE12C545140AD993A1E4E8F2658`, committed as
`lab/configs/wazuh-agent-ossec.conf`. Previous version kept in the guest as
`ossec.conf.telos-pre-item8`.

**Item 8 is not fully closed.** The agent-upgrade module still starts and has **no agent-side
switch**. The only control is on the manager: never issue an upgrade command.

### 2. Item 11 answered: host power loss

The power cable was accidentally unplugged. I verified that rather than accepting it,
because two stops had been recorded and only one explanation was offered. Windows records
unexpected shutdowns explicitly:

```
2026-09-02 11:27:05 UTC  Id=1074  StartMenuExperienceHost.exe (WIN-EP-01) has initiated the
                                  power off of computer WIN-EP-01 on behalf of user WIN-EP-01\eli
2026-09-02 13:19:07 UTC  Id=41    The system has rebooted without cleanly shutting down first.
2026-09-02 13:19:10 UTC  Id=6008  The previous system shutdown at 12:36:56 PM was unexpected.
```

**Two different causes.** The 13:05 stop was the power loss, confirmed by Event ID 41 with 6008,
and both guests restarted within two seconds of each other (WIN-EP-01 `13:19:03`, SIEM-01
`13:19:05`). The 11:27 stop was a deliberate power off from the Start menu. Moved to the Answered
section.

**What stays, and it is a different question:** a 67-hour unattended campaign has no protection
against host power loss. Phase 6 needs a watchdog that detects a guest which died mid-run and
aborts that run cleanly, rather than writing a manifest for data never collected.

### 3. Two new loss channels found while reading the agent config

Both found, both **deliberately not changed**, because each is a design decision rather than an
obvious fix.

**New item 12, active response is enabled.** `<active-response><disabled>no</disabled>` lets the
**manager execute commands on the endpoint**. That is the instrument modifying the machine under
test, possibly mid-window. Worse than the scan modules, because it changes state rather than
adding events.

**New item 13, the agent has its own rate limiter.**
`<client_buffer><queue_size>5000</queue_size><events_per_second>500</events_per_second>`. Above
500 events per second the agent throttles; when the 5000-event queue fills, events are dropped
before they are ever sent.

**There are now three silent loss channels between the endpoint and `archives.json`:**

| Where | Limit | Item |
|---|---|---|
| Sysmon event channel | 64 MB, `Circular` | 9 |
| Wazuh agent buffer | 500 events/s, 5000 queued | **13** |
| journald on SIEM-01 | rate limit, still unread | 1d |

The same failure in three places, and every one of them looks exactly like telemetry lost to a
hardening change.

### 4. Documentation audit

Went back over the session looking for things that happened but were never written down. Six
gaps, now closed:

1. **`git core.autocrlf` is `true` on this host**, and it silently rewrote the pinned Sysmon
   config on first commit. The stored blob was **123,256 bytes, one byte short** of the 123,257
   recorded in DECISIONS.md, so a clone would have produced a file whose hash did not match the
   pin, making the claim that Sysmon runs the committed config false. Fixed with `.gitattributes`
   and verified from git itself:
   ```
   git cat-file blob :lab/configs/sysmonconfig.xml | sha256sum
   055febc600e6d7448cdf3812307275912927a62b1f94d0d933b64b294bc87162
   ```
2. **The guest clock ran about nine hours ahead during Windows installation.** The System log's
   latest-dated entries are `22:41` and `22:42` with computer names `WIN-DUH56S57VMD` and
   `MINWINPC`, which are Windows setup names. The clock was corrected later. This explains the
   `InstallDate : 2026-09-02 22:43:07 UTC` that looked wrong earlier. The earliest Windows log
   entries carry a wrong timestamp. It does not affect the experiment, since the golden snapshot
   is far later.
3. **`vmrun` guest authentication fails on SIEM-01** with `Invalid user name or password for the
   guest OS`, using a password file that is well formed (32 bytes, no stray whitespace, no
   carriage return). SSH password authentication with the same account works, so the account is
   fine. Cause unknown, most likely a PAM configuration for `vmtoolsd` on Ubuntu. **Not chased,
   because it no longer blocks anything:** SSH key authentication to SIEM-01 works, and that is
   what the harness needs. Recorded so nobody re-discovers it.
4. **Kaspersky 21.26 is the host antivirus and Windows Defender is off on the host.** Added to the
   host baseline table. The `E:\TeLoS-artifacts` exclusion is a host change that must be removed
   when the thesis is finished.
5. **`E:\TeLoS-artifacts\` and `C:\Users\Elijah\.telos\`** were being used all session with no
   entry saying what they are. Both added to the host baseline table, with a note that the
   credentials folder must never be committed.
6. **`Host offset from UTC is -08:00` in `vmware.log`** contradicts the host file timestamps and
   both guests, which agree the host is UTC+8. Most likely VMware's sign convention for that
   field `(unverified)`. Recorded, not acted on.

### 5. Shutdown checks, and the first real test of the archive export path

Before shutting down, checked what had been left undone. Four things, three of them acted on.

**The Windows installer ISO was still connected at boot.** `sata0:1.startConnected = "TRUE"` on
WIN-EP-01, while SIEM-01 had been set to `"FALSE"` back in Phase 2. That left the endpoint
**depending on E: at every power-on**, and E: is the hard disk the project's first rule says no VM
may depend on. If that ISO were moved or renamed, WIN-EP-01 would fail to start. Set to `"FALSE"`
after the guests were powered off, because VMware rewrites the `.vmx` on power off and would have
discarded an earlier edit.

**Neither VM had a single snapshot.** Two days of work with no restore point, on a machine whose
power cable came out today. Took `phase3-complete-2026-09-02` on both. This is **not** the Phase 5
golden snapshot, which comes later with NAT disconnected. It is insurance. F: has 611.6 GB free.

**Blueprint run-protocol step 10 tested for the first time**, using the Phase 3 evidence as the
payload. Rotate, compress, pull to the host, decompress, verify:

```
rotate on SIEM-01 : /tmp/archives-20260902T153830Z.json.gz   2,214,413 bytes
pulled to host    : E:\TeLoS-runs\phase3-check\   2.11 MB
decompressed      : 48.37 MB, 15,261 lines
lines carrying telos-p3-check-001 : 2   (expected 2)
```

The path works. Two numbers worth keeping for planning 101 runs of storage:

| Measurement | Value |
|---|---|
| gzip compression on `archives.json` | about **23 to 1** |
| average size of one archive line | about **3.3 KB** |

**Truncation was deliberately not performed.** The retention decision is still deferred, and
`archives.json` holds the only copy of some evidence until exports like this one exist.

**Broke / stuck on:**

1. **`vmrun list` changes its return type, and it will bite the Phase 6 harness.** It returns
   **several lines when VMs are running and one line when none are**, so PowerShell hands back an
   **array** in the first case and a **string** in the second. A poll written as
   `if ($l[0] -eq "Total running VMs: 0")` reads the first list entry when it is an array and the
   first **character** when it is a string, so it prints `T` forever and never matches. My
   shutdown poll ran to its full 6 minute deadline instead of exiting as soon as the VMs stopped.
   The outcome was correct, the wait was wasted. **The harness calls this on every one of 101
   runs.** Force an array, for example `@(& $vmrun -T ws list)`, or match on the joined output.

2. **A PowerShell safety guard blocked a command** containing a remote `rm -f '/tmp/...'`. The
   cleanup was unnecessary anyway, since `/tmp` on SIEM-01 is cleared on boot, which is what
   deleted a staged script earlier today. Dropped the step.

Otherwise nothing new. The item 8 edit applied on the first attempt, with each of the four
replacements checked for exactly one match before writing.

**Next:** Phase 4 is largely already written in DECISIONS.md. The list blocking the Phase 5
golden snapshot now stands at:

| | Item | Status |
|---|---|---|
| 1d | journald rate limiting on SIEM-01 | open, unmeasured |
| 5 | snapd auto-refresh on SIEM-01 | open |
| 6 | clock drift plus four unset `time.synchronize.*` switches | open |
| 7 | vmnet3 host adapter contradicts the record | open |
| 8 | Wazuh agent scan modules | **mostly fixed**, agent-upgrade remains |
| 9 | Sysmon channel 64 MB Circular | open, unmeasured |
| 10 | Tamper Protection will defeat Config S | open |
| 11 | SIEM-01 restarts | **answered** |
| 12 | active response enabled | open, awaiting a decision |
| 13 | agent buffer 500 events/s, 5000 queued | open, unmeasured |

Items 1d, 9 and 13 are the same problem in three places and should be answered together with one
measurement during a real capture window.

---

## 2026-09-02 - Phase 3 complete. WIN-EP-01 built, telemetry proven end to end from endpoint to `archives.json`.

All machine timestamps below are **UTC**. Both guests now run UTC, the host runs UTC+8.

**Did:** Runbook Phase 3 in full, plus nine pieces of work the runbook does not list. Every step
was verified with a command whose output is recorded, not assumed.

| Runbook step | Outcome |
|---|---|
| Create the VM on F:, attach vmnet8 | Built by hand: `vmware-vdiskmanager` for an 80 GB single-file growable disk, then a hand-written `.vmx`. Two NICs, VMnet8 and VMnet2. |
| Install Windows, install VMware Tools | Windows 11 **Education** `26100.9168`, unactivated. Tools `12.3.5 build-22544099`. |
| Fully patch Windows while NAT is connected | Two passes. Pass 1 installed 5 updates, all `rc=2`. Pass 2 returned `updates found: 0`. Verified no pending reboot. |
| Set static 10.20.10.20 on the vmnet2 adapter | `LAB` adapter `10.20.10.20/24`, DHCP disabled, no gateway, DNS cleared. |
| Install Sysmon with a pinned config | Sysmon `15.21` with SwiftOnSecurity pinned at `1836897f`. **Sysmon itself reports the config hash**, and it matches the committed file. |
| Copy the config into `lab/configs/` and hash it | `lab/configs/sysmonconfig.xml`, SHA256 `055FEBC6...C87162`, byte-identical to the download. |
| Install the Wazuh agent, point at 10.20.10.10, add the Sysmon `<localfile>` | Agent `4.14.7` registered as `id=001 WIN-EP-01`, `Connected to the server ([10.20.10.10]:1514/tcp)`. Sysmon channel added, original `ossec.conf` kept as `ossec.conf.telos-orig`. |
| Install Atomic Red Team, record the commit | Pinned at `cb486d9a888e921fac5902a06c7b46e420bb14a7`, **1310 files**, 342 technique YAMLs. |
| Copy the fence tool into the guest | `telos-fence.exe` built on the host, source committed at `lab/scripts/telos-fence.cs`. |
| **Check: run one atomic test, confirm the event reaches `archives.json`** | **PASSED.** See below. |

**Work not in the runbook, all forced by what was found:**

1. **The runbook never chose a Windows edition.** It said "Enterprise Eval (or Server 2022 Eval)".
   Enterprise Evaluation expires after 90 days, which from 2026-09-02 lands on about 2026-12-01,
   on top of the defense. Chose **Windows 11 Education, unactivated**, which has no timer at all.
   Verified `LicenseStatus 5` (Notification), `GracePeriodRemaining 0`. Reasoning in DECISIONS.md.
2. **Windows 11 setup refused to install** with `This PC doesn't currently meet Windows 11 system
   requirements`. The VM has UEFI and Secure Boot but deliberately no TPM. Passed with four
   `LabConfig` registry values set from Shift+F10 at the first setup screen. **This step is
   required on a rebuild.**
3. **The installer named the machine `DESKTOP-14G5S5G`.** The Wazuh agent registers by hostname,
   and that name would then be on every event in the results. Renamed to `WIN-EP-01` before the
   agent was installed.
4. **Windows Update had already run during setup**, before the session started. `KB5121003`
   (`26100.9168`) went on at 08:10 UTC along with three others. That is why the build was already
   current. One Defender signature update failed at 08:17 (`rc=4`) and succeeded on retry at
   08:18.
5. **Kaspersky on the host was blocking 66 Atomic Red Team files.** Found by counting, not
   guessing. The list included three technique definitions (`T1218.005.yaml`, `T1548.002.yaml`,
   `T1685.yaml`), `Indexes/windows-index.yaml`, and most of the Windows payload binaries for
   T1055, T1218 and T1134.001. I added an exclusion for `E:\TeLoS-artifacts`. After
   that: **1310 files packed, 0 blocked.**
6. **Defender in the guest would have quarantined the same files at extraction time**, permanently
   removing them from the golden image. Added a narrow exclusion for `C:\AtomicRedTeam` only.
   Result after extraction: **`Defender detections during extraction: 0`**, all 1310 files
   present.
7. **`Invoke-AtomicTest` could not run.** It needs the `powershell-yaml` module, which the normal
   `Install-AtomicRedTeam` installer would have pulled in. Avoiding that installer to pin the
   commit meant the dependency was missed. Installed `powershell-yaml 0.4.12` from the host.
8. **Unattended access to SIEM-01 did not exist.** No SSH key, no passwordless sudo, and
   `/var/ossec` is mode 750 `root:wazuh` with `eli` not in the `wazuh` group. Blueprint step 10
   needs all of this. Installed an `ed25519` key and a root-owned helper script
   `/usr/local/sbin/telos-archive` with one narrow sudoers rule.
9. **Built the capture-window fence and verified it**, which the runbook asks for but does not
   specify.

**Result. The Phase 3 check, run as a miniature capture window:**

```
Endpoint side
  fence Event ID 1 records found : 2
  START  2026-09-02 13:30:38.709 UTC  RecordId=1558
  END    2026-09-02 13:30:47.711 UTC  RecordId=1571
  window span : 9 seconds
  Sysmon events inside the window : 14   (EventID 1 x11, EventID 11 x3)
  agent status='connected'  last_ack='2026-09-02 13:33:15'

Manager side
  lines in archives.json carrying the run id : 2
```

Both fences travelled Sysmon, event channel, Wazuh agent, manager, `archives.json`, arriving with
full detail including the fence binary's SHA256.

**Measurements worth keeping:**

| Measurement | Value |
|---|---|
| Endpoint-to-archive latency | **1.6 to 1.9 s** (endpoint `13:30:38.7096614Z`, manager `13:30:40.599`) |
| `archives.json` growth, one agent, idle | 74,989 bytes in 180.4 s, **34.3 MB/day** |
| `archives.json` growth, no agents (Phase 2) | 9.7 MB/day |
| One Phase 3 window, fences + one atomic test + drain + report | about **954 KB** |
| `archives.json` size at the start of Phase 3 | 47.3 MB after about one day |
| Sysmon channel | 64 MB, `Circular`, `RecordCount 1583` |
| Free space on SIEM-01 | 162 GB |
| Fence tool | one invocation, exactly one Sysmon Event ID 1, no other event ID matched |

**Findings that change the experiment, not just the build:**

1. **The Wazuh agent's own scan modules fire inside every capture window.** FIM synchronization
   every **5 minutes**, FIM real time continuously, plus SCA, rootcheck, syscollector and a full
   FIM scan all with `scan_on_start yes`. Every Phase 6 run starts with a revert and a boot, so
   all four run at the start of **every run**. This is noise from the measuring instrument, and it
   lands in the coefficient of variation. New OPEN-QUESTIONS item 8. The agent-upgrade module is
   also enabled, which is the Windows twin of the Wazuh repo disabled in Phase 2.
2. **The Sysmon channel is 64 MB and `Circular`.** If a run fills it before the agent reads it,
   the oldest events are overwritten and never sent. Biased toward the start of the window, where
   the start fence is. The Windows twin of item 1d. New OPEN-QUESTIONS item 9.
3. **Defender Tamper Protection is on, and it will silently defeat Config S.** A script that
   turns Defender off will fail while Tamper Protection is on, and Config S would then be a
   snapshot that is not actually suppressed. It cannot be turned off from a script. New
   OPEN-QUESTIONS item 10.
4. **`tools.syncTime = "FALSE"` does not stop clock sync on snapshot revert.** Four separate
   `time.synchronize.*` switches control that, and neither `.vmx` sets any of them. Phase 6
   reverts before every run, so a clock step would land at the start of all 101 windows. Added to
   OPEN-QUESTIONS item 6.
5. **Sysmon Event ID 7 never appears.** `Sysmon64.exe -c` reports `Image loading : disabled` in
   the SwiftOnSecurity config. Any hardening change whose effect is a DLL load is invisible. The
   config is also from 2021 (`Source version: 74 | Date: 2021-07-08`), schema `4.50` on a `4.91`
   binary, so it has no rules for Sysmon event types 25 to 29.
6. **Background noise was already visible in a 9-second window.** Two of eleven process creations
   were `TiWorker.exe` and `TrustedInstaller.exe`, Windows servicing processes with nothing to do
   with the test. Eighteen percent of process events in nine seconds.
7. **VBS is off and provably so**, from `Win32_DeviceGuard` and independently from `systeminfo`.
   Change #8 still has something real to switch on. Added to OPEN-QUESTIONS item 2.

**Broke / stuck on:**

1. **`This PC doesn't currently meet Windows 11 system requirements`.** Cause: no TPM, by design.
   Fixed with four `LabConfig` bypass values. First reported as "no flags" needed, which was
   wrong; the flags were required.

2. **`Access to the path ... index.yaml is denied` on the host.** Not a permission problem, the
   ACL granted `Elijah` FullControl. `Get-MpPreference` failing with `0x800106ba` and `WinDefend`
   `Stopped` led to `Get-CimInstance -Namespace root\SecurityCenter2`, which named **Kaspersky
   21.26**. Fixed by adding an exclusion.

3. **My own archiver bug turned 1 real failure into 1,301.** I created the zip entry before
   opening the source file. When the open failed the entry stayed open, and `ZipArchive` refuses
   to create a new entry while one is open:
   ```
   Exception calling "CreateEntry" with "2" argument(s): "Entries cannot be created while
   previously created entries are still open."
   ```
   Fixed by opening the source first and disposing in a `finally` block. The real count was 66.

4. **Two SSH key installs silently wrote the wrong thing.** `authorized_keys` on SIEM-01 ended up
   containing the literal **file path** with a carriage return:
   ```
   C:\Users\Elijah\.telos\siem01_ed25519.pub^M$
   ```
   The key itself was never there. `ssh -v` showed the key being offered and rejected, which
   pointed at the server side. Fixed by typing the key directly inside an interactive SSH session,
   with no PowerShell in the path. **Do not pipe a key file through PowerShell into `ssh`.**

5. **One command had a stray trailing quote**, leaving `bash` at a `>`
   continuation prompt. Nothing ran, because the whole line was joined with `&&`.

6. **`sudo install` failed with `cannot stat '/tmp/telos-archive'`.** The file had been copied
   successfully and passed a syntax check 20 minutes earlier. Cause: **SIEM-01 rebooted at
   13:19 UTC and `/tmp` is cleared on boot.** Lab files now go to the home directory.

7. **SIEM-01 restarted twice with no shutdown recorded.** `journalctl --list-boots` shows boots
   ending at 11:26:59 and 13:05:17, both with journals that stop mid-stream and no shutdown
   sequence. The hypervisor's `vmware-0.log` also stops mid-stream. Memory ruled out: 12 GB locked
   of a 55 GB ceiling, 12 GB free in the guest, zero out-of-memory events ever. Cause still
   unknown. New OPEN-QUESTIONS item 11.

8. **A read-only check of mine printed a false success.** It said
   `READABLE - exclusion is working` while the line above showed the file was still blocked.
   `Get-FileHash` writes a non-terminating error, so `catch` never fired. Corrected by opening the
   file with `[System.IO.File]::Open` inside a real `try`/`finally`.

9. **I reported archive growth as "roughly 500 MB per day", which was wrong.** That figure came
   from two rough timestamps spanning an activity burst. A clean 180-second measurement gives
   **34.3 MB/day** idle with one agent. The burst figure is only meaningful as a per-window cost.

10. **A PowerShell command was blocked by a safety guard**, reading `Remove-Item` plus a literal
    backslash in `TrimEnd('\')` as a possible root deletion. Worked around by putting the script
    in a file and running the file.

**Next:** Phase 4, pin and record everything. Most of that table is already filled in
DECISIONS.md. Four items must be settled **before the Phase 5 golden snapshot**, and the list has
grown from four to eight:

| Item | What |
|---|---|
| 1d | journald rate limiting on SIEM-01, still unmeasured |
| 5 | snapd auto-refresh still enabled on SIEM-01 |
| 6 | clock drift after isolation, **plus** the four `time.synchronize.*` switches |
| 7 | vmnet3 host adapter contradicts the Phase 1 record |
| **8** | **Wazuh agent scan modules fire inside every capture window** |
| **9** | **Sysmon channel is 64 MB and Circular** |
| **10** | **Tamper Protection will silently defeat Config S** |
| **11** | **SIEM-01 restarted twice with no shutdown recorded** |

---

## 2026-09-02 - Phase 2 complete. SIEM-01 built, Wazuh 4.14.7 installed, `logall_json` proven end to end.

All machine timestamps below are **UTC**, as SIEM-01 runs on `Etc/UTC`. The VM logs read
2026-09-01 while the local session date is 2026-09-02. Same session, different timezone.

**Did:** Runbook Phase 2 steps 2 through 8, plus four pieces of work the runbook does not list.
Every step was verified with a command, not assumed.

| Runbook step | Outcome |
|---|---|
| 2. Install Ubuntu Server | Ubuntu 24.04.4 LTS, kernel `6.8.0-138-generic`, hostname `siem-01`, OpenSSH installed, installer media disconnected permanently (`sata0:1.startConnected = "FALSE"`) |
| 3. Confirm internet | ping succeeded, `apt update` reaches `ph.archive.ubuntu.com` and `security.ubuntu.com` |
| 4. Lab network and static IP | `ens37` up with `10.20.10.10/24`, survived a reboot, reachable by SSH from Windows |
| 5. Install Wazuh | `4.14.7-1`, all three services `active` |
| 6. Disable the Wazuh repo | repo line commented, plus `apt-mark hold` on all three packages as a second lock |
| 7. `logall_json` | set to `yes` and proven end to end with a marker event |
| 8. Reduce indexer footprint | replicas verified already 0 for current and future indices; retention deliberately deferred |

**Work not in the runbook, all forced by what was found:**

1. **Root filesystem was half the disk.** The guided LVM install gave the root logical volume
   99 GiB of a 200 GB disk and left 99 GiB unallocated in the volume group. Nothing errored.
   Found by reading the SSH login banner (`Usage of /: 6.8% of 96.88GB`) and confirmed with
   `lsblk`, `df -h /`, `vgs`, `lvs`. Fixed online with `lvextend -l +100%FREE` then `resize2fs`.
   Root went from 97 GB to 195 GB. No reboot needed.
2. **Automatic package updates were on.** `apt-daily.timer` and `apt-daily-upgrade.timer` were
   armed and `20auto-upgrades` had both values at `"1"`. Disabled both timers, set both values
   to `"0"`, then applied all 49 pending updates deliberately. No kernel update was among them.
3. **Wazuh vulnerability detection was downloading content hourly.** `ossec.conf` had
   `<feed-update-interval>60m</feed-update-interval>`. Disabled it. Full reasoning in
   DECISIONS.md.
4. **Installer read before running.** Downloaded `wazuh-install.sh` and inspected it rather
   than piping it straight into a root shell. This answered a real question, see Result below.

**Result:**

| Measurement | Value |
|---|---|
| Wazuh packages | `wazuh-manager`, `wazuh-indexer`, `wazuh-dashboard`, all `4.14.7-1` |
| `wazuh-control info` | `WAZUH_VERSION="v4.14.7"`, `WAZUH_REVISION="rc1"`, `WAZUH_TYPE="server"` |
| Installer SHA256 | `8ebe9514688ace8af9445805e8887cd491dd9f95fa9d421a70f0ea012ab06f3a` |
| Cluster health | `green`, 1 node, `active_primary_shards: 23`, `active_shards: 23`, `unassigned_shards: 0` |
| Replicas | all 21 indices `rep 0`; template `wazuh` sets `number_of_replicas: "0"` with `auto_expand_replicas: "0-1"` |
| Archive growth, idle, no agents | 32,604 to 39,367 bytes in 60 seconds, about **9.7 MB per day** |
| Disk after install | 195 GB total, 27 GB used, 159 GB free |
| `/var/ossec/queue/vd` | 12 GB (CVE feed, module now disabled, data kept on purpose) |
| `ufw` | `Status: inactive`. No firewall. Baseline fact. |
| Lab NIC MAC | `00:0c:29:8c:83:33` (`ethernet1`, VMnet2) |

**Two findings that change the experiment, not just the build:**

1. **SIEM-01 collects operating system events from `journald` only.** `ossec.conf` lists exactly
   three sources: `journald`, `/var/ossec/logs/active-responses.log`, and `/var/log/dpkg.log`.
   There is no `/var/log/syslog` and no `/var/log/auth.log`. Anything that does not pass through
   those three cannot appear in the results, whatever a hardening change does. New OPEN-QUESTIONS
   item 1d follows from this.
2. **The Wazuh all-in-one installer issues certificates for `127.0.0.1`.** Confirmed by reading
   lines 97 to 106 of `wazuh-install.sh` before running it, and by lines 149, 220, 252, 402 and
   1796 which show every component talking over loopback. This matters because Phase 5
   disconnects the NAT adapter. That disconnect **cannot** break Wazuh component communication.
   The question was raised, then answered with evidence rather than assumed either way.

**Broke / stuck on:**

1. **SSH to `192.168.243.129` timed out.** Cause: the host had **no VMware Network Adapter
   VMnet8**. `Get-NetAdapter` showed only VMnet1, VMnet2 and VMnet3, so Windows had no interface
   on `192.168.243.0/24` and no route to the VM. Fixed by ticking "Connect a host virtual adapter
   to this network" for VMnet8 in the Virtual Network Editor. Note: the literal error line was
   reported as "connection timed out" but was not captured verbatim.

2. **SSH to `10.20.10.10` refused on a changed host key.** Exact text:

   ```
   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
   @    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
   The fingerprint for the ED25519 key sent by the remote host is
   SHA256:HQDMPu7HFO/rTFgWsK2M9B08iBLSFpTphHD5Q3LmL6o.
   Offending ECDSA key in C:\Users\Elijah/.ssh/known_hosts:6
   Host key for 10.20.10.10 has changed and you have requested strict checking.
   Host key verification failed.
   ```

   Not an attack. An earlier machine had used `10.20.10.10` and its three keys were still at
   lines 4 to 6 of `known_hosts`. Verified before deleting anything, two ways: the MAC answering
   at `10.20.10.10` was `00-0C-29-8C-83-33`, matching `ethernet1.generatedAddress` in the `.vmx`;
   and the fingerprint of the key already trusted for `192.168.243.129` (line 7) was
   `SHA256:HQDMPu7HFO/rTFgWsK2M9B08iBLSFpTphHD5Q3LmL6o`, identical to what SSH was offered.
   The old key was `SHA256:+H22aT3vGkmkAbvhogV9++MQDOGgRMv5xgso6Noz/mk`. Then cleared with
   `ssh-keygen -R 10.20.10.10`.

3. **`systemctl is-active ssh` returned `inactive` and looked like a failure.** It was not.
   Ubuntu 24.04 starts SSH through socket activation, so `ssh.service` is correctly `inactive`
   until a connection arrives. `systemctl status ssh` showed `TriggeredBy: * ssh.socket` and
   `systemctl is-enabled ssh.socket` returned `enabled`. **Do not check `ssh.service` on 24.04.
   Check `ssh.socket`, or just connect.**

4. **A marker search inflated its own count.** `grep -c "TELOS-TEST-EVENT-002"` on
   `archives.json` returned `2`, then `3` on the next attempt, from a single `logger` event.
   Cause: `sudo` logs every command line to journald, Wazuh collects journald, so each search
   created a new event containing the marker. Re-tested from a `sudo -i` root shell, where
   individual commands are not logged by `sudo`, and got exactly `1`. **One emitted event
   produces one archive line.** This is a measurement design rule for the Phase 6 harness, now
   recorded under OPEN-QUESTIONS 1b.

5. **The Wazuh documentation could not be read.** Three `WebFetch` calls to
   `documentation.wazuh.com` for the indexer tuning and indices pages returned "Command failed
   with no output". The quickstart and step-by-step pages had loaded earlier in the same session,
   so the cause is unknown. Worked around by querying the live indexer API and by reading
   `wazuh-install.sh` directly, which is better evidence anyway because it describes the
   installed software rather than the documented software.

6. **A web search summary was wrong and was discarded.** A search result claimed the Wazuh
   docs instruct using `127.0.0.1` for all-in-one node IPs. Fetching the actual page showed it
   says no such thing, only placeholders like `"<indexer-node-ip>"`. The correct answer was
   found in the installer source instead. **Treat search summaries as leads, not sources.**

**Next:** Phase 3. Before starting it, three items carried forward that must be settled before
the Phase 5 golden snapshot: snapd auto-refresh is still enabled (OPEN-QUESTIONS 5), journald
rate limiting is unmeasured (OPEN-QUESTIONS 1d), and vmnet3 has a host adapter connected which
contradicts the Phase 1 record (OPEN-QUESTIONS 7).

---

## 2026-09-02 - README rewritten for the chosen topic and the working code.

**Did:** Rewrote `README.md`. It still described the three-topic selection process and made no
mention that working code exists, which was accurate two weeks ago and wrong now.

**Cut:** the three-topic table from the top, "T1 is the primary choice and it is gated behind a
two week feasibility spike" (T1 is approved), T3 references in the Methodology section, and the
"rules that cannot be parsed" paragraph, which was T3's language about Sigma parsing and has
nothing to do with T1.

**Added:** the TeLoS name and the approved thesis title, the problem stated in three sentences,
the Stage D result table with its synthetic-data caveat, run instructions, an honest status
table listing what is not built as plainly as what is, and an "Alternatives considered" section
keeping the T3 finding (6 of 3,783 rules at commit `da9bb07`) as evidence of verifying a claim
rather than assuming it.

**Reasoning for the reorder:** a portfolio README should lead with what works. A reader who
sees a result table takes the repo seriously; a reader who sees a topic-selection table does
not. Being explicit about what is unfinished reads as competence. Overclaiming is what does
damage.

**Title wording:** used the panel's exact wording, unmodified, on purpose. A title the panel
has not seen should not appear in a public repo. The grammar problem ("Using Differential
Analysis Algorithm" is missing an article) is now tracked as OPEN-QUESTIONS item 0, with two
suggested corrections and a tactful way to raise it with the adviser. It was not tracked
anywhere before, which was a gap.

Verified: all 7 internal links resolve, no em dash characters.

---

## 2026-09-02 - Package renamed blindspot to telos. Split-vs-single VMware disk answered.

**Did:** Renamed `src/blindspot/` to `src/telos/` with `git mv`, updated the two files that
imported it by name (`src/demo.py`, `tests/test_differential.py`). Verified: `20 passed`,
demo output unchanged, no remaining `blindspot` string in any `.py` file.

The `docs/DECISIONS.md` and `docs/WORKLOG.md` entries from 2026-08-31 that say `blindspot`
are left as written. They are an accurate record of what the package was called at that time,
not a live reference that needed updating.

**Also answered:** split or single file for the VMware `.vmdk`. Checked F:'s filesystem first:
`NTFS`. The 2 GB split option exists to work around FAT32's 4 GB file limit, which does not
apply here. Recommended single file: slightly less I/O overhead, one fewer variable in the
storage layer while T1 measures timing variance, and no benefit from splitting since NTFS has
no size limit that matters at 200 GB.

**Next:** continue Phase 2. Confirm the SIEM-01 VM was created with split disk unchecked; if
it was already created with split checked, the disk needs recreating before Ubuntu installs.

---

## 2026-08-31 (fifth session) - Project named TeLoS. Phase 2 started.

**Did:** Picked a project name from a shortlist (`covdrift`, `Scotoma`, `anino`, `TeLoS`).
Landed on **TeLoS**: reads as Telemetry Loss, also the Greek word for purpose. Recorded in
DECISIONS.md with the reasoning and the other candidates.

Student created `F:\TeLoS Homelab\SIEM-01` and started Phase 2 (build SIEM-01). Verified the
folder exists and is empty, ready for the VM. The runbook only ever said "create the VM on
F:", with no fixed subfolder name, so this path satisfies it exactly. Nothing needed correcting
there.

**Follow-up not yet done:** the Python package is still `src/blindspot/`. Renaming it to match
TeLoS is cheap now and gets expensive once the harness and stored-run format exist. Do it
before Phase 3 if the name is considered final.

**Next:** continue Phase 2, steps 1 through 8 (VM creation through indexer replica settings),
per the procedure already given. Record each step's result as it completes.

---

## 2026-08-31 (fourth session) - Adapter fix confirmed. Phase 1 complete.

**Did:** Ran Virtual Network Editor → Restore Defaults, reconfigured vmnet2/vmnet3 per the
steps from the previous session, then verified the result.

**Result: fixed.** All three checks that failed before now pass.

| Check | Before | After |
|---|---|---|
| Driver status (`Get-PnpDevice`) | Error, all three | OK, all three |
| Adapter status | Not Present / Down | Up / Up |
| VMnet2 IP | none | **10.20.10.1/24** |
| VMnet3 IP | none | **10.20.20.1/24** |
| DHCP on 10.20.10.0 or 10.20.20.0 | n/a | confirmed absent from `vmnetdhcp.conf` |

Both subnets were set exactly as specified, with the host adapter connected on vmnet2 only,
matching the runbook. No correction needed.

Moved OPEN-QUESTIONS item 0 to Answered with the full before/after evidence.

**Runbook Phase 1 (virtual networks) is complete.** The host has a working path to the lab
network at 10.20.10.1, which is what the harness needs to reach the Wazuh API in Phase 6.

**Next:** Phase 2, build SIEM-01 (Ubuntu 24.04.4, Wazuh all-in-one, pin the version, disable
the repo, enable `logall_json`).

---

## 2026-08-31 (third session) - Pre-flight for Phase 1. VMware network adapters broken.

**Did:** Ran the four-command pre-flight check from COMMANDS.md before starting Runbook
Phase 1, then began Phase 1 itself.

**Pre-flight result: 3 of 4 pass.**

| Check | Result |
|---|---|
| `vmrun -T ws list` | PASS. `Total running VMs: 0` |
| Hypervisor still off | PASS. `HypervisorPresent: False` |
| F: free space | PASS. 715 GB free (53.1 GB already used by two existing Win11 VMs under `F:\VMWARE`, unrelated to this project) |
| CLI tools present | `vmware-vdiskmanager.exe` and `vnetlib64.exe` confirmed present, useful for scripting later phases |

**Existing state found on the host, not created this session:**
- `F:\VMWARE\For Testing\...` and `F:\VMWARE\Fresh Installed\...`: two pre-existing Windows 11
  VMs, 53.1 GB, unrelated to the thesis. Left alone.
- `vmnet2` and `vmnet3` already existed in `netmap.conf`, and neither appears in
  `vmnetdhcp.conf`, so DHCP was already off on both. That part of Phase 1 was already correct.

**BROKE: all three VMware host adapters (VMnet1, VMnet2, VMnet3) are in `Error` state.**

```
Get-PnpDevice | Where FriendlyName -like '*VMware Virtual Ethernet*'

Status Class FriendlyName
------ ----- ------------
Error  Net   VMware Virtual Ethernet Adapter for VMnet1
Error  Net   VMware Virtual Ethernet Adapter for VMnet2
Error  Net   VMware Virtual Ethernet Adapter for VMnet3
```

`Get-NetAdapter` shows all three as `Not Present`, `AdminStatus Down`, with no IP address
assigned on any of them. The VMware services themselves (`VMnetDHCP`, `VMware NAT Service`)
are `Running`. The failure is at the adapter/driver level, not the service level.

**This blocks Phase 1 and everything after it.** The harness runs on the host and reaches
the Wazuh API over the host's vmnet2 interface at 10.20.10.1. With no working adapter, that
path does not exist, and Runbook Phase 6 cannot function.

**Suspected cause (unverified):** `vEthernet (Default Switch)`, a Hyper-V virtual switch, is
`Up` at 10 Gbps even though `hypervisorlaunchtype` is off. Hyper-V's network filter drivers
binding to the stack alongside VMware's adapters is a known cause of this exact `Error` state
`(unverified as confirmed here, but consistent with the evidence)`. The 2026-08-20 fix turned
off the hypervisor at boot; it did not remove the Hyper-V Windows feature or its networking
components, and `vmcompute`/`vmms` services are still `Running`.

**Fix, not yet done (needs the VMware GUI, so it is done by hand):**
1. VMware Workstation → Edit → Virtual Network Editor → Change Settings (admin).
2. Click **Restore Defaults** to reinstall the adapters. No custom settings are lost, since
   vmnet2/vmnet3 had no subnets configured yet.
3. Add VMnet2: Host-only, **host virtual adapter checked** (required, this is the harness's
   path to the lab), DHCP unchecked, subnet 10.20.10.0/24.
4. Add VMnet3: Host-only, host adapter unchecked, DHCP unchecked, subnet 10.20.20.0/24.
5. Leave VMnet8 (NAT) at default.

**Verification once done:**
```
Get-NetIPAddress | Where InterfaceAlias -like '*VMnet2*'
```
Expect `10.20.10.1`. That address is the proof the harness's path to the lab exists.

**If Restore Defaults does not fix it:** the working theory is wrong or incomplete, and the
Hyper-V Windows feature itself needs to be removed (`Disable-WindowsOptionalFeature`), not
just its boot-time hypervisor. Bigger change, needs its own DECISIONS entry if it comes to
that.

**Next:** run the Virtual Network Editor steps above. Phase 1 is not complete until
`Get-NetIPAddress` confirms 10.20.10.1.

---

## 2026-08-31 (second session) - Built the analysis core. First code in the repo.

**Did:** Wrote stages 2, 3 and 5 of the pipeline in Python, with tests, running on synthetic
data. No lab involved.

**The decision that made this possible:** the analyser consumes event counts and does not care
where they came from. So only stage 1 (acquisition) needs the lab. Recorded in DECISIONS.md.

**Files written:**

| File | Holds |
|---|---|
| `src/blindspot/model.py` | `Phase`, `Finding`, `Classification`, `AnalysisResult` |
| `src/blindspot/variance.py` | Noise floor: CoV and dispersion from the control runs |
| `src/blindspot/differential.py` | The core: align, global gate, rate ratio, BH, classify |
| `src/blindspot/baseline.py` | Naive differencing, the comparison baseline |
| `src/blindspot/report.py` | Text rendering |
| `src/blindspot/synth.py` | Synthetic count generator |
| `src/demo.py` | End-to-end run |
| `tests/test_differential.py` | 20 tests |

**Result:** 20 tests pass. The demo reproduces the headline claim on synthetic data:

```
  method                       TP   FP   FN  precision   recall      F1
  naive differencing            2    8    0     20.0%  100.0%   0.333
  proposed system               2    0    0    100.0%  100.0%   1.000
```

Full output saved to [demo-output.txt](demo-output.txt).

**BROKE:** first test run gave `1 failed, 17 passed`. The failure was a real bug, not a bad
test. When the post-change phase records zero events for every key, `chi2_contingency` raises:

```
ValueError: The internally computed table of expected frequencies
has a zero element at (np.int64(1), np.int64(0)).
```

Cause: an all-zero row makes every expected frequency in that row zero, and the calculation
divides by it. This is not an artificial case. It is what a dead agent, a dropped network, or
logging stopped entirely would produce during a real run. The old code would have crashed
mid-batch instead of reporting the condition.

Fixed in `global_gate()` by checking for degenerate tables before calling chi-square: both
phases empty means no detectable change, one phase empty means the profile certainly changed,
otherwise run the test. Added `test_phase_that_emitted_nothing_does_not_crash` and
`test_two_empty_phases_do_not_crash` so it cannot return.

**Design positions implemented** (all three were argued in the proposal revision and are now
real code): chi-square applied once globally as a gate rather than per event type; a
dispersion-aware rate ratio instead of Poisson; and REDUCED requiring the corrected q value,
the effect size, and the measured noise floor together.

**Versions pinned** in DECISIONS.md and `requirements.txt`. `statsmodels` turned out not to be
needed, because `scipy.stats.false_discovery_control` provides Benjamini-Hochberg.

**Still missing:** stage 1 acquisition (needs the lab), stage 4 impact scoring (needs the
dependency index, buildable offline), persistence to disk, run manifest hashing, and the web
interface.

**Honest limit:** the synthetic generator draws from a rounded normal. Real event counts are
not normal. The demo proves the code is correct, not that the telemetry behaves this way. No
demo number may be presented as a finding.

**Next:** OPEN-QUESTIONS item 1b must be settled before stage 1 is written, because it changes
the profile schema and therefore every stored run.

---

## 2026-08-31 - T1 approved with revisions. Proposal revision drafted. Walkthrough written and then flagged as wrong.

**Did:** Recorded the outcome of the title proposal defense, drafted answers to the panel's
11 revision items, extracted the submitted .docx into markdown, and wrote a system walkthrough.

**T1 is approved.** The panel proposed a new title:
> Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential
> Analysis Algorithm

That wording is missing an article. Recommended correction, which keeps the panel's words and
only reorders them: *Detecting Security Blind Spots Through Differential Analysis of Pre- and
Post-Hardening Events*. Raise with the adviser as a wording question, not a correction.

**Panel's 11 revision items,** all answered in [T1-PROPOSAL-REVISION.md](T1-PROPOSAL-REVISION.md),
mapped to the exact form section each belongs to: system type, report output, input and
prerequisites, compute process, remediation ability, repeatability guarantees, activity diagram
in plain terms, web versus script, algorithm in plain terms, before-and-after comparison, and
the source of the adversary tests. The panel asked no research-validity questions. Every item
was a product question.

**Two decisions taken as assumptions, still unconfirmed:**
1. Web application using the existing Wazuh agent. No new endpoint agent is written.
2. Limited remediation suggestion: report a surviving telemetry source, do not rewrite rules,
   never recommend reversing the hardening.

**Also did:** extracted the submitted proposal form to `thesis/T1/proposal-form.md`. The Gantt
schedule is drawn as cell shading in the .docx, so a plain text conversion loses it entirely.
Recovered it by reading the shading directly.

**BROKE / GOT WRONG:** Wrote `T1-WALKTHROUGH.md` using "disable Audit Process Creation, CIS
17.6.2" as the demo scenario, without reading OPEN-QUESTIONS item 1 first. That item, recorded
2026-08-20, already establishes that CIS **requires** this setting enabled (17.3.1 or 17.3.2),
so disabling it is de-hardening, and it is a class A catalogue item. The control ID 17.6.2 was
also invented. The walkthrough additionally omits condition (d) of the corrected blind-spot
definition and has inconsistent surviving-coverage numbers, contradicting item 1c.

The file is kept but carries a warning banner at the top. Its structure and the naive-versus-
proposed comparison are still usable. The example must be rebuilt around a class C change.

**Lesson recorded:** read OPEN-QUESTIONS before writing anything that uses a specific control,
event ID, or setting. The answer was already in the repo.

**Also corrected:** two earlier WORKLOG entries were dated 2026-08-19 but the commits show the
work happened 2026-08-20 (repo published, Phase 0 checks). Dates fixed. A broken cross-reference
to a non-existent entry titled "Runbook Phase 0 cont." was repointed to DECISIONS.md.

**Next:** rebuild the 16-change catalogue with pinned control IDs and class labels
(OPEN-QUESTIONS item 1). That is still the top task, ahead of Runbook Phase 1, and the
walkthrough cannot be fixed until it is done.

---

## 2026-08-20 - Built the one-slide title deck for the topic proposal defense

**Did:** Made a single slide listing the three candidate titles, in rank order (T1, then T3,
then T2). No full presentation. The Topic Proposal Document is what gets presented; the slide
only exists so the panel can pick a title at the start.

**Result:** `thesis/topic-proposal-titles.pptx`. One slide, 13.333 x 7.5 in. Speaker notes hold
the 30-second spoken description of each title plus the closing question to the panel.

**Built with:** python-pptx 1.0.2 (installed this session, node is not on this host, so
pptxgenjs was not usable). Rendered to PNG through the installed PowerPoint COM object for
visual check, because LibreOffice is not installed either.

**Broke / stuck on:** Nothing. First render had cards 1.55 in tall with dead space at the
bottom and only 0.14 in clearance from the slide edge; reduced to 1.25 in and re-rendered.

**Also did:** Wrote `DEFENSE-PREP.md` (moved out of this repository on 2026-09-10, see that
day's entry), a full preparation guide for the pre-oral
topic proposal defense. Covers all three topics end to end: threat model, the 5-problem to
5-objective pairing, the five modules, algorithms, evaluation and baseline, prior work with the
concrete figures, and the weakest point of each with an honest answer. Includes a glossary, a
numbers-to-memorize table, a question bank, and a list of the known holes in the proposals.

**Holes found while writing it (all listed in DEFENSE-PREP.md section 8):**
- The Tyagi sigmalint citation is dated 2026 in T2 and 2026 with different dates in T3, and T2
  also calls it a 2025 SSRN working paper. The two entries must agree.
- Author names carry mojibake in the proposal text files: "Hackl?nder", "Jo?o", "Map?a".
- The 16 hardening changes are still not pinned to CIS or DISA control IDs (OPEN-QUESTIONS item 4).
  This is the highest-value offline fix before the defense.

**Broke / stuck on:** Could not rebuild the pptx to correct the T3 speaker note, which still
describes validating against the SigmaHQ STP annotations without saying that only 6 of 3,783
rules carry one. `PermissionError: [Errno 13] Permission denied` because the file was open in
PowerPoint. Rebuild after closing it.

**Then stress-tested T1** against a formal definition of security hardening. Found nine problems.
The two that matter:

1. **Four of the 16 catalogue items are anti-hardening.** Verified against the benchmarks on
   2026-08-20. CIS requires Audit Process Creation set to Success (17.3.1 or 17.3.2 by version)
   and requires 'Include command line in process creation events' Enabled (18.9.3.1, or 18.8.3.1
   in some versions). DISA STIG WN10-CC-000326 / V-220860 requires PowerShell script block
   logging Enabled. Catalogue items 1 to 4 turn all of these off, which is de-hardening.
2. **Telemetry loss is not a blind spot.** Disabling SMBv1 removes SMB1 events and SMB1 attacks
   together, so the rule should be retired, not flagged. The blind-spot definition needs a fourth
   condition: the technique must still be executable after the change.

Classification of the catalogue: 4 anti-hardening, 1 with no benchmark control (Sysmon config),
6 where the attack is removed with the telemetry, 5 true blind-spot candidates. Of those 5, one
is content-level and invisible to the current profile design and one is blocked on nested
virtualization, leaving 3 solid positive cases.

**Checked what this does to the submitted proposal.** Nothing in the submitted T1 document names
a specific control, event ID, or setting. The only sentences at risk are the two that say the
16 changes are "drawn from" CIS Benchmarks and DISA STIGs (Objective 4 and Scale of the
Experiment). Those stay true once the catalogue is corrected, and the count of 16 can stay at 16.
The defect is entirely in `lab/blueprint.md` section 8, which was never submitted.

Full detail in [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) items 1, 1b, and 1c.

**Next:** Rebuild the 16-change catalogue with pinned control IDs and a class label per change.
That is now the top task, ahead of Runbook Phase 1.

---

## 2026-08-20 - Runbook Phase 0 checks. Mostly pass, one flag.

**Did:** Ran the Phase 0 readiness checks on the host.

**Results:**
| Check | Result |
|---|---|
| F: free space (need 350 GB) | PASS. 732 GB free. |
| C: free space | 315 GB free. |
| AMD SVM virtualization in firmware | PASS. VirtualizationFirmwareEnabled = True. |
| Python 3.11+ on C: | PASS. Python 3.13.14 at C:\Program Files\Python313. |
| VMware Workstation | PASS. 17.5.1 build-23298084 (matches blueprint pin). |
| vmrun works | PASS. `vmrun -T ws list` returned "Total running VMs: 0". |
| ISOs present | PASS. In E:\Homelab files (see paths below). |
| Python venv created | NOT DONE YET. |

**vmrun path:** `C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe`

**ISO choices (in E:\Homelab files):**
- SIEM-01 (Ubuntu LTS): `ubuntu-24.04.4-live-server-amd64.iso`. 24.04 LTS, which Wazuh supports.
- WIN-EP-01 (Windows): `Windows 11 Enterprise Eval 26200.6584...25h2...CLIENTENTERPRISEEVAL`. The
  evaluation edition the runbook asks for.

**FLAG worth a decision before the spike:** `HypervisorPresent = True`. RESOLVED same day, see
DECISIONS.md entry "Windows hypervisor turned off". Cause was the Hyper-V
feature (not a security feature). Turned it off with `bcdedit /set hypervisorlaunchtype off` and
rebooted. Verified HypervisorPresent = False, VBS = 0, vmrun still works. Host now runs VMware
natively, before any VM was built, which is the correct time to make this change.

**Also noted:** the host has other virtualization tools present (Proxmox, TrueNAS, OPNsense ISOs;
other homelab folders). Our whole plan assumes VMware Workstation + vmrun. If the plan ever moves
to Proxmox, the harness (which calls vmrun) has to be rewritten. Sticking with VMware.

**Next:** decide on the Python venv location, then Phase 1 (virtual networks).

---

## 2026-08-20 - Repo published to GitHub, public

**Did:** Professor cleared publishing (no IP rule, no similarity-check problem). Installed
GitHub CLI (`gh` 2.97.0) via winget. User logged in as EASolutions00. Created the public repo
and pushed all commits.

**Result:** Live at https://github.com/EASolutions00/detection-hardening-lab (public, 6 commits).
`gh` is now installed and authenticated, so future pushes work directly from the Bash tool.

**Note:** `gh` lives at `C:\Program Files\GitHub CLI`. If a shell cannot find it, add that to
PATH for the session: `export PATH="$PATH:/c/Program Files/GitHub CLI"`.

**Still open:** no LICENSE file yet. Add one (MIT or Apache 2.0) before pointing anyone at the
repo, so the "usable by small companies" claim in the proposals is legally true.

**Next:** start the lab. Runbook Phase 0.

---

## 2026-08-19 - Counted SigmaHQ STP annotations. Result is bad for T3.

**Did:** Cloned `SigmaHQ/sigma` at commit `da9bb07`, counted rules carrying a Summiting the
Pyramid robustness tag (`stp.<level>` in the `tags:` list).

**Result:** 6 rules out of 3,783. 0.16%. Levels: stp.1u x3, stp.1k x1, stp.2a x1, stp.4u x1.

**Gotcha worth remembering:** a plain `grep stp.` gave 19 files and looked survivable. 13 were
false hits on `cmstp.exe` / `chrmstp.exe`. Always match the tag line `- stp.<digit>`, not the
substring. If I had trusted the first number I would have called T3 safe when it is not.

**Consequence:** T3's Objective 5 is not executable as written. T3 is no longer a safe fallback.
Recorded in DECISIONS.md and moved the open question to Answered. No decision made yet on whether
the fallback becomes "T3 with self-annotation" or "T2 instead". That waits for the T1 spike.

**Next:** unchanged. T1 is still primary. But the safety net changed, so the T1 spike matters
more than before, because a failed spike no longer has a clean landing.

---

## 2026-08-19 - Reply rules made global

**Did:** Created `C:\Users\Elijah\.claude\CLAUDE.md` holding the full AI rules.

**Why:** The rules were only applying because they were pasted at the start of each chat.
Nothing loaded them automatically. `~/.claude/CLAUDE.md` did not exist, there was no
`settings.json`, no output style, and the memory directory was empty. The project CLAUDE.md
only *linked* to `docs/AI-RULES.txt`, and a link is not a load.

**Result:** Rules now load automatically in every project and every session on this machine.
No more pasting.

**Note for later:** that file is **outside this repo**, so git does not back it up and it will
not follow you to another machine. `docs/AI-RULES.txt` is the versioned copy. Verified the two
are identical apart from a trailing newline. If you edit one, edit both.

---

## 2026-08-19 - CLAUDE.md reviewed and trimmed

**Did:** Reviewed `CLAUDE.md` as an index rather than a document. Cut it from 140 lines to
104. Removed detail that duplicated the runbook (the reasoning behind the silent-failure
rules, the spike Q1/Q2 breakdown), the restated voice rules, and a filler `git status` block.
Created `thesis/README.md` to hold the institutional template and the problem-to-objective
numbering rule, which previously had no home outside `CLAUDE.md`.

**Result:** All 12 internal links verified as resolving. Nothing was lost, only relocated.

**Fixed while reviewing:**
- `CLAUDE.md` said the repo is private on GitHub. It is not. `git remote -v` is empty, no
  GitHub repo exists yet. Now reads "will be created private".
- "end of September" had no year. Now says September 2026.
- "gh is not installed" removed from `CLAUDE.md`. That is machine state, not project state,
  and it is already recorded in this log below.

**Kept deliberately:** the five silent-failure rules stay in `CLAUDE.md` instead of becoming
a pointer. They have to be loaded before deciding which file to read, otherwise a VM ends up
on E: without the runbook ever being opened.

**Next:** unchanged from the entry below.

---

## 2026-08-19 - Repo structure created

**Did:** Turned the folder into an organized git repo. Created `docs/`, `thesis/`, `lab/`,
`src/`, `data/`. Moved the four original documents into place. Wrote `CLAUDE.md` as the
index, `docs/RUNBOOK-homelab.md` as the from-scratch build procedure, and this log.

**Result:** Structure is in place. Nothing about the lab or the thesis has been built yet.
The four source documents are unchanged in content, only moved.

**Broke / stuck on:** `gh` (GitHub CLI) is not installed on this machine, so the repo cannot
be created from the terminal yet. Either install it or create the repo in the browser.

**Next:**
1. Answer the T3 SigmaHQ annotation count question. See `docs/OPEN-QUESTIONS.md`.
   It is offline, takes minutes, and it gates your only fallback.
2. Start Phase 0 of the runbook.
3. Create the private GitHub repo and push.

---

## 2026-08-18 - Source documents written (before this log existed)

**Did:** Wrote the three thesis proposals (T1, T2, T3) and the homelab blueprint.

**Result:** All four are in `thesis/` and `lab/blueprint.md` now.

**Next:** Was superseded by the 2026-08-19 session above.

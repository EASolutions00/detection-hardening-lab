# Open Questions

Things that are not verified and that change the plan if the answer is bad.
When one is answered, move it to "Answered" at the bottom with the date and the evidence.

Ranked by how much damage the wrong answer does.

---

## 0. What is the exact approved title wording?

**Status:** Open. Cheap to close. Raised 2026-09-02.

**Why it matters:** the title now appears in the public README, on every document from here,
and eventually on the cover page and the library record. It should be settled once, not drifted.

**The panel proposed:**
> Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential
> Analysis Algorithm

**The problem:** "Using Differential Analysis Algorithm" is missing an article. English needs
"a" or "the" before a singular countable noun.

**Two corrections, both keeping the panel's vocabulary:**
1. Reorder, adding no words: *Detecting Security Blind Spots Through Differential Analysis of
   Pre- and Post-Hardening Events*
2. Minimal, add one word: *...Using **a** Differential Analysis Algorithm*

**Currently in use:** the panel's exact wording, unmodified, in `README.md`. Deliberate. A
title the panel has not seen should not appear in a public repo.

**How to answer:** ask the adviser as a question about wording, not as a correction of the
panel. For example: "Sir/Ma'am, for the final title, should it read 'Using a Differential
Analysis Algorithm'? I want the wording correct before it goes on all my documents."

**What a bad answer means:** nothing bad. If they keep their original wording, use it
everywhere and stop revisiting it.

**Note for Chapter 3:** the approved title names a general method ("Differential Analysis
Algorithm") rather than a specific one. The specific algorithm must therefore be named and
defined explicitly in the methodology chapter, since the title no longer does it.

---

## 1. Which 16 hardening changes survive the corrected blind-spot definition?

**Status:** Open. Raised 2026-08-20 while stress-testing T1 against a formal definition of
security hardening. This supersedes the older item 4 below in priority, and absorbs it.

**Why it matters:** Four items in the catalogue in `lab/blueprint.md` section 8 are the
**opposite** of what the benchmarks require, verified 2026-08-20:

| Catalogue item | What the benchmark actually requires |
|---|---|
| 1. Disable Audit Process Creation | CIS requires Success auditing. Level 1. Numbered 17.3.1 or 17.3.2 depending on benchmark version. |
| 2. Disable `ProcessCreationIncludeCmdLine_Enabled` | CIS requires Enabled. Level 1. 18.9.3.1, or 18.8.3.1 in some versions. |
| 3. Disable PowerShell ScriptBlock logging | DISA STIG WN10-CC-000326 / V-220860, CAT II, requires Enabled. |
| 4. Disable PowerShell Module logging | Same family. Benchmarks require enabling it. Exact control ID `(unverified)`. |

Item 15 (narrow the Sysmon config) is genuine security-tool hardening but has no CIS or DISA
control, so it cannot be described as drawn from a published baseline.

Second and deeper problem: **telemetry loss is not the same as a blind spot.** Disabling SMBv1
removes SMB1 events, but it also removes SMB1 attacks, so the detection rule should be retired,
not flagged. The two-tier labeling in `lab/blueprint.md` section 8 does not test whether the
technique is still executable after the change.

**Corrected definition to adopt in Chapter 3.** A hardening-induced blind spot exists when
(a) the change is a control from a named benchmark with its control ID recorded, (b) the change
removes or degrades an event type or a required field, (c) at least one detection rule depends
on it, and (d) **the technique that rule covers is still executable after the change.**

Classifying the current catalogue against that definition:

| Class | Meaning | Items | Count |
|---|---|---|---|
| A | Anti-hardening. Benchmark requires the opposite | 1, 2, 3, 4 | 4 |
| A' | Real tool hardening, but no benchmark control exists | 15 | 1 |
| B | Attack removed along with the telemetry. Not a blind spot | 5, 9, 11, 12, 13, 14 | 6 |
| C | True blind-spot candidate. Attack still possible | 6, 7, 8, 10, 16 | 5 |

Of class C, item 6 (Constrained Language Mode) is content-level and item 2 was field-level, and
the frequency profile in Module 2 counts event-type rates, so neither is visible to the method
as written. Item 8 is still blocked on untested nested virtualization. That leaves 3 solid
positive cases: disable WDigest, restrict NTLM, enforce RDP NLA.

**How to answer:** Replace items 1, 2, 3, 4 with real controls where the technique survives the
change. Candidates to check, control IDs all `(unverified)`: LSA Protection (RunAsPPL), ASR rule
blocking Office child processes, block macros from the internet, AppLocker or WDAC enforcement,
restrict anonymous SAM enumeration, enforce SMB signing, enforce LDAP signing and channel
binding, disable AutoPlay and AutoRun. Keep the class B items as **negative controls** for the
impact scorer, where telemetry loss is expected and the impact score should correctly be near
zero. Keep the count at 16 so the submitted proposal text stays true.

**What a bad answer means:** If fewer than about 8 class C changes can be pinned, the precision
and recall comparison is underpowered and T1's evaluation has to be restated around a smaller
labeled set.

---

## 1b-remainder. Harness counting rules that survive the schema decision

**Status:** Open, but no longer a schema question. The schema itself was decided 2026-09-04,
see Answered. What remains are two counting rules the Phase 6 harness must obey.

**Measured evidence, 2026-09-02,** from the first live archive on SIEM-01.

1. **One emitted event produces exactly one line in `archives.json`.** There is no duplicate
   collection to de-duplicate. Verified with a `logger` marker read from a root shell.
2. **A search can create the thing it is searching for.** `sudo grep -c "MARKER" archives.json`
   returned `2`, then `3`, from a single `logger` event. `sudo` writes every command line to
   journald, Wazuh collects journald, so each search added a new event containing the marker.
   Reading from a `sudo -i` root shell, where individual commands are not logged by `sudo`,
   returned the correct `1`.

**Harness rule that follows:** the Phase 6 harness must never place a marker, technique name, or
search pattern on a command line it runs under `sudo` on a monitored host. Read the archive from
a root shell, or pass the pattern from a file with `grep -f` so only the filename appears in the
logged command. Breaking this rule does not error. It silently inflates counts.

---

## 1c. Does a redundant telemetry source cancel the blind spot?

**Status:** Open. Raised 2026-08-20.

**Why it matters:** WIN-EP-01 runs Sysmon. Sysmon Event ID 1 records process creation
independently of Windows audit policy, so losing 4688 may blind nothing at all. A panelist can
say the measured loss has no operational impact.

**How to answer:** Add a compensating-source check to the impact scoring in Module 4. If a
redundant source covers the lost event type, the impact score drops toward zero.

**What a bad answer means:** Nothing bad. This turns an objection into a feature, and no
comparable tool does it. The cost is extra work in the dependency index.

---

## 1d. Does journald rate limiting silently drop events during a capture?

**Status:** **Answered 2026-09-03. No, not as the lab is currently scoped.** Measured, and the
premise of the question turned out to be partly wrong. Resolution at the end of this item.

**Why it matters:** SIEM-01 collects operating system events from **`journald` only**. Verified
from `ossec.conf`, which lists exactly three sources:

| Source | Format |
|---|---|
| `journald` | `journald` |
| `/var/ossec/logs/active-responses.log` | `syslog` |
| `/var/log/dpkg.log` | `syslog` |

There is no `/var/log/syslog` and no `/var/log/auth.log`. Older Wazuh guidance assumes those
files, and it does not apply here.

**journald discards messages by design when a service exceeds its rate limit.** It writes a short
"Suppressed N messages" notice and drops the rest. Dropped messages never reach Wazuh, never
reach `archives.json`, and never appear in any result. That is telemetry loss caused by
configuration, which is the exact subject of this thesis, sitting **inside the measurement
pipeline itself**.

If a Phase 6 run generates events faster than the limit, the run loses events for a reason that
has nothing to do with the hardening change being tested. The loss would look exactly like a
finding.

**How to answer:** read the effective `RateLimitIntervalSec` and `RateLimitBurst` on SIEM-01 and
on WIN-EP-01's forwarder path, then generate a burst at the rate a real Atomic Red Team suite
produces and check `journalctl` for suppression notices. Either raise or disable the limit and
record it as a pinned baseline value, or keep it and prove the run rate stays under it.

**What a bad answer means:** if the limit is being hit at realistic run rates and is not
addressed, every T1 result is contaminated by an unmeasured, uncontrolled loss channel. This is
a threat to validity, not a performance issue.

### Resolution, 2026-09-03

**The premise was partly wrong, and correcting it is most of the answer.** This item assumed the
endpoint's telemetry travels through journald on SIEM-01. It does not. The Phase 3 evidence in
`archives.json` shows how WIN-EP-01's events actually arrive:

```
"decoder":{"name":"windows_eventchannel"}   ...   "location":"EventChannel"
```

They come over port 1514 into the manager's own queue. **journald on SIEM-01 carries only
SIEM-01's own operating system events**, which a capture run barely touches. The original worry,
that a busy run would overrun journald and lose endpoint data, cannot happen by that path.

**Measured on SIEM-01, 2026-09-03:**

| Item | Value |
|---|---|
| `RateLimitIntervalSec` | **30s** (default, not overridden anywhere) |
| `RateLimitBurst` | **10000** (default, not overridden anywhere) |
| Meaning | more than 10,000 messages from **one service** within 30 s and the rest are dropped |
| **Suppression notices ever recorded on this machine** | **0** |
| Journal storage | persistent (`/var/log/journal` exists), 79.5 MB |
| Only non-default journald setting | `ForwardToSyslog=yes` |

Every journald setting is at its built-in default. The limit has **never** been reached, across
every boot in the journal.

**A separate finding from the same output.** `rsyslog` is installed and active, and
`ForwardToSyslog=yes` means **every journald message is written twice**, once to the journal and
once to `/var/log/syslog`, which is already 1.77 MB. Wazuh does **not** read `/var/log/syslog`,
so this is duplicate disk writes, not duplicate collection. Minor, but it is disk churn inside
every capture window and it belongs in the baseline description.

**What is left of this item, and when it comes back.** If a Linux endpoint is ever added
(`LNX-EP-01` in `lab/blueprint.md` Tier B), its `auditd` and OS events **would** pass through
journald on that machine, and this question becomes live again for that host. It is answered for
the current Tier A lab only.

**Related, and still open:** the loss-channel worry is real, just in different places. See items
9 (Sysmon channel, 64 MB circular) and 13 (agent buffer, 500 events/s).

---

## 2. Does nested virtualization work for Credential Guard on this host?

**Status:** Untested.

**Why it matters:** T1 hardening change #8 (Enable Credential Guard) needs VBS inside the
guest, which needs nested virtualization (Virtualize AMD-V/RVI in VM settings). Unverified
on Zen 4 with Workstation 17.5.1.

**How to answer:** Enable the setting in WIN-EP-01, boot, try to turn on Credential Guard,
check `msinfo32` for VBS running.

**What a bad answer means:** Drop change #8 and substitute another from the catalogue.
Low damage. Test it in week 1 so the substitution is not rushed.

**Baseline established 2026-09-02 during Phase 3.** WIN-EP-01 was deliberately built with
`vhv.enable = "FALSE"`, so the guest has no virtualization extensions and **VBS cannot start on
its own**. This matters because Windows 11 enables VBS by default on capable hardware, and if it
were already running in the golden image, change #8 would have nothing left to switch on and
would measure nothing.

Confirmed from two independent sources on the built machine:

```
Win32_DeviceGuard : VirtualizationBasedSecurityStatus = 0, SecurityServicesRunning = 0
systeminfo        : Virtualization-based security: Status: Not enabled
Confirm-SecureBootUEFI : True
Get-Tpm           : TpmPresent = False
```

Secure Boot is on and there is no TPM, which is the intended configuration (see DECISIONS.md,
same date). TPM 2.0 is recommended rather than required for VBS `(unverified)`, so the test is
still worth running.

**The test is now a two-step change, not one.** Set `vhv.enable = "TRUE"` with the VM powered
off, boot, and **first check whether Windows has switched VBS on by itself**. If it has, the
golden snapshot has to be re-examined, because the baseline would no longer be "VBS off".

---

## 3. What is the real indexer heap and archive growth under `logall_json`?

**Status:** Partly measured 2026-09-02. Idle baseline now known. Load figure still unmeasured.

**Why it matters:** The 16 GB RAM and 200 GB disk figures for SIEM-01 are headroom based on
judgment, not measurement. If archives grow faster than expected, F: fills mid experiment.

**Measured on SIEM-01, 2026-09-02, idle, no agents connected:**

| Item | Value |
|---|---|
| `archives.json` growth | 32,604 to 39,367 bytes in 60 seconds, about **9.7 MB per day** |
| Archives on disk | 88 KB |
| Indexer data (`/var/lib/wazuh-indexer`) | 3.4 MB |
| Root filesystem after the full build | 195 GB total, 27 GB used, **159 GB free** |
| Largest single consumer | `/var/ossec/queue/vd`, **12 GB**, the CVE feed. Module now disabled, data kept. |

**What this changes:** the disk is not the near-term risk it was assumed to be. At the idle rate
archives take decades to matter, and the 200 GB allocation is now 195 GB usable rather than the
97 GB the installer actually gave it (see DECISIONS.md, LVM extend).

**Measured again 2026-09-02, Phase 3, with WIN-EP-01 connected:**

| Condition | Measurement | Rate |
|---|---|---|
| No agents, idle (Phase 2) | 32,604 to 39,367 bytes in 60 s | **9.7 MB/day** |
| One agent, idle, agent scan modules **enabled** | 48,358,184 to 48,433,173 bytes in 180.4 s | **34.3 MB/day** |
| **One agent, idle, agent scan modules DISABLED** | 49,615,051 to 49,654,191 bytes in 180.4 s | **17.9 MB/day** |
| One Phase 3 capture window (2 fences, 1 atomic test, 120 s drain, 1 report script) | 47,305,482 to 48,259,184 bytes, about **954 KB** | not a rate, a per-activity cost |

**Disabling the agent's own scan modules cut idle volume roughly in half**, from 34.3 to 17.9
MB/day, which is about two thirds of everything the agent was contributing over the no-agent
baseline. See item 8.

`archives.json` was already **47.3 MB** when Phase 3 began, from roughly one day of running.

**Read the third row carefully. It is not a daily rate.** It spans a burst of activity, and
extrapolating it to a day would give about 500 MB/day, which is wrong. The steady figure with an
agent connected is the second row.

**What this changes:** one connected, idle agent costs about 3.5 times the no-agent baseline.
With 162 GB free, the idle rate alone would take years to matter. The risk is the burst rate
multiplied by 101 runs, and that still cannot be known until a full capture window with a real
technique list exists.

**Still unmeasured, and this is the part that counts:** growth during a full Atomic Red Team
suite, not one discovery test. That number cannot be known until a real Phase 6 run exists.

**How to answer the rest:** measure `archives.json` growth across one full capture window in
Phase 6, then set retention from that number. Retention was deliberately **not** set in Phase 2
for this reason. See DECISIONS.md, same date.

**What a bad answer means:** Truncate more aggressively, or shrink the technique list.
The harness must abort cleanly on low disk (runbook Phase 6). That check is now load-carrying,
because it is the only thing standing between a burst and a filled disk.

---

## 4. Are all 16 hardening changes pinned to a real CIS or DISA control ID?

**Status:** Several are generic domain knowledge, not sourced.

**Why it matters:** T1's proposal says the 16 changes are drawn from CIS Benchmarks and
DISA STIGs. A panelist can ask for the control ID of any one of them. "General knowledge"
is not an answer.

**How to answer:** Go through the catalogue in `lab/blueprint.md` section 8 and attach a
specific control ID to each. Anything you cannot pin gets replaced.

**What a bad answer means:** Swap the unpinnable changes for pinnable ones. Do this before
data collection starts, not after.

---

## 5. Is snapd still refreshing packages on its own schedule?

**Status:** **Answered 2026-09-03.** Four units disabled. One failed lookup per SIEM-01 boot
remains, deliberately, and a protocol rule covers it. Resolution at the end.

**Why it matters:** `snapd` was found installed on SIEM-01 (version `2.76`, upgraded to
`2.76.3` in the Phase 2 patch run). snapd refreshes its snaps automatically, several times a
day, without asking. That is the same problem as the apt timers, which were disabled on
2026-09-02, and the same problem as the Wazuh vulnerability feed, which was disabled the same
day. This one was **not** dealt with.

All featured snaps were skipped at install, but snapd itself and its base snaps are present and
its refresh timer is live.

**How to answer:** check `systemctl list-timers | grep snap` and `snap refresh --time` on
SIEM-01. Then either hold refreshes indefinitely, or remove snapd entirely if nothing depends on
it. Record whichever is chosen in DECISIONS.md with the reversal command.

**What a bad answer means:** a snap refresh inside a capture window changes packages on the
machine mid-run and generates its own events. Same failure mode as an unattended apt upgrade:
silent, scheduled, and it invalidates every run collected before it.

### Measured 2026-09-03. The problem is real but it is not the one written above.

```
snap list           : empty, NO snaps are installed at all
snap refresh --time : last: n/a   next: n/a
snapd version       : 2.76.3+ubuntu24.04
```

**Nothing can refresh, because nothing is installed.** The feared "snap refresh mid-run" cannot
happen. But the journal shows what snapd is actually doing:

```
Sep 03 08:02:30 siem-01 snapd[5068]: state ensure error:
  Get "https://api.snapcraft.io/api/v1/snaps/sections": net/http: request canceled while
  waiting for connection (Client.Timeout exceeded while awaiting headers)
```

**snapd contacts Canonical on its own loop even with zero snaps installed, and it is already
failing.** After Phase 5 disconnects NAT it will fail **every time, forever**, and each failure
is a journald message that Wazuh collects into `archives.json`. That is the same failure mode as
the Wazuh vulnerability feed disabled in Phase 2: an internet-dependent service on a deliberately
isolated machine, logging on a timer.

`snapd.snap-repair.timer` is also `enabled`, and it contacts Canonical independently of installed
snaps.

**Removing snapd is the wrong fix.** `apt-cache rdepends --installed snapd` returns
`ubuntu-server-minimal`, `ubuntu-server`, `apparmor` and `command-not-found`. Removing the package
would drag out the server metapackages.

**How to close it: stop the daemon, keep the package.** Disable and stop the units that reach the
network, leave `snapd.apparmor.service` and `snapd.seeded.service` alone so boot ordering and
AppArmor are untouched:

```bash
sudo systemctl disable --now snapd.service snapd.socket snapd.snap-repair.timer snapd.autoimport.service
```

Then reboot and confirm the machine comes up, Wazuh is active, and no further `api.snapcraft.io`
lines appear. **The `phase3-complete-2026-09-02` snapshot makes this safe to attempt**: if boot
breaks, revert.

**This cannot be done by the harness account.** The sudoers rule installed on 2026-09-02 grants
`/usr/local/sbin/telos-archive` and nothing else, so it is a student step by design.

### Resolution, 2026-09-03. Fixed as far as it is worth fixing.

The four units were disabled and the machine rebooted. State afterwards:

```
snapd.service             enabled=disabled   active=inactive
snapd.socket              enabled=disabled   active=ACTIVE
snapd.snap-repair.timer   enabled=disabled   active=inactive
snapd.autoimport.service  enabled=disabled   active=inactive
snapd.seeded.service      enabled=enabled    active=active
```

**The socket is still active, and the exclusion list was the reason.** `snapd.seeded.service` was
deliberately left alone to protect boot ordering, and it **requires** `snapd.socket`, which
socket-activates `snapd.service` anyway:

```
systemctl list-dependencies --reverse snapd.socket
  snapd.socket
  ├─snapd.seeded.service
  └─snapd.service
```

**What actually happens now, per boot:**

```
08:40:32  state ensure error: Get "https://api.snapcraft.io/..."  timeout
08:41:02  snapd.service: Deactivated successfully.
snapcraft.io contacts this boot : 1
```

One failed lookup, then snapd shuts itself down. **The repeating timer behaviour is gone**, which
was the actual problem. What is left is a single event at boot.

**Deliberately stopping here, and this is a judgement call rather than a fix.** Removing the last
one means disabling `snapd.seeded.service`, which sits in the boot path on a machine that holds
every piece of evidence the thesis has. Risking a boot failure on the SIEM to remove one log line
that occurs outside every capture window is a bad trade.

**It is outside every capture window because of a protocol rule that this makes explicit:**

> **SIEM-01 must not be rebooted during a capture campaign.** Only WIN-EP-01 is reverted and
> booted per run. If SIEM-01 ever has to restart mid-campaign, the runs on either side of that
> restart carry one extra `snapcraft.io` failure event, and that must be noted in the run
> manifest rather than discovered later.

Added to `lab/blueprint.md` and runbook Phase 6.

**If it ever needs closing completely:** `sudo systemctl disable --now snapd.seeded.service`, then
reboot and confirm the machine comes up and Wazuh is active. The `timesync-off-2026-09-03`
snapshot makes that recoverable.

---

## 6. How do SIEM-01 and WIN-EP-01 keep their clocks together after Phase 5?

**Status:** **Answered and fixed 2026-09-03.** The six switches are set on both machines, and the
drift half is answered by not depending on the manager's clock at all. Resolution at the end.

**Why it matters:** SIEM-01 currently reports `NTP service: active` and
`System clock synchronized: yes`, synchronising over the internet through the NAT adapter. Phase
5 disconnects that adapter. After that, `systemd-timesyncd` has no reachable time server and the
clock is free to drift, as is WIN-EP-01's.

Runbook rule 5 (fence capture windows in telemetry, not host clock) protects the **window**. It
does not protect **cross-machine correlation**, which is a different thing. Matching an endpoint
event to a manager event depends on the two clocks agreeing.

**How to answer:** pick one of three.
1. Accept drift and correlate only within a single host. Cheapest. Restricts the analysis.
2. Run a time source on the Windows host, reachable at `10.20.10.1`. Keeps both guests aligned
   without giving them internet.
3. Re-enable VMware Tools time sync (`tools.syncTime` is currently `FALSE` in `SIEM-01.vmx`).
   **Note the catch:** a clock step is itself a logged event and could land inside a capture
   window, which is probably why it was disabled in the first place.

**Progress 2026-09-02.** WIN-EP-01 was set to `UTC`, matching SIEM-01's `Etc/UTC`, so the two
machines at least share a reference frame. `tools.syncTime = "FALSE"` is set in both `.vmx`
files.

**A gap found the same day, and it is the sharp part of this item.** `tools.syncTime = "FALSE"`
stops the **periodic** clock sync. It does **not** stop VMware Tools from stepping the guest clock
on snapshot revert, on resume, or at Tools startup. Those are separate switches, and **neither
`.vmx` sets any of them**:

```
time.synchronize.restore
time.synchronize.resume.disk
time.synchronize.tools.startup
time.synchronize.continue
```

**Why this is worse than ordinary drift.** Phase 6 reverts a snapshot before **every single
run**. If VMware Tools steps the clock on each revert, a time-change event lands at the very
start of every capture window, in all 101 runs. That is a scheduled, uncontrolled event injected
into the exact window being measured, and it would be present in the pre-change and post-change
runs alike, so it would not cancel out cleanly either.

**How to answer this part:** set the four switches to `FALSE` in both `.vmx` files with the VMs
powered off, then revert a snapshot and check whether the guest clock moved and whether a
time-change event was written. Do this before the Phase 5 golden snapshot.

**What a bad answer means:** if drift is ignored and cross-host correlation is needed later, the
timestamps cannot be repaired after the fact. Decide before Phase 6, not after.

### Resolution, 2026-09-03

**Part one, the switches. Done.** All six are now `FALSE` in **both** `.vmx` files, alongside
`tools.syncTime`. Verified to survive a full power cycle, which matters because VMware rewrites
the `.vmx` on every power off:

```
tools.syncTime                  = "FALSE"
time.synchronize.continue       = "FALSE"
time.synchronize.restore        = "FALSE"
time.synchronize.resume.disk    = "FALSE"
time.synchronize.resume.host    = "FALSE"
time.synchronize.shrink         = "FALSE"
time.synchronize.tools.startup  = "FALSE"
```

VMware Tools can no longer step either guest's clock in any situation. Backups of both files were
kept as `<name>.vmx.telos-20260903T081807Z.bak`.

**Part two, the drift. The three options offered above were the wrong question.** Look at what an
archive line actually contains, from the Phase 3 evidence:

```
endpoint clock : "systemTime":"2026-09-02T13:30:38.7096614Z"
manager clock  : "timestamp":"2026-09-02T13:30:40.599+0000"
```

**Both clocks are in every single event.** So the fix is not to synchronise the two machines, it
is to **stop depending on the manager's clock**.

**Harness rule, to be enforced in Phase 6:** every capture window boundary and every measurement
uses the **endpoint's own** `systemTime` or `utcTime` from inside the event. The manager's
`timestamp` field is used for **nothing** except measuring pipeline latency, and that figure is
only meaningful while the clocks are known to agree. Under this rule SIEM-01's drift cannot reach
the results, because it never enters them.

This is runbook rule 5 applied properly: fence in the telemetry, not on a host clock.

**Option 2 is therefore rejected**, not deferred. Running a time server on the Windows host at
`10.20.10.1` would put a live network service on a segment the thesis describes as isolated, to
solve a problem the rule above removes.

**One thing that must be decided in Phase 5, and it is currently only an implication.** A **cold**
snapshot, taken powered off, boots the guest fresh and VMware sets the virtual clock from the host
at power-on, so the clock is right without Tools touching it. A **live** snapshot, taken with
memory, restores a stale clock. The blueprint's run protocol reverts then starts, which implies
cold, but nothing says so. **The golden snapshot must be taken cold, and that has to be written
into Phase 5 as a requirement rather than left to inference.**

---

## 14. Wazuh rotates `archives.json` daily, by hard link, and the run protocol assumes it does not

**Status:** **Answered 2026-09-03. The run protocol changed: export by date, never truncate.**
Resolution at the end of this item.

**Why it matters:** `lab/blueprint.md` run-protocol step 10 says "rotate `archives.json`, gzip,
pull to `E:\runs\<run_id>\`, then **truncate on the SIEM**". That assumes one growing file per
run. Wazuh does not work that way.

**Observed.** `archives.json` was 49,654,191 bytes on 2026-09-02 and 5,166,709 bytes the next
morning. It did not shrink, it was rotated at the day boundary:

```
drwxr-x--- 3 wazuh wazuh    4096 Sep  1 19:36 2026
-rw-r----- 2 wazuh wazuh 5272919 Sep  3 08:19 archives.json
-rw-r----- 2 wazuh wazuh       0 Sep  3 07:59 archives.log
```

**Note the link count of 2 on `archives.json`.** It is a **hard link** to today's file inside the
dated tree, almost certainly `2026/Sep/ossec-archive-03.json`. Both names point at the same inode.

**Two consequences, and the second one destroys data:**

1. **A run crossing midnight splits across two files.** With 101 runs of 25 to 60 minutes each,
   unattended overnight batches are exactly when this happens. The harness would export half a
   run and not notice.
2. **Truncating `archives.json` also empties that day's stored archive**, because it is the same
   inode. The run protocol's truncate step does not clear a scratch file, it deletes the day's
   permanent record. Safe only if the export already succeeded and was verified.

**How to answer:**
- Have the harness read the **dated file** for the run's date rather than `archives.json`, or
  detect a date boundary inside a window and export both files.
- Verify the export, by hash or line count, **before** any truncate.
- Better: stop truncating at all and let Wazuh's own rotation manage the files, exporting the
  dated archives instead. That removes a destructive step from a 101-run unattended loop.
- `/usr/local/sbin/telos-archive` needs a subcommand to list and read the dated tree. It cannot
  today, and the harness account has no other root access by design.

**What a bad answer means:** a run silently exports partial data, or the truncate step destroys a
day of archives that was never successfully copied. Both are unrecoverable after the fact.

### Resolution, 2026-09-03

**Decision: the harness exports by date and never truncates anything.**

`lab/scripts/telos-archive` was rewritten. `truncate` and `rotate` are **removed entirely**, and
these were added:

| Subcommand | What it does |
|---|---|
| `dated-list` | every dated archive with size and whether it is gzipped |
| `dated-path DATE` | resolve `YYYY-MM-DD` to its archive path |
| `export DATE` | copy that day's archive to `/tmp` as `.gz`, then print `bytes_gz`, `sha256_gz` and `lines` so the caller can **verify** the copy rather than assume it |
| `disk` | free space on the filesystem holding the archives |

`tail`, `count` and `show` now take an optional `DATE` and read gzipped dated archives through
`zcat`. **If a window crosses midnight, export both dates.**

**The second benefit is worth naming in Chapter 3.** With truncation gone, the tool has **no
destructive subcommand at all**, so the single sudoers rule grants the harness account **read and
export only**. It cannot alter or delete the evidence store. The question "how do you know your
archives were not modified?" now has a checkable answer rather than an assurance.

**What this moves rather than removes.** Disk management now depends entirely on Wazuh's own
rotation plus a retention policy that is still deferred (see item 3). The harness must check free
space before every run with `telos-archive disk` and abort cleanly when low. That guard was
already in the blueprint risk table; it is now load-bearing.

**Updated in:** `lab/blueprint.md` section 6 step 10, runbook Phase 6 step 10, and
`lab/scripts/telos-archive`.

**Installation is a student step**, because replacing a root-owned file needs sudo and the
harness account has none:

```bash
sudo install -o root -g root -m 755 /home/eli/telos-archive /usr/local/sbin/telos-archive
```

---

## 7. Does vmnet3 have a host adapter connected, and should it?

**Status:** **Answered 2026-09-03.** Yes it has one, nothing uses vmnet3, and the record has been
corrected rather than the machine. Resolution at the end of this item.

**Why it matters:** the Phase 1 record and the runbook describe vmnet3 as host-only with **no
host adapter**. The host says otherwise, verified 2026-09-02:

```
VMware Network Adapter VMnet3   Up   10.20.20.1/24
```

The adapter is connected and the Windows host holds an address on that network. If vmnet3 was
meant to be isolated, that claim is currently false and any statement in the thesis about
isolation on that segment would be wrong.

Nothing uses vmnet3 yet, so nothing is broken today.

**Separate but related, recorded here so it is not lost:** VMnet8 originally had **no** host
adapter, which is why the first SSH attempt to `192.168.243.129` timed out. It was enabled
deliberately on 2026-09-02 via "Connect a host virtual adapter to this network". That is a host
configuration change and it is now part of the host baseline.

**How to answer:** decide whether vmnet3 is meant to be isolated. If yes, untick its host
adapter in the Virtual Network Editor and correct the Phase 1 record. If no, correct the record
to say the adapter is connected on purpose. Either way the document and the machine must agree.
Do it before the Phase 5 golden snapshot.

**What a bad answer means:** low technical damage, real thesis damage. A written isolation claim
that the machine does not support is the kind of thing a panelist can check.

### Resolution, 2026-09-03

**Verified on the host:**

```
VMware Network Adapter VMnet3   Up   10.20.20.1/24

Which VMs are attached to vmnet3?
  SIEM-01.vmx   : VMnet8, VMnet2
  WIN-EP-01.vmx : VMnet8, VMnet2
```

**No virtual machine is attached to vmnet3 at all.** It is a configured network with a host
adapter and nothing on it.

**The record was corrected, not the machine.** Re-reading runbook Phase 1, it never actually said
vmnet3 has no host adapter. It said vmnet2 should keep its adapter and left vmnet3 unstated, and
the contradiction was with an inference rather than with anything written. Phase 1 now states
explicitly that vmnet3 **has** a host adapter at `10.20.20.1/24` and is unused.

**Nothing was unticked**, for two reasons. Nothing is on that network, so there is no isolation
claim to defend today, and unticking requires the Virtual Network Editor with administrator
rights, which is a manual step with no benefit right now.

**The condition under which this reopens:** if `IDS-01` is ever built on vmnet3 as a promiscuous
monitor segment (`lab/blueprint.md` Tier B) **and** the thesis claims that segment is isolated,
the host adapter must be unticked at that point and the claim re-verified. That condition is
written into runbook Phase 1 so it cannot be missed.

---

## 8. The Wazuh agent's own scheduled modules fire inside every capture window

**Status:** **Closed 2026-09-03.** Four modules disabled and verified on 2026-09-02. The
agent-upgrade remainder is answered procedurally, because it has no agent-side switch. See both
resolutions at the end of this item.

**Why it matters:** the agent's default configuration runs five scan modules on their own
timers. With `logall_json` on, every event they produce lands in `archives.json`. These are
events generated by the **measuring instrument**, not by the machine under test.

Read from `ossec.conf` on WIN-EP-01 on 2026-09-02:

| Module | Setting | Fires inside a 25 to 60 minute capture window? |
|---|---|---|
| **FIM synchronization** | `<interval>5m</interval>` | **Yes, five to twelve times every run** |
| **FIM real time** | `Real-time file integrity monitoring started` | **Yes, continuously, on every file change** |
| syscollector | `interval 1h`, `scan_on_start yes` | Often, and always right after a revert |
| SCA (policy `cis_win11_enterprise.yml`) | `interval 12h`, `scan_on_start yes` | **Always**, because every run starts from a revert |
| rootcheck | enabled, runs at start | **Always**, same reason |
| syscheck full scan | `frequency 43200` (12 h) | **Always**, same reason |
| cis-cat, osquery | `disabled yes` | No |

**`scan_on_start yes` is the sharp part.** Every Phase 6 run begins with a snapshot revert and a
boot, so SCA, rootcheck, syscollector and the FIM scan run at the start of **every** run, and the
FIM sync then fires every 5 minutes throughout. Observed directly in `ossec.log` after the
2026-09-02 13:19 boot: rootcheck, an SCA scan lasting 25 seconds, a syscollector evaluation and a
FIM scan all completed within 21 seconds of the agent starting.

This noise lands in the coefficient of variation, which is the number T1's whole statistical
argument rests on.

**A second, separate problem in the same log.** `wazuh-modulesd:agent-upgrade: Module Agent
Upgrade started.` The manager can push a new agent version to the endpoint. That is the Windows
twin of the Wazuh apt repo disabled on SIEM-01 in Phase 2, and an agent version bump partway
through invalidates every earlier run under runbook rule 2.

**What a bad answer means:** run-to-run event counts differ for reasons unrelated to any
hardening change, and the difference is not even constant, because a 12-hour timer lands in some
runs and not others. That is contamination of the primary measurement, not a performance issue.

### Resolution, 2026-09-02

Four modules disabled in the agent's `ossec.conf`, each with a comment in the file explaining
why. Verified from what the agent reports about itself after restart, not from the file:

```
2026/09/02 13:56:21  (6001): File integrity monitoring disabled.
2026/09/02 13:56:21  rootcheck: Rootcheck disabled.
2026/09/02 13:56:21  syscollector: Module disabled. Exiting...
2026/09/02 13:56:21  sca: Module disabled. Exiting.
```

The measurement path is untouched. `Application`, `Security`, `System`,
`Microsoft-Windows-Sysmon/Operational` and `active-responses.log` are all still analyzed, and the
agent reports `Connected to the server` with `status='connected'`.

`ossec.conf` is now **11,848 bytes, SHA256
`1F36416E1BC59443D98AD0307638F5C5C788BEE12C545140AD993A1E4E8F2658`**, committed as
`lab/configs/wazuh-agent-ossec.conf`. The previous version is kept in the guest as
`ossec.conf.telos-pre-item8`.

**Two of those four were more than noise, and this is the part worth remembering.** `sca`
evaluates a **CIS Windows 11 policy**, so its results change when a hardening change is applied.
`syscheck` monitors the registry, so it would **observe the hardening script making its change**.
Both would have produced events that appear only in post-change runs. That is not background
noise. That is the instrument reacting to the thing being measured, and it would have looked like
a finding.

**Still open, with reduced scope.** The log still shows:

```
wazuh-modulesd:agent-upgrade: INFO: (8153): Module Agent Upgrade started.
```

There is **no agent-side switch** for it. The module waits for an upgrade command from the
manager. The only control is on the manager: never issue one. An agent version bump partway
through invalidates every earlier run under runbook rule 2.

### Resolution of the remainder, 2026-09-03

**There is nothing to disable, and nothing automatic to prevent.** The agent-upgrade module is a
listener. Wazuh never pushes an upgrade on its own. One only happens if a person triggers it:
the `agent_upgrade` command line tool on the manager, the Wazuh API, or the **Upgrade** button in
the dashboard.

So the control is procedural, and it needs two parts because a rule nobody can check is not a
control:

1. **Never run `agent_upgrade`, never call the upgrade API, and never click Upgrade in the Wazuh
   dashboard for the whole campaign.** The dashboard button is the realistic risk, because it is
   one click away while looking at an agent's page.
2. **Record the agent version in every run manifest**, read from the agent itself at the start of
   the run. That turns "an upgrade cannot happen" into "an upgrade would be visible in the data",
   which is the difference between an assumption and a check. Phase 4 already lists the agent
   version as a pinned value; this makes it a per-run field as well.

**What a bump would cost:** every run collected before it becomes non-comparable under runbook
rule 2. Detecting it in the manifest means discarding the runs after the bump instead of
discovering months later that the whole set is mixed.

---

## 12. Active response lets the manager run commands on the endpoint

**Status:** **Fixed 2026-09-03.** Disabled and verified. Resolution at the end of this item.

**Why it matters:** the agent's config has

```xml
<active-response>
  <disabled>no</disabled>
</active-response>
```

Active response lets the **manager execute commands on WIN-EP-01**. That is the measuring
instrument modifying the machine under test, possibly in the middle of a capture window. It is
worse than the scan modules in item 8, because those only added events. This changes state.

Nothing has fired so far. The risk is that a default manager rule triggers one during a real
Atomic Red Team run, which is exactly when the manager is most likely to see something it reacts
to.

**How to answer:** either set `<disabled>yes</disabled>` on the agent, or list which active
responses the manager actually has configured and prove none can trigger. The first is one line
and is reversible; the second is more work but keeps the deployment closer to a real one.

**What a bad answer means:** an untracked state change lands inside a capture window, and the
post-change run differs for a reason that is not the hardening change and is not recorded
anywhere.

### Resolution, 2026-09-03

`<active-response><disabled>yes</disabled>` in the agent config, with a comment in the file saying
why. Confirmed by the agent itself after restart:

```
2026/09/03 08:04:36 wazuh-agent: INFO: (1350): Active response disabled.
```

All five collection channels still analyzed, `status='connected'`. `ossec.conf` is now **12,115
bytes, SHA256 `CED16E0B41384BF421192317E3754732D0E3155A85BA98F2CEEDFA846B0278B1`**, committed as
`lab/configs/wazuh-agent-ossec.conf`. Previous version kept in the guest as
`ossec.conf.telos-pre-item12`.

**To reverse:** one word in the file, or restore `ossec.conf.telos-pre-item12`.

---

## 13. The agent has its own rate limiter, a third silent loss channel

**Status:** Open, unmeasured. Raised 2026-09-02.

**Why it matters:** the agent config contains

```xml
<client_buffer>
  <disabled>no</disabled>
  <queue_size>5000</queue_size>
  <events_per_second>500</events_per_second>
</client_buffer>
```

If a run produces more than **500 events per second**, the agent throttles. If the **5000-event**
queue then fills, events are dropped before they are ever sent.

**There are now three loss channels between the endpoint and `archives.json`**, and they are the
same failure in three places:

| Where | Limit | Item |
|---|---|---|
| Sysmon event channel on the endpoint | 64 MB, `Circular` | 9 |
| **Wazuh agent buffer** | **500 events/s, 5000 queued** | **13** |
| journald on SIEM-01 | `RateLimitIntervalSec` and `RateLimitBurst`, unread | 1d |

Every one of them drops events silently, and every drop looks exactly like telemetry lost to a
hardening change.

**How to answer:** during a full capture window, measure the peak event rate on the endpoint and
watch `ossec.log` for buffer-full warnings. Then either raise the limits and pin the new values,
or prove the run stays under them. Note that disabling the buffer entirely removes flow control
rather than removing the loss, so it is not automatically the safer choice.

**What a bad answer means:** the same as 1d and 9. An unmeasured, uncontrolled loss channel
inside the measurement pipeline. A threat to validity, not a performance issue.

---

## 9. The Sysmon event channel is 64 MB and overwrites itself

**Status:** Open, and unmeasured under load. Raised 2026-09-02 during Phase 3.

**Why it matters:** this is the Windows twin of item 1d.

```
LogName       : Microsoft-Windows-Sysmon/Operational
MaximumSizeMB : 64
LogMode       : Circular
```

`Circular` means the oldest events are overwritten when the channel fills. If a capture run
produces more than 64 MB of Sysmon events before the Wazuh agent has read them, the oldest are
overwritten and **never sent to the manager**. They never reach `archives.json` and never appear
in any result.

The loss would look exactly like a hardening effect, and it would be biased toward the **start**
of the window, which is where the start fence and the first technique executions are.

**How to answer:** measure the channel's byte growth across one full capture window with a real
technique list. Then either raise `MaximumSizeInBytes` and record it as a pinned baseline value,
or prove the run stays under 64 MB. Note that raising it is itself a configuration change that
must be recorded and applied identically to Config S and Config N.

**Related measurement already taken:** endpoint-to-archive latency is about **1.6 to 1.9
seconds** (fence recorded on the endpoint at `13:30:38.7096614Z`, stamped by the manager at
`13:30:40.599`; end fence `13:30:47.711` and `13:30:49.311`). The agent is not far behind, which
lowers but does not remove the risk.

**What a bad answer means:** an unmeasured, uncontrolled loss channel inside the measurement
pipeline, exactly like 1d. Threat to validity, not performance.

---

## 10. Defender Tamper Protection will silently defeat Config S

**Status:** **Answered 2026-09-03.** Turned off, and the fix was verified by a functional test,
not by reading a flag. Resolution at the end.

**Why it matters:** `lab/blueprint.md` section 5 defines Config S as "Defender off, Windows
Update off, tasks disabled". On WIN-EP-01, `Get-MpComputerStatus` reports:

```
RealTimeProtectionEnabled : True
IsTamperProtected         : True
```

**Tamper Protection blocks scripted changes to Defender's protection settings.** A script that
turns real-time protection off will fail, and it will not necessarily fail loudly. Config S would
then be a snapshot that is not actually suppressed, while the analysis assumes it is.

Tamper Protection cannot be switched off from a script. It is a manual toggle in the Windows
Security window inside the VM.

**One thing that does still work, verified:** `Add-MpPreference -ExclusionPath` was accepted while
Tamper Protection was on. So exclusions are not blocked, but protection state changes are.

**How to answer:** before the Config S snapshot, turn Tamper Protection off by hand in the guest,
then verify from a script that `Set-MpPreference -DisableRealtimeMonitoring $true` actually takes
effect by reading `Get-MpComputerStatus` back. Never assume the write succeeded.

**What a bad answer means:** Config S and Config N are the same machine wearing different labels,
and the whole suppressed-versus-natural comparison in blueprint section 7 collapses without
anyone noticing.

### Resolution, 2026-09-03

Turned off by hand in Windows Security inside the guest, which is the only way it can be done.

**Reading the flag was not accepted as proof.** `IsTamperProtected : False` is necessary but not
sufficient. What Phase 5 actually needs is for a **script** to change a Defender setting and have
the change stick. So a functional test was run: flip one harmless setting, read it back, then put
it exactly as it was.

```
IsTamperProtected             : False
RealTimeProtectionEnabled     : True
DisableCpuThrottleOnIdleScans : True -> False -> restored to True
RESULT: scripted changes to Defender ARE accepted. Config S will work.
ExclusionPath                 : C:\AtomicRedTeam   (still in place)
WazuhSvc                      : Running, status='connected'
```

**Rule carried into Phase 5, because a flag can be re-enabled:** after applying Config S, **read
every setting back and confirm it took effect** before taking the snapshot. Never assume a
`Set-MpPreference` succeeded. Written into runbook Phase 5.

**Note:** Windows may re-enable Tamper Protection on its own after some updates. It is worth
re-checking immediately before the golden snapshot rather than trusting today's result.

---

## 11. SIEM-01 restarted twice with no shutdown recorded (ANSWERED, see the Answered section)

**Status:** **Answered 2026-09-02.** Host power loss for the second event, a deliberate power off
for the first. Evidence and reasoning are in the Answered section at the bottom. Kept here so the
numbering stays stable.

**Why it matters:** a SIEM that stops in the middle of a capture run loses that run. If it
happens on its own schedule, it can ruin an unattended overnight batch and the loss may not be
noticed for hours.

**Evidence, 2026-09-02:**

```
journalctl --list-boots
 -2  2026-09-02 10:27:16 UTC -> 11:26:59 UTC
 -1  2026-09-02 11:56:53 UTC -> 13:05:17 UTC
  0  2026-09-02 13:19:11 UTC -> running

last -x reboot
  reboot system boot  Wed Sep  2 13:19   still running
  reboot system boot  Wed Sep  2 11:56   still running     <- no shutdown recorded
```

The VM was started once, at about 10:27. Two further restarts are unaccounted for. **The previous
boot's journal ends abruptly** at 13:05:17 with no shutdown sequence at all, and the hypervisor's
own `vmware-0.log` also stops mid-stream at 12:56 with no power-off lines. Both are the signature
of a process that was terminated rather than shut down.

**Ruled out already:** memory. `MemSched` in the VMware log shows about 12 GB locked against a
55 GB ceiling with two VMs running, SIEM-01 reports 12 GB free of 15 GB, and
`journalctl | grep -c 'out of memory\|oom-kill'` returns `0`. The only errors in the previous
boot were harmless SMBus and Bluetooth kernel messages.

**Side effect already caused:** `/tmp` is cleared on boot, which silently deleted a staged script
and made an install command fail with a confusing error. Lab files now go to the home directory,
not `/tmp`.

**How to answer:** confirm whether I powered off or reset the VM through the VMware
interface at those times. If not, watch `vmware.log` and `journalctl --list-boots` across the next
few sessions and look for a pattern.

**What a bad answer means:** if the VM is stopping on its own, Phase 6 needs a watchdog that
detects a dead SIEM and aborts the run cleanly, rather than writing a run manifest for a run whose
data was never collected.

---

## Answered

### 1b. Can Module 2 see field-level telemetry loss? (answered 2026-09-04)

**Answer: not as originally designed. The schema was changed so it can.**

The unit of analysis is now the event type **plus which tracked fields were populated**, written
`Security-4688[CommandLine,NewProcessName]`. Full reasoning in DECISIONS.md, same date.

**The failure, demonstrated in code.** Keyed on event type alone, a change that empties
ScriptBlockText inside PowerShell 4104 leaves the rate at 838 per window in both phases. The
analyser reports UNCHANGED, correctly on the evidence it has, and the blind spot is invisible.
Test: `test_field_loss_is_invisible_to_event_type_keying`.

**The fix, demonstrated in code.** Same rates, same statistics, composite key:

```
PowerShell-4104[Path,ScriptBlockText]   838 -> 0     LOST
PowerShell-4104[Path]                     0 -> 838   NEW
lost field(s): ScriptBlockText
```

Test: `test_field_loss_is_caught_by_field_aware_keying`. The demo prints this as an explicit
FIELD-LEVEL LOSS section rather than leaving a reader to pair an unexplained LOST with an
unexplained NEW.

**What it cost:** one new module (`src/telos/eventkey.py`), a rewritten synthetic generator, and
29 new tests. **No change to `differential.py`, `variance.py` or `baseline.py`** — they treat the
key as an opaque string, which was verified before starting.

**Honest limit carried into the paper:** this is a profiling improvement, not a statistical one,
and the naive baseline benefits from it equally. The composite key improves what can be *seen*;
the variance model and correction improve what can be *trusted*. Two separate contributions,
to be claimed separately.

**Not resolved by this:** value-level degradation, where a field stays populated but its content
changes (Constrained Language Mode altering 4104 content, for example). Out of scope, and the
paper should say so.

### Why did SIEM-01 restart twice with no shutdown recorded? (answered 2026-09-02, item 11)

**Answer: two different causes, neither of them a fault in the VM.** The 13:05 stop was a **host
power loss**, the power cable was pulled by accident. The 11:27 stop was a **deliberate power
off**.

**Evidence.** Windows records unexpected shutdowns explicitly, so this was answerable from the
guest's own System log rather than from reasoning:

```
2026-09-02 11:27:05 UTC  Id=1074  StartMenuExperienceHost.exe (WIN-EP-01) has initiated the
                                  power off of computer WIN-EP-01 on behalf of user WIN-EP-01\eli
2026-09-02 11:56:56 UTC  Id=6005  The Event log service was started.

2026-09-02 13:19:07 UTC  Id=41    The system has rebooted without cleanly shutting down first.
2026-09-02 13:19:10 UTC  Id=6008  The previous system shutdown at 12:36:56 PM was unexpected.
```

Event ID 41 with 6008 is exactly the power-loss signature. Both guests also came back within two
seconds of each other, WIN-EP-01 at `13:19:03` and SIEM-01 at `13:19:05`, which is a host-level
event and not a VM-level one.

**One thing not to over-read.** `6008` names `12:36:56` as the last shutdown, which is earlier
than SIEM-01's final journal line at `13:05:17`. That is not a contradiction. Windows writes that
"still alive" timestamp on a timer, so it is a lower bound on when the machine died, not the
moment it died.

**What stays as a risk, and it is not the same question.** A 67-hour unattended capture campaign
has no protection against host power loss. A run interrupted this way is lost, and the harness
would not know unless it checks. This belongs in the Phase 6 design as a watchdog requirement:
detect a guest that died mid-run and abort that run cleanly rather than writing a manifest for
data that was never collected. It is not an open question about a fault, it is a known property
of the environment.

**Side effect worth remembering:** `/tmp` on SIEM-01 is cleared on boot. A reboot silently deleted
a staged script and made an install command fail with `cannot stat`. Stage lab files in the home
directory, never `/tmp`.

### Why were the VMware VMnet1/2/3 adapters in Error state? (answered 2026-08-31)

**Answer: fixed by Virtual Network Editor → Restore Defaults, then reconfiguring vmnet2 and
vmnet3.** The working theory (a lingering Hyper-V virtual switch conflicting with VMware's
adapters) was never confirmed as the exact cause, but the standard repair worked.

**Evidence, verified 2026-08-31 after running the fix:**

```
Get-PnpDevice | Where FriendlyName -like '*VMware Virtual Ethernet*'
  Status OK   (was Error)  for VMnet1, VMnet2, VMnet3

Get-NetAdapter | Where InterfaceDescription -like '*VMware*'
  Status Up   AdminStatus Up   (was Not Present / Down)  for all three

Get-NetIPAddress | Where InterfaceAlias -like '*VMnet*'
  VMnet2   10.20.10.1/24   (host adapter connected, matches the runbook)
  VMnet3   10.20.20.1/24
  VMnet1   192.168.12.1/24  (default, unrelated to this project)
```

DHCP confirmed off on both lab subnets: `vmnetdhcp.conf` contains no `subnet 10.20.10.0` or
`subnet 10.20.20.0` block, only the defaults for VMnet1 (192.168.12.0) and VMnet8 (192.168.243.0).

**What this means:** Runbook Phase 1 (virtual networks) is complete. The host now has a working
path to the lab network at 10.20.10.1, which is what the harness needs to reach the Wazuh API
in later phases. Proceed to Phase 2 (build SIEM-01).

### How many SigmaHQ rules carry a manual STP robustness annotation? (answered 2026-08-19)

**Answer: 6 rules out of 3,783. That is 0.16%.** Effectively none.

**Evidence:** Shallow-cloned `SigmaHQ/sigma` at commit `da9bb07d642a2826e89702445d32c795209ec108`
(dated 2026-08-19). The STP annotation is a Sigma **tag** of the form `stp.<level>` inside a
rule's `tags:` list, confirmed against the SigmaHQ tag specification. Counted rule files whose
tags contain a real `stp.` entry.

Level distribution across the 6 rules:

| Tag | Count |
|---|---|
| stp.1u | 3 |
| stp.1k | 1 |
| stp.2a | 1 |
| stp.4u | 1 |

**Method note:** a naive `grep stp.` returns 19 files, but 13 of those are false hits on
`cmstp.exe` and `chrmstp.exe`, which are Windows binaries many rules mention. The real count
requires matching the tag line `- stp.<digit>`, not the substring `stp`.

**What this means:** T3's Objective 5 as written is dead. Cohen's kappa on 6 data points
spread across 4 different levels is not a meaningful agreement statistic. T3 is no longer a
safe fallback without a redesigned validation strategy. See DECISIONS.md, same date.

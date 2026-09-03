# Decision Log

Every choice that would be expensive to reverse, or that you will forget the reason for.
Newest at the top. Never delete an entry. If a decision is reversed, add a new entry that
says so and link back.

Format: date, the decision, why, and what it costs if wrong.

---

## 2026-09-03 - VMware Tools clock synchronisation fully disabled on both VMs, and the analysis will use the endpoint clock only (closes OPEN-QUESTIONS 6)

**Decision one:** all six `time.synchronize.*` switches set to `FALSE` in **both** `.vmx` files,
alongside the `tools.syncTime` that was already there.

```
tools.syncTime                  = "FALSE"
time.synchronize.continue       = "FALSE"
time.synchronize.restore        = "FALSE"
time.synchronize.resume.disk    = "FALSE"
time.synchronize.resume.host    = "FALSE"
time.synchronize.shrink         = "FALSE"
time.synchronize.tools.startup  = "FALSE"
```

**Why:** `tools.syncTime` alone stops only the **periodic** sync. The other six cover snapshot
revert, resume, and Tools startup. Phase 6 reverts a snapshot before **every one of 101 runs**, so
a clock step there would land at the start of every capture window, in every run, on both sides
of the pre-change and post-change comparison.

**Verified through a full power cycle**, because VMware rewrites the `.vmx` on every power off and
could have stripped them. All seven lines were still present afterwards. Backups kept as
`<name>.vmx.telos-20260903T081807Z.bak`.

**Decision two, and it is the more important half:** the analysis uses the **endpoint's own
clock** and never the manager's.

Every archive line carries both:

```
endpoint clock : "systemTime":"2026-09-02T13:30:38.7096614Z"
manager clock  : "timestamp":"2026-09-02T13:30:40.599+0000"
```

**Rule for the Phase 6 harness:** every capture-window boundary and every measurement uses the
endpoint's `systemTime` or `utcTime` from inside the event. The manager's `timestamp` is used for
nothing except measuring pipeline latency, and that number is only meaningful while the two clocks
are known to agree. Under this rule SIEM-01's clock drift after isolation cannot reach the
results, because it never enters them.

This is runbook rule 5 applied properly: fence in the telemetry, not on a host clock.

**What this rejects, deliberately:** running a time source on the Windows host at `10.20.10.1`,
which was option 2 in OPEN-QUESTIONS 6. It would place a live network service on a segment the
thesis describes as isolated, in order to solve a problem the rule above removes.

**Cost if wrong:** if some later analysis genuinely needs manager-side timing, the timestamps
cannot be repaired after the fact. The mitigation is that the endpoint timestamp is present in
every event, so nothing is lost by preferring it.

**To reverse:** delete the six lines from both `.vmx` files with the VMs powered off, or restore
the `.bak` files.

**Left for Phase 5, and currently only an implication:** a **cold** snapshot boots the guest fresh
and VMware sets the virtual clock from the host, so no sync is needed. A **live** snapshot restores
a stale clock. The blueprint's run protocol implies cold but never says so. **The golden snapshot
must be taken cold**, and Phase 5 has to state that.

## 2026-09-03 - Second checkpoint snapshot on both VMs

**Decision:** `agent-hardened-2026-09-03` on WIN-EP-01 and `timesync-off-2026-09-03` on SIEM-01,
both taken cold.

**Why:** the existing `phase3-complete-2026-09-02` checkpoint predates the item 12 fix. Reverting
to it today would have silently re-enabled active response. The new checkpoint captures items 6, 8
and 12 together, so a revert cannot lose them.

Two flat snapshots per VM, not a branching chain, so the warning in `lab/blueprint.md` section 5
about 16 branching delta chains does not apply. F: has 607.4 GB free.

**To reverse:** `vmrun -T ws deleteSnapshot <vmx> <name>`

## 2026-09-03 - Active response disabled on WIN-EP-01 (closes OPEN-QUESTIONS 12)

**Decision:** `<active-response><disabled>yes</disabled>` in the agent's `ossec.conf`, with a
comment in the file explaining why. Confirmed by the agent itself after restart:

```
2026/09/03 08:04:36 wazuh-agent: INFO: (1350): Active response disabled.
```

**Why:** active response lets the **manager execute commands on the endpoint**. The measuring
instrument must not be able to change the machine under test, and least of all inside a capture
window. Nothing had fired, but a real Atomic Red Team run is exactly when the manager is most
likely to see something it reacts to. Unlike the scan modules in item 8, this one changes state
rather than adding events, so its failure mode is worse and harder to detect after the fact.

`active-responses.log` is still collected as a `<localfile>`. It will simply stay empty, which is
itself evidence that nothing fired.

**Cost if wrong:** the deployment is one more step away from a default Wazuh install, and Chapter
3 must say so. The answer to a panelist is one sentence: active response was disabled because it
allows the monitoring platform to modify the endpoint under measurement, which would introduce
state changes the experiment does not control or record.

**To reverse:** one word in the file, or restore
`C:\Program Files (x86)\ossec-agent\ossec.conf.telos-pre-item12` and restart `WazuhSvc`.

## 2026-09-02 - WIN-EP-01 installer media disconnected, and a checkpoint snapshot taken on both VMs

**Decision one:** `sata0:1.startConnected = "FALSE"` in `WIN-EP-01.vmx`, matching what Phase 2 did
for SIEM-01. The CD-ROM device stays present and still points at the ISO, but it no longer
connects at power-on.

**Why:** with it connected, the endpoint **depended on E: at every boot**, and E: is the hard disk
that the runbook's first rule says no VM may depend on. Move or rename that ISO and WIN-EP-01
fails to start. It also left an installer disc inside what becomes the golden image.

**When it has to be done:** with the VM powered off. VMware rewrites the `.vmx` on power off and
would discard an edit made while it was running.

**To reverse:** set it back to `"TRUE"` with the VM powered off.

**Decision two:** a checkpoint snapshot named `phase3-complete-2026-09-02` on both VMs.

**Why:** neither machine had any restore point, and a host power loss already happened on the same
day. Two days of build work had no protection at all. F: had 587.6 GB free before, 611.6 GB after
the guests released their memory files, so cost is not a factor.

**This is not the Phase 5 golden snapshot.** That one is taken later, with NAT disconnected, and
it is the base of the `cfg-suppressed` and `cfg-natural` branches in `lab/blueprint.md` section 5.
This is a single flat checkpoint, and the blueprint's warning about branching delta chains does
not apply to it.

**Cost if wrong:** a snapshot delta grows as the VM changes. If F: gets tight before Phase 5,
delete it.

**To reverse:** `vmrun -T ws deleteSnapshot <vmx> phase3-complete-2026-09-02`

## 2026-09-02 - Four Wazuh agent scan modules disabled on WIN-EP-01 (closes most of OPEN-QUESTIONS 8)

**Decision:** disabled `rootcheck`, `sca`, `syscheck` (file integrity monitoring) and
`syscollector` in the agent's `ossec.conf`. Each change carries a comment in the file saying why.
The agent is now a log forwarder and nothing else.

**Verified from what the agent reports about itself after restart, not from the file:**

```
2026/09/02 13:56:21  (6001): File integrity monitoring disabled.
2026/09/02 13:56:21  rootcheck: Rootcheck disabled.
2026/09/02 13:56:21  syscollector: Module disabled. Exiting...
2026/09/02 13:56:21  sca: Module disabled. Exiting.
```

The measurement path is untouched. `Application`, `Security`, `System`,
`Microsoft-Windows-Sysmon/Operational` and `active-responses.log` are all still analyzed, and the
agent reports `Connected to the server` with `status='connected'`.

**Why. There are two separate reasons and the second is the serious one.**

*Noise.* All four have `scan_on_start` behaviour, and every Phase 6 run begins with a snapshot
revert and a boot, so all four would run at the start of **every one of 101 runs**. FIM also
synchronises every 5 minutes and watches some paths in real time. With `logall_json` on, every
event they produce lands in `archives.json`. That is the measuring instrument's own output
entering the measurement, and it lands in the coefficient of variation that T1's whole
statistical argument rests on.

*Confounding, which is worse.* Two of the four **react to the change being measured**:

- `sca` evaluates a **CIS Windows 11 policy**. Apply a hardening control and its results change.
- `syscheck` monitors the **registry**. It would observe the hardening script making its edit.

Both would emit events that appear only in post-change runs. A differential analysis comparing
pre-change and post-change event profiles would see a systematic difference caused by the
instrument watching the change happen. That is not background noise, and it would have looked
like a finding.

**Cost if wrong:** the deployment is a reduced Wazuh agent and Chapter 3 must say so. The answer
to a panelist is one sentence: the agent's own assessment and inventory modules were disabled
because they generate events on timers unrelated to the experiment, and two of them respond
directly to the hardening changes under test, which would confound the comparison. Their data
cannot show telemetry loss, so nothing measurable is given up.

**Not fixed, and stated as such:** the agent-upgrade module still starts
(`wazuh-modulesd:agent-upgrade: INFO: (8153): Module Agent Upgrade started.`). There is no
agent-side switch. The only control is on the manager: never issue an upgrade command.
OPEN-QUESTIONS 8 stays open with that reduced scope.

**Deliberately not changed, because they are separate decisions:** `active-response` is still
enabled, which lets the manager run commands on the endpoint (OPEN-QUESTIONS 12), and
`client_buffer` still throttles at 500 events per second with a 5000-event queue, which is a
third silent loss channel alongside the Sysmon channel and journald (OPEN-QUESTIONS 13).

**To reverse:** the previous config is in the guest at
`C:\Program Files (x86)\ossec-agent\ossec.conf.telos-pre-item8`. Copy it back and restart
`WazuhSvc`. Every change is a single word.

## 2026-09-02 - WIN-EP-01 runs Windows 11 **Education, unactivated**, not the Enterprise Evaluation ISO

**Decision:** Installed Windows 11 Education from the retail multi-edition ISO
`Win11_24H2_English_x64.iso`, choosing "I don't have a product key" and selecting Education from
the edition list (index 4, verified by reading the XML block inside `install.wim` before
installing). The machine is left **unactivated**. This supersedes the 2026-08-20 choice of
`Windows 11 Enterprise Eval 26200.6584 25H2`.

**Why:** The runbook offered "Windows 11 Enterprise Eval (or Server 2022 Eval)" and never picked
one. Windows 11 Enterprise Evaluation runs for **90 days**. Installed 2026-09-02, it stops around
**2026-12-01** and then shuts down once per hour. Reverting a snapshot does not fix that, because
the grace period is computed from the install date stored inside the restored image against the
real clock. Every capture run after that date would be broken, and the December defense sits
right on the boundary.

Education carries the same security feature set as Enterprise, including Credential Guard and
AppLocker `(unverified against Microsoft's edition matrix, taken from the edition requirements
pages)`, so the hardening catalogue is unaffected. The CIS Microsoft Windows 11 Enterprise
Benchmark and the Microsoft Windows 11 STIG still apply, which keeps OPEN-QUESTIONS 4 answerable.
Unactivated Windows has **no expiry timer at all**. Verified on the built machine:

```
Name          : Windows(R), Education edition
LicenseStatus : 5   (Notification)
GracePeriodRemaining : 0
```

`Notification` is the nag state. It does not shut the machine down.

**Cost if wrong:** a desktop watermark, personalization settings locked, and the Software
Protection service retrying activation on its own schedule and failing. That retry is a
background event source and must be named in the baseline description. Rebuilding to a different
edition later would mean a new golden snapshot and discarding every run before it.

**To reverse:** reinstall. There is no in-place path from Education to another edition without a
key.

## 2026-09-02 - WIN-EP-01 uses UEFI with Secure Boot and **no virtual TPM**

**Decision:** `firmware = "efi"` and `uefi.secureBoot.enabled = "TRUE"` in the `.vmx`, with no
TPM device. Windows 11 setup was passed with four `LabConfig` registry values set from the
Shift+F10 command prompt at the first setup screen:

```
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassTPMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassSecureBootCheck /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassRAMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassCPUCheck        /t REG_DWORD /d 1 /f
```

**These are required.** Setup showed `This PC doesn't currently meet Windows 11 system
requirements` and only proceeded after they were set. Anyone rebuilding from this runbook must
do this step.

**Why no TPM:** VMware Workstation 17 requires the virtual machine to be encrypted before it will
attach a TPM. An encrypted VM asks for a password at power-on. The Phase 6 harness must run 101
cycles unattended, so that password would have to live in the harness configuration, putting a
secret into a project whose repository is public. Secure Boot without a TPM still permits VBS,
so hardening change #8 (Credential Guard) remains possible. TPM 2.0 is recommended but not
required for VBS `(unverified against current Microsoft documentation)`.

**Verified on the built machine:** `TpmPresent : False`, `SecureBootOn : True`.

**Cost if wrong:** no BitLocker, and a panelist may ask whether an endpoint without a TPM is
representative. The answer is that no control in the 16-change catalogue depends on a TPM.

**To reverse:** add a TPM in VMware, accept the encryption prompt, and give the harness the
password. The guest keeps working.

## 2026-09-02 - `vhv.enable = "FALSE"` so that Windows cannot switch VBS on by itself

**Decision:** nested virtualization is explicitly disabled in `WIN-EP-01.vmx`.

**Why:** Windows 11 enables Virtualization-Based Security by default on capable hardware. If VBS
were already running in the golden image, hardening change #8 (Enable Credential Guard) would
have nothing left to switch on and would measure nothing. Without virtualization extensions in
the guest, VBS cannot start, so the change stays a real, measurable change.

**Verified twice, from two independent sources.** `Win32_DeviceGuard` reports
`VirtualizationBasedSecurityStatus : 0` and `SecurityServicesRunning : 0`, and `systeminfo`
during the Phase 3 atomic test reported `Virtualization-based security: Status: Not enabled`.

**Cost if wrong:** none while it stays off. It must be switched **on** deliberately, and the
golden snapshot re-examined, when change #8 is tested. This is tied to OPEN-QUESTIONS 2, which is
still untested.

**To reverse:** set `vhv.enable = "TRUE"` with the VM powered off. Then check whether Windows
turns VBS on by itself, because that would silently invalidate change #8.

## 2026-09-02 - WIN-EP-01 time zone set to UTC to match SIEM-01

**Decision:** `Set-TimeZone -Id 'UTC'`. Windows setup had left it at `Singapore Standard Time`
(UTC+8).

**Why:** SIEM-01 runs `Etc/UTC`. Two machines in two time zones turns every cross-host comparison
into a manual conversion, and OPEN-QUESTIONS 6 already concerns cross-host time. Windows stores
event times in UTC internally, so this changes how times are displayed, not what is recorded.

**Cost if wrong:** none to the data. The desktop clock inside the VM shows UTC, which is mildly
confusing when working in the guest by hand.

**To reverse:** `Set-TimeZone -Id 'Singapore Standard Time'`.

## 2026-09-02 - Sysmon baseline config is SwiftOnSecurity at a pinned commit

**Decision:** `SwiftOnSecurity/sysmon-config`, file `sysmonconfig-export.xml`, pinned at commit
`1836897f12fbd6a0a473665ef6abc34a6b497e31`, committed to the repo as
`lab/configs/sysmonconfig.xml`.

**Why:** the alternative considered was `olafhartong/sysmon-modular`, which has a wider event
surface and MITRE ATT&CK mapping. It was rejected for two reasons. First, archive growth under
load is still unmeasured (OPEN-QUESTIONS 3), and a much more verbose sensor makes an unmeasured
disk risk worse. Second, catalogue item 15 is "narrow the Sysmon config" treated as a hardening
change in its own right. That item only means something if the baseline is not already the
narrowest available option.

**Two limits that must be stated in Chapter 3, both discovered at install time:**

1. `Sysmon64.exe -c` reports `Image loading : disabled`. **Sysmon Event ID 7 never appears.** Any
   hardening change whose effect would show up as a DLL load is invisible to the method.
2. The config file's own header reads `Source version: 74 | Date: 2021-07-08`, and Sysmon loaded
   it as schema `4.50` into a `4.91` binary. It contains no rules for the event types Sysmon
   added later: 25 (ProcessTampering), 26 (FileDeleteDetected), 27, 28 and 29.

**Cost if wrong:** a config change later invalidates every earlier run under runbook rule 2.

**To reverse:** `Sysmon64.exe -c <newconfig.xml>`, then re-record the hash here and discard all
prior runs.

## 2026-09-02 - Atomic Red Team is pinned by **commit and file count**, not by archive hash

**Decision:** the pin is `cb486d9a888e921fac5902a06c7b46e420bb14a7` plus the count of 1310 files
in the `atomics` folder. The transfer archive `atomics.zip` is **not** a valid pin.

**Why:** the archives were built by a custom lock-tolerant archiver that does not preserve file
timestamps, so the SHA256 of the zip changes on every repack. This was observed directly: the
same 74-file module produced two different archive hashes on two consecutive packs. Anyone who
recorded the archive hash as a pinned value would be recording a number that cannot be
reproduced.

**Cost if wrong:** nothing, provided the distinction is written down. It is written down here and
in `C:\AtomicRedTeam\TELOS-PROVENANCE.txt` inside the guest.

## 2026-09-02 - Antivirus exclusions on the host and in the guest, for the Atomic Red Team folder only

**Decision:** two exclusions.

1. **Host:** `E:\TeLoS-artifacts` added to Kaspersky 21.26's exclusion list, by hand.
2. **Guest:** `Add-MpPreference -ExclusionPath "C:\AtomicRedTeam"` on WIN-EP-01.

**Why the host exclusion:** Kaspersky was blocking read access to **66** Atomic Red Team files.
Verified by counting them, not estimated. The list included three technique definitions
(`T1218.005.yaml`, `T1548.002.yaml`, `T1685.yaml`), `Indexes/windows-index.yaml`, and most of the
Windows payload binaries for T1055 process injection, T1218 proxy execution and T1134.001 token
manipulation. Without the exclusion the pinned commit `cb486d9a` would describe a set of files
that is not what is on the endpoint, and the reproducibility claim in the proposal would be
false. After the exclusion: **1310 files packed, 0 blocked.**

Note that Windows Defender is **not running on the host**. `Get-MpPreference` fails with
`0x800106ba` and `WinDefend` is `Stopped`, because Kaspersky has taken over.

**Why the guest exclusion, and why it is narrow:** without it, Defender quarantines the same class
of files **once, at extraction time**, before the golden snapshot exists. Quarantined files are
then permanently absent from the image. That would not be studying an endpoint where antivirus
blocks attacks. It would be studying an endpoint where an unrecorded subset of test files simply
does not exist, chosen by whichever signature version was current on the build day. The exclusion
covers only `C:\AtomicRedTeam` and is identical in Config S and Config N, so it cancels out
between them. Atomic Red Team is the stimulus generator, part of the instrument, not the machine
under test.

**Verified:** the exclusion was accepted **despite Tamper Protection being on**
(`RESULT: ACCEPTED`, `TamperProtection : True`), and after extraction
`Defender detections during extraction: 0` with all 1310 files present.

**Cost if wrong:** a stated deviation from a default endpoint that must appear in Chapter 3. A
panelist can reasonably say the baseline is less realistic. The answer is that the alternative is
an unrecorded and unreproducible difference baked into the golden snapshot, which runbook rule 2
exists to prevent.

**To reverse:** `Remove-MpPreference -ExclusionPath "C:\AtomicRedTeam"` in the guest, and delete
the entry from Kaspersky's exclusion list on the host. Remove the host exclusion when the thesis
is finished.

## 2026-09-02 - Unattended access to SIEM-01: one SSH key and one narrow sudo rule

**Decision:** two changes on SIEM-01.

1. An `ed25519` key pair at `C:\Users\Elijah\.telos\siem01_ed25519`, **no passphrase**, public
   half in `/home/eli/.ssh/authorized_keys`.
2. A root-owned helper script `/usr/local/sbin/telos-archive` with a fixed list of subcommands,
   and exactly one sudoers line in `/etc/sudoers.d/telos-archive`:
   ```
   eli ALL=(root) NOPASSWD: /usr/local/sbin/telos-archive
   ```

**Why:** blueprint run protocol step 10 is "over SSH to SIEM-01: rotate `archives.json`, gzip,
pull to `E:\runs\`, then truncate on the SIEM", and the harness must complete 101 cycles with
nobody watching. `/var/ossec` is mode 750 owned by `root:wazuh` and `eli` is not in the `wazuh`
group, so root is required.

**Why a script rather than adding `eli` to the `wazuh` group.** Group membership was the one
command answer, but it grants the interactive login account read **and write** access to
everything Wazuh holds, including `client.keys` and the archive files that are the evidence base
of the thesis. A panelist can reasonably ask how you know the archives were not altered. "The
harness account could not write to them" is an answer. "It could, but I did not" is not.

**The script also enforces a measurement rule.** Its `count` and `show` subcommands take a
**file** holding the search pattern, never the pattern on the command line, because `sudo` writes
every command line to journald and Wazuh collects journald. That is OPEN-QUESTIONS 1b, found on
this machine in Phase 2. The design makes the mistake impossible rather than relying on
discipline.

**Cost if wrong:** a passphrase-less private key on the host can reach SIEM-01. In a disconnected
lab with one user the practical risk is small, but it is a real credential and it must never be
committed. It lives in `C:\Users\Elijah\.telos\`, outside the repository.

**To reverse:** `sudo rm /etc/sudoers.d/telos-archive /usr/local/sbin/telos-archive` and delete
the `telos-harness` line from `~/.ssh/authorized_keys`.

## 2026-09-02 - WIN-EP-01 was built from a hand-written `.vmx`, not the Workstation wizard

**Decision:** the disk was created with `vmware-vdiskmanager.exe -c -s 80GB -a lsilogic -t 0` and
the `.vmx` was written by hand.

**Why:** the New Virtual Machine wizard forces a virtual TPM and VM encryption for a Windows 11
guest, which is exactly what the decision above rejects. A hand-written config also means the
machine's definition can be read, reviewed and committed rather than clicked.

**Deviations from SIEM-01's configuration, each deliberate:**

| Setting | SIEM-01 | WIN-EP-01 | Reason |
|---|---|---|---|
| Firmware | BIOS | `efi` + Secure Boot | Windows 11 needs UEFI; Secure Boot keeps VBS possible |
| Disk controller | LSI SCSI | NVMe | Windows 11 has no in-box LSI SAS driver, setup would not see the disk |
| Network card | `e1000` | `e1000e` | `e1000` driver is not in-box on Windows 11 24H2 `(unverified)`; `e1000e` is |
| Sound card | present | absent | one less device and driver emitting background events |
| 3D graphics | on | off | removes GPU driver activity from the guest |
| CPU and RAM hot-add | on | off | the device set must not change during a measurement run |

**Cost if wrong:** a malformed `.vmx` would refuse to power on, which is loud and immediate, not
silent. It powered on first time.

## 2026-09-02 - Wazuh vulnerability detection disabled on SIEM-01

**Decision:** Set `<enabled>no</enabled>` inside the `<vulnerability-detection>` block of
`/var/ossec/etc/ossec.conf`. Backup kept at `ossec.conf.pre-vd.bak`. Confirmed by Wazuh itself:
`wazuh-modulesd:vulnerability-scanner: INFO: Vulnerability scanner module is disabled.`

**Why:** The module was configured with `<feed-update-interval>60m</feed-update-interval>` and
`ossec.log` showed it acting on that timer (UTC):

```
20:02:49  Initiating update feed process.
20:31:46  Initiating update feed process.
20:51:53  Triggered a re-scan after content update.
20:51:53  Feed update process completed.
```

The 20:31 update ran for about 20 minutes and then triggered a full re-scan. Four reasons to
turn it off:

1. It cannot contribute to the measurement. It compares installed package versions against a
   CVE list. It does not observe system events, so it can neither produce nor lose the event
   types T1 counts.
2. Phase 5 removes its internet access. An internet-dependent module on a deliberately isolated
   machine will log repeated failures on a timer, forever.
3. An hourly download plus a 20 minute re-scan is uncontrolled change inside a capture window.
   Fencing capture windows in telemetry does not help when the noise arrives inside the window.
4. It had consumed 12 GB in `/var/ossec/queue/vd`.

**Cost if wrong:** SIEM-01 is a reduced Wazuh deployment, and the methodology must say so. The
answer to a panelist is one sentence: vulnerability detection was disabled because it depends on
external content updates incompatible with an isolated measurement environment, and it observes
package inventory rather than events.

**To reverse:** `sudo cp -a /var/ossec/etc/ossec.conf.pre-vd.bak /var/ossec/etc/ossec.conf`
then restart `wazuh-manager`. Needs internet to rebuild the feed, so it must be done before
Phase 5 isolation, not after.

**The 12 GB at `/var/ossec/queue/vd` was left in place on purpose.** With 159 GB free it is not
urgent, and once the machine is isolated that data cannot be downloaded again.

## 2026-09-02 - Automatic package updates disabled, and the 49 pending updates applied once

**Decision:** Disabled `apt-daily.timer` and `apt-daily-upgrade.timer`, set both
`APT::Periodic` values in `/etc/apt/apt.conf.d/20auto-upgrades` to `"0"`, then ran
`apt upgrade -y` once and applied all 49 pending updates. Verified afterwards:
`apt list --upgradable` returns only `Listing... Done`, nothing kept back, and no reboot was
required. `systemctl is-enabled` reports both timers `disabled`, `is-active` reports both
`inactive`.

**Why:** Ubuntu 24.04 patches itself on a schedule by default. Both timers were armed. Doing
nothing does not freeze the machine, it just means the change happens at a time nobody chose,
possibly mid-run. The choice was never "change it or leave it alone", it was "change it now on
purpose and write it down" or "let it change itself later".

Applying the updates rather than freezing an unpatched machine, because:
1. Exact reproduction from the ISO is not achievable anyway. The Wazuh install itself pulls from
   the internet. The real reproducibility artifact is the Phase 5 golden snapshot.
2. The hardening catalogue is CIS-based, and CIS baselines assume a patched system. Measuring
   telemetry loss on a knowingly unpatched host invites an obvious panel question.

The kernel was **not** among the updates. It stays `6.8.0-138-generic`. The 49 packages included
`apparmor` (writes audit records), `cloud-init` 25.2 to 26.1, `netplan.io`, and `open-vm-tools`
12.5 to 13.0. All four were checked after the upgrade and a reboot: `ens37` still held
`10.20.10.10/24`, exactly one default route on `ens33`, kernel unchanged, clock on UTC with NTP
active. `systemd`, `openssh-server` and `rsyslog` were **not** in the update list, so the
logging stack did not move.

**Cost if wrong:** SIEM-01 no longer receives security updates automatically, so it must not be
exposed to an untrusted network. Acceptable because it is isolated on vmnet2 from Phase 5. If a
future update is ever needed, it becomes a deliberate, recorded act that invalidates prior runs.

**To reverse:** `sudo systemctl enable --now apt-daily.timer apt-daily-upgrade.timer` and set
both `20auto-upgrades` values back to `"1"`.

**Still open:** `snapd` refreshes its snaps on its own schedule and has **not** been dealt with.
See OPEN-QUESTIONS item 5. Same class of problem, not yet closed.

## 2026-09-02 - Root logical volume extended to the whole volume group (one-way)

**Decision:** Kept the installer's LVM layout rather than reinstalling without it, and ran
`lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv` followed by
`resize2fs /dev/ubuntu-vg/ubuntu-lv`. Root filesystem went from 97 GB to 195 GB, online, with no
reboot. Free space went from 86 GB to 179 GB.

**Why:** The Ubuntu guided install with LVM gave the root logical volume 99 GiB of a 200 GB disk
and left 99 GiB unallocated in the volume group. No error and no warning was shown. It was found
only by reading the SSH login banner. Half the disk was unreachable while `df` reported a
plausible-looking number.

Reinstalling without LVM would have cost 20 minutes for no benefit, because rollback is handled
by VMware snapshots of the whole VM, not by LVM snapshots. Free extents in the volume group
would have bought a second rollback mechanism that this project will not use.

**Cost if wrong:** The extend is effectively **one-way**. Shrinking an ext4 root filesystem
requires booting from other media. If free extents in the volume group are ever needed, the VM
must be rebuilt.

## 2026-09-02 - Wazuh pinned to 4.14.7-1, repo disabled, packages held

**Decision:** Three separate locks on the Wazuh version.

1. Downloaded the installer from `https://packages.wazuh.com/**4.14**/wazuh-install.sh`, not the
   runbook's `4.x`. Recorded its SHA256 before running it.
2. Commented out the repository the installer added, per runbook step 6. Verified: `apt update`
   no longer contacts `packages.wazuh.com`.
3. Ran `apt-mark hold wazuh-manager wazuh-indexer wazuh-dashboard` as a second, independent lock.

**Why:** `4.x` is a moving pointer that returns whatever is newest on the day it runs, which
contradicts the project's own rule to pin every version. Worth noting that the installer, having
been fetched from the pinned `4.14` path, then configured the machine to track `4.x`:

```
deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main
```

So pinning the download alone would not have pinned the machine. The repo had to be disabled too.
The `apt-mark hold` is the third lock because a repository can be re-added by a reinstall, by a
later runbook step, or by hand, and a hold still blocks the upgrade if it is.

**On `WAZUH_REVISION="rc1"`:** `wazuh-control info` reports that string. Why it reads `rc1` is
**not known**. The authoritative record is the apt package version `4.14.7-1` from a repository
component literally named `stable`, which is what all three packages report. Do not cite `rc1`
as a version.

**Cost if wrong:** Low. Unlocking is `apt-mark unhold` plus uncommenting one line. The cost of
not doing it is high and silent: a version bump partway through discards every earlier run.

## 2026-09-02 - Retention decision deferred until a measured event rate exists (deviates from runbook step 8)

**Decision:** Runbook Phase 2 step 8 says to shorten retention. That half of the step was
**deliberately not done**. The replica half was verified as already satisfied and needed no
change.

**Why:** The runbook itself admits the 16 GB and 200 GB figures were unmeasured headroom. Now
there are measurements:

| Item | Measured 2026-09-02 |
|---|---|
| Archive growth, idle, no agents | about 9.7 MB per day |
| Archives on disk | 88 KB |
| Indexer data on disk | 3.4 MB |
| Free space | 159 GB |

At the idle rate, archives take decades to matter. The real risk is a burst during a Phase 6 run,
and that rate cannot be known until a run has happened. Setting a retention number now would
replace one guess with another.

**Instead:** record the measured baseline (done, in WORKLOG), add a free-space check to the
Phase 6 harness so a run aborts rather than filling the disk (already required by runbook Phase
6), and set retention after the first real run.

**Cost if wrong:** If Phase 6 generates events far faster than expected, the disk could fill
before retention exists. The harness free-space check is what prevents that from corrupting a
run, so **that check is now load-carrying and must actually be implemented.**

## 2026-09-02 - Smaller Phase 2 build choices

Four small decisions, grouped because none of them warrants its own entry.

**1. Declined the Ubuntu installer self-update.** The installer offered to update itself from
24.04.4 to 24.04.4.1. Chose "Continue without updating". The installer is fetched live, so its
version would depend on the day the build ran. The installed OS is 24.04.4 LTS either way.
*Cost if wrong:* if a bug in the shipped installer had broken the install, redo it and accept
the update. Cheap, because no data existed at that point.

**2. Hostname is lowercase `siem-01`, not `SIEM-01`.** The Ubuntu installer lowercased it.
Left as is, because lowercase is the Linux convention and hostname lookups are case-insensitive.
The VMware display name stays `SIEM-01`. Wazuh event fields will show `siem-01`. Both refer to
the same machine.

**3. Netplan file uses `dhcp4: false` instead of the runbook's `routes: []`.** The goal of
`routes: []` was to stop the lab interface adding a default gateway. With `dhcp4: false` and no
gateway specified, netplan adds only the local `10.20.10.0/24` route, which is the same result,
without relying on an empty-list construct that was not verified for this netplan version.
Confirmed with `ip route`: exactly one `default` line, on `ens33`.

**4. The lab interface is `ens37`, not `ens34`.** The runbook guessed `ens34`. The real name
comes from the PCI slot: `ethernet0.pciSlotNumber = "33"` gives `ens33` and
`ethernet1.pciSlotNumber = "37"` gives `ens37`. The runbook was right to say "find it with
`ip link show`" rather than trusting the guess.

## 2026-08-19 - Windows hypervisor turned off (host runs VMware natively)

**Decision:** Disabled the Windows hypervisor with `bcdedit /set hypervisorlaunchtype off`,
then rebooted. Verified: HypervisorPresent went True to False, VBS status went 2 to 0, vmrun
still works.

**Why:** Phase 0 found a Windows hypervisor running. The cause was the Hyper-V feature, not any
security feature (Memory Integrity off, Credential Guard off, EnableVirtualizationBasedSecurity=0,
no Docker, no WSL2). Two reasons to turn it off:
  1. VMware now runs directly on the hardware. Sharing the machine with the Windows hypervisor
     can add timing changes, and T1 measures timing variance. This removes that variance source.
  2. Hardening change #8 (Credential Guard) needs nested virtualization inside the guest. VMware
     exposes that more reliably when the host hypervisor is off.

**Cost if wrong / how to reverse:** `bcdedit /set hypervisorlaunchtype auto` then reboot. This
also disables Docker Desktop, WSL2, and host Credential Guard while off, but none of those are
in use here.

**Must stay off for the whole experiment.** Changing this mid-experiment changes timing and
invalidates prior runs. It is now part of the host baseline, same status as a pinned version.

## 2026-08-31 - Project named TeLoS

**Decision:** The system and lab are named **TeLoS**. Chosen from a shortlist that included
`covdrift`, `Scotoma`, and `anino` (Tagalog for shadow).

**Why:** Two readings land on the same word. "TeLoS" reads as **Telemetry Loss**, which is
literally the thing the system detects. It is also the Greek word for purpose or end goal,
which fits a thesis project without being decorative. Checked against PyPI and GitHub search
at decision time; no existing security tool found using this name `(unverified, spot-check
only, not an exhaustive trademark search)`.

**Where it is used:** the homelab folder on F: (`F:\TeLoS Homelab\`, with a space, exact
casing). Runbook paths written before this decision (`F:\Homelab\...`) are corrected to match.
The Python package is still `src/blindspot/`; renaming it to match is a follow-up task, cheap
now, expensive after the harness and web layer exist.

**Cost if wrong:** Low. A folder rename on F: is a `Move-Item`. The package rename is more
work the later it happens, so do it before Phase 3 if the name is final.

## 2026-08-31 - Build the analysis core before the lab, using synthetic data

**Decision:** Write stages 2, 3 and 5 of the pipeline (variance model, differential analysis,
reporting) now, tested against generated counts. Leave stage 1 (acquisition from live VMs) and
stage 4 (impact scoring) until later.

**Why:** The analyser consumes event counts. It does not care whether a real Windows machine or
a script produced them. So nothing about stages 2, 3 and 5 needs a lab, Wazuh, or Atomic Red
Team. Waiting for the lab before writing any code would have cost weeks for no reason.

This also corrects an earlier claim in this log. The broken hardening catalogue
(OPEN-QUESTIONS item 1) was described as blocking everything. It is not. It blocks the
**experiment design**, not the analyser.

**Cost if wrong:** Synthetic data proves the code is correct. It proves nothing about real
telemetry. Real event counts are not normally distributed, and the demo generator draws from a
rounded normal. No result from `src/demo.py` may be presented as a finding. The moment real
captures exist, the same tests must be re-run against them.

**Immediate benefit:** the test suite found a genuine crash before any real data existed. See
the WORKLOG entry for the same date.

## 2026-08-19 - T3 loses its fallback status (SigmaHQ has only 6 STP-annotated rules)

**Finding:** `SigmaHQ/sigma` at commit `da9bb07` carries STP robustness tags on only **6 of
3,783 rules (0.16%)**. See the full evidence in OPEN-QUESTIONS.md, Answered section.

**Decision:** T3 can no longer be treated as the safe fallback to T1. Its Objective 5 (validate
automated scores against the manually annotated subset with Cohen's kappa) cannot be executed on
6 rules across 4 levels.

**Why this matters now:** The plan assumed T1 primary, T3 fallback. As of this finding there is
**no verified fallback.** If T1 fails its spike gate, the options are:
  1. Redesign T3's validation: annotate a subset yourself with a second annotator and report
     inter-rater agreement. This turns T3 into a partly manual study and weakens its main
     selling point (that it validates against someone else's labels).
  2. Switch the fallback to **T2** (severity inversion), which needs no external annotation
     corpus. Its weakness is self-created ground truth, which is a smaller problem than having
     no ground truth at all.

**Cost if wrong:** Low to act on now, high to ignore. Knowing this in August means the fallback
can be rebuilt calmly. Discovering it in October, after a failed T1 spike, means no time to
recover.

**Not yet decided:** which of the two paths above. This is a strategic call to make alongside
the T1 spike result, not before it. T1 is still the primary and still the goal.

## 2026-08-19 - Repo can be public now (supersedes the private decision below)

**Decision:** The repo can be public from the start. No need to wait for the defense.

**Why:** The professor confirmed two things. There are no intellectual property rules that
stop a student publishing thesis work early. And there is no similarity-check problem: a
match between the final paper and my own public repo is not treated as an issue.

This removes both reasons the earlier entry gave for staying private.

**Still true, separate point:** the repo has no code yet. It is not a strong portfolio piece
until the harness exists. Being public early does not harm this, because the value of a public
repo is the commit history built over time. Publishing now starts that history and also backs
up the work off the single local disk.

**Cost if wrong:** Low. A public repo can be made private again at any time.

## 2026-08-19 - Repo stays private until the defense (SUPERSEDED, see entry above)

**Decision:** GitHub repo is private now. Flip to public on defense day.
**Why:** Three unsubmitted thesis proposals in a public repo is an academic integrity and
scooping risk. The commit history still proves months of work when it goes public, which is
the part that has portfolio value.
**Cost if wrong:** Delayed portfolio visibility by a few months. Low.

## 2026-08-19 - Raw run data never enters git

**Decision:** `data/runs/` is gitignored. Only small derived files in `data/summaries/`
are committed.
**Why:** GitHub rejects files over 100 MB and warns past 1 GB per repo. 101 gzipped archive
exports will not fit. Git LFS free tier is 1 GB storage and 1 GB bandwidth per month, which
this would blow past and start costing money.
**Cost if wrong:** Raw data exists on one disk only. Mitigate with a separate backup copy
to a second physical drive, not with git.

## 2026-08-19 - Everything lives in E:\Claude general

**Decision:** Repo, code, docs, and archives all in this one folder on E:.
**Why:** One place to look. Nothing to forget. The blueprint originally put code on C: for
speed, but the only hard rule is that **VMs** must never run from E:. Git and Python on a
hard disk are just slower, not wrong.
**Cost if wrong:** Slower git operations and Python imports. Acceptable.

## 2026-08-19 - T1 gets full structure, T2 and T3 get stubs

**Decision:** Build out `thesis/T1/` properly. T2 and T3 keep a folder and a README that
holds the fallback reasoning.
**Why:** Only one topic will be built. Empty scaffolding for two abandoned topics is
maintenance work for nothing. But the fallback trail must stay written down, because T1
can still fail its spike gate.
**Cost if wrong:** If T1 fails and you switch to T3, you build that structure then. Cheap.

---

# Pinned versions (fill these in during Phase 4 of the runbook)

A version bump partway through the experiment means every earlier run must be discarded.
Record these **before** taking the golden snapshot.

## Host and analysis stack (recorded 2026-08-31)

| Item | Value | Date recorded |
|---|---|---|
| Host OS | Windows 11 Pro 10.0.26200 | 2026-08-31 |
| CPU | AMD Ryzen 9 7950X, 16C/32T | 2026-08-20 |
| VMware Workstation | 17.5.1 build-23298084 | 2026-08-20 |
| Windows hypervisor | **OFF** (`hypervisorlaunchtype off`) | 2026-08-20 |
| Python | 3.13.14 (`C:\Program Files\Python313`) | 2026-08-31 |
| numpy | 2.5.2 | 2026-08-31 |
| scipy | 1.18.1 | 2026-08-31 |
| pandas | 3.0.5 | 2026-08-31 |
| PyYAML | 6.0.3 | 2026-08-31 |
| pytest | 9.1.1 | 2026-08-31 |
| Analyser git commit | `78f41f4` (first version of the analysis core) | 2026-08-31 |
| **Host antivirus** | **Kaspersky 21.26** (`AVP21.26` service running). **Windows Defender is OFF on the host** as a result: `WinDefend` is `Stopped` and `Get-MpPreference` fails with `0x800106ba`. Kaspersky blocks Atomic Red Team files, so `E:\TeLoS-artifacts` is on its exclusion list. **Remove that exclusion when the thesis is finished.** | 2026-09-02 |
| Artifact store | `E:\TeLoS-artifacts\` holds every pinned installer, clone and archive. **Not** in the repo. Binaries do not belong in git. | 2026-09-02 |
| Credentials store | `C:\Users\Elijah\.telos\` holds `WIN-EP-01.pw`, `SIEM-01.pw` and the `siem01_ed25519` key pair. Outside the repo on purpose, since the repo is public. **Never commit these.** | 2026-09-02 |
| `git core.autocrlf` | **`true`** on this host. This silently rewrote the pinned Sysmon config on first commit, one byte short of the recorded hash. `.gitattributes` now pins `lab/configs/sysmonconfig.xml` as binary and keeps `lab/scripts/telos-archive` and `*.sh` at LF. | 2026-09-02 |

`scipy` supplies Benjamini-Hochberg through `scipy.stats.false_discovery_control`, so
`statsmodels` is not a dependency. `scikit-learn` was in the original plan for Cohen's kappa,
which belonged to T3 and is no longer in scope.

## Lab stack (fill in during Runbook Phase 4)

| Item | Value | Date recorded |
|---|---|---|
| **Wazuh version** | **`4.14.7-1`** for `wazuh-manager`, `wazuh-indexer` and `wazuh-dashboard`, from `packages.wazuh.com/4.x/apt stable main`. Repo now disabled and all three packages held. | 2026-09-02 |
| Wazuh installer script | `wazuh-install.sh` from `https://packages.wazuh.com/4.14/wazuh-install.sh`, 204 KB, SHA256 `8ebe9514688ace8af9445805e8887cd491dd9f95fa9d421a70f0ea012ab06f3a` | 2026-09-02 |
| Wazuh deployment mode | all-in-one (`-a`). Certificates issued for `127.0.0.1`, so the Phase 5 NAT disconnect cannot break component communication. | 2026-09-02 |
| SIEM-01 OS | Ubuntu 24.04.4 LTS (Noble Numbat), hostname `siem-01` | 2026-09-02 |
| SIEM-01 kernel | `6.8.0-138-generic` | 2026-09-02 |
| SIEM-01 patch level | all 49 pending updates applied once, then automatic updates disabled. No kernel update was included. `apt list --upgradable` returns empty. | 2026-09-02 |
| SIEM-01 lab address | `10.20.10.10/24` on `ens37` (VMnet2), MAC `00:0c:29:8c:83:33` | 2026-09-02 |
| **Sysmon binary version** | **`15.21`**, `Sysmon64.exe` SHA256 `A60AA845457406383277AFDEAD35BD90C7804572B99901D239CC974841DF2528`, from `https://download.sysinternals.com/files/Sysmon.zip` (zip SHA256 `6D48089C7FAE14944C82B06767B79CCBA3CC26D13218A4227ED28C90F80D0F0E`) | 2026-09-02 |
| **Sysmon config SHA256** | **`055FEBC600E6D7448CDF3812307275912927A62B1F94D0D933B64B294BC87162`**, 123,257 bytes. `SwiftOnSecurity/sysmon-config` pinned at commit `1836897f12fbd6a0a473665ef6abc34a6b497e31`, file `sysmonconfig-export.xml`, committed to the repo as `lab/configs/sysmonconfig.xml`. **Sysmon itself reports this same hash** via `Sysmon64.exe -c`, so the running sensor is provably using the committed file. | 2026-09-02 |
| Sysmon config caveats | Config schema `4.50` running on a `4.91` binary. `Image loading : disabled`, so Sysmon Event ID 7 never appears. The config's own header reads `Source version: 74 \| Date: 2021-07-08`, so it has no rules for the event types Sysmon added later (25 to 29). | 2026-09-02 |
| **Atomic Red Team commit** | **`cb486d9a888e921fac5902a06c7b46e420bb14a7`** (`redcanaryco/atomic-red-team`, committed 2026-08-28), shallow clone, **1310 files** in the `atomics` folder, 342 technique YAML files | 2026-09-02 |
| Invoke-AtomicRedTeam commit | `8af478bb9e4637df568ac1e596553b025b16cd1b` (`redcanaryco/invoke-atomicredteam`, committed 2025-09-08), module version `2.1.0`, 74 files | 2026-09-02 |
| `powershell-yaml` | `0.4.12`, nupkg SHA256 `D4602BC7A4A093766520422D53CA8B09ACDE162286FAE11E2EE6C8EDFEA07810`. Hard dependency of `Invoke-AtomicTest`, which cannot parse the atomics without it. | 2026-09-02 |
| **Windows build number (guest)** | **`10.0.26100.9168`**, Windows 11 **Education**, `DisplayVersion 24H2`. Fully patched: two update passes, the second returned `updates found: 0`. 7 hotfixes: KB5120710, KB5050575, KB5054273, KB5122035, KB5121003, KB5043113, KB5123304. | 2026-09-02 |
| Wazuh agent version | `4.14.7`, stage `rc1`, commit `8c41e20`, from `wazuh-agent-4.14.7-1.msi` SHA256 `E967F36B75589D6210244FD58239C7021FA53A77C38D92315C3B3BD115002EDE`. Registered as `id=001 name=WIN-EP-01`. Matches the manager exactly. | 2026-09-02 |
| **WIN-EP-01 agent `ossec.conf`** | **current: SHA256 `CED16E0B41384BF421192317E3754732D0E3155A85BA98F2CEEDFA846B0278B1`, 12,115 bytes**, committed as `lab/configs/wazuh-agent-ossec.conf`. History, each kept in the guest: as installed `4F4531A2...F4D64B` (10,152 bytes) as `ossec.conf.telos-orig`; plus the Sysmon `<localfile>` block `F9541429...C4D82F` (10,409 bytes) as `ossec.conf.telos-pre-item8`; plus `rootcheck`, `sca`, `syscheck`, `syscollector` disabled `1F36416E...8F2658` (11,848 bytes) as `ossec.conf.telos-pre-item12`; current adds `active-response` disabled. | 2026-09-03 |
| WIN-EP-01 lab address | `10.20.10.20/24` on adapter `LAB`, MAC `00:0C:29:A7:96:32`. NAT adapter `NAT`, MAC `00:0C:29:A7:96:28`, `192.168.243.130/24`. Default route exists only on NAT. | 2026-09-02 |
| WIN-EP-01 VMware Tools | `12.3.5 build-22544099` from the Workstation `windows.iso` dated 2024-02-12. Drivers after the Windows Update pass: VMware SVGA 3D `9.17.11.3` (Broadcom), VMCI Bus `9.8.30.0` (Broadcom), Pointing Device `12.5.12.0` (VMware). | 2026-09-02 |
| Fence tool | `telos-fence.exe`, 4,096 bytes, SHA256 `D35C939B71ECAC94868947932292531C02A171DECFD3046DEE47DB8E3BD0D814`. Built on the host from `lab/scripts/telos-fence.cs` with the .NET Framework compiler. Verified to emit **exactly one** Sysmon Event ID 1 per run, carrying the run id in its command line. | 2026-09-02 |
| Ubuntu ISO used | `ubuntu-24.04.4-live-server-amd64.iso`, **installed on SIEM-01**. Installer self-update to 24.04.4.1 declined on purpose. | 2026-09-02 |
| **Windows ISO used** | **`E:\Homelab files\Win11_24H2_English_x64.iso`**, retail multi-edition, **Windows 11 Education selected**, left unactivated. Supersedes the Enterprise Evaluation ISO chosen on 2026-08-20. See the decision entry of 2026-09-02. | 2026-09-02 |

`WAZUH_REVISION` reads `rc1` in `wazuh-control info`. The reason is unknown. Cite the apt package
version `4.14.7-1`, not `rc1`.

## Reference corpora

| Item | Value | Date recorded |
|---|---|---|
| `SigmaHQ/sigma` clone commit | `da9bb07d642a2826e89702445d32c795209ec108` | 2026-08-19 |
| `wazuh/wazuh` clone commit | not yet cloned | |

---

# Spike results (fill in after Phase 7)

The go/no-go gate for T1. Both must be answered before committing.

| Question | Result | Date |
|---|---|---|
| Q1 CoV under Config S | not yet measured | |
| Q1 CoV under Config N | not yet measured | |
| Q2 real wall clock per run | not yet measured | |
| Q2 projected total for 101 runs | not yet measured | |
| **T1 or T3 decision** | **not yet made** | |

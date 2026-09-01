# Decision Log

Every choice that would be expensive to reverse, or that you will forget the reason for.
Newest at the top. Never delete an entry. If a decision is reversed, add a new entry that
says so and link back.

Format: date, the decision, why, and what it costs if wrong.

---

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
match between the final paper and the student's own public repo is not treated as an issue.

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
| Sysmon binary version | not yet recorded | |
| Sysmon config SHA256 | not yet recorded | |
| Atomic Red Team commit | not yet recorded | |
| Windows build number (guest) | not yet recorded | |
| Ubuntu ISO used | `ubuntu-24.04.4-live-server-amd64.iso`, **installed on SIEM-01**. Installer self-update to 24.04.4.1 declined on purpose. | 2026-09-02 |
| Windows ISO used | `Windows 11 Enterprise Eval 26200.6584...25h2` (selected, not yet installed) | 2026-08-20 |

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

# Work Log

What actually happened, session by session. Newest at the top.

This exists because you forget things. Write an entry every time you sit down, even a short
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
per the procedure already given. Waiting on the student to report each step's result.

---

## 2026-08-31 (fourth session) - Adapter fix confirmed. Phase 1 complete.

**Did:** Verified the fix after the student ran Virtual Network Editor → Restore Defaults and
reconfigured vmnet2/vmnet3, per the steps from the previous session.

**Result: fixed.** All three checks that failed before now pass.

| Check | Before | After |
|---|---|---|
| Driver status (`Get-PnpDevice`) | Error, all three | OK, all three |
| Adapter status | Not Present / Down | Up / Up |
| VMnet2 IP | none | **10.20.10.1/24** |
| VMnet3 IP | none | **10.20.20.1/24** |
| DHCP on 10.20.10.0 or 10.20.20.0 | n/a | confirmed absent from `vmnetdhcp.conf` |

The student set both subnets exactly as specified and connected the host adapter on vmnet2
only, matching the runbook. No correction needed.

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

**Fix prescribed, not yet done (needs the GUI, is the student's step):**
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

**Next:** waiting on the student to run the Virtual Network Editor steps above. Phase 1 is
not complete until `Get-NetIPAddress` confirms 10.20.10.1.

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

**Two decisions taken as assumptions, still unconfirmed by the student:**
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

**Also did:** Wrote [DEFENSE-PREP.md](DEFENSE-PREP.md), a full preparation guide for the pre-oral
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

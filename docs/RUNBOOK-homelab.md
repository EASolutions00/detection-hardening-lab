# RUNBOOK: Build the T1 Homelab From Scratch

Purpose: rebuild the whole lab from a bare host, in order, without remembering anything.
Follow top to bottom. Every phase ends with a check. Do not skip a check.

If you are only doing T2 or T3, skip to Phase 8. Those topics need no lab.

Host: Ryzen 7950X (16C/32T), 64 GB RAM, VMware Workstation 17.5.1 Pro.
Drives: C: NVMe (host, Python) - F: NVMe (all VMs) - E: HDD (this repo, archives, backups).

**The one rule that breaks the thesis if broken: no VM ever runs from E:.**
E: is a hard disk. Its seek delay changes process timing, which changes event
order and counts, which lands straight in the coefficient of variation number
that T1's entire statistics argument rests on. You would be measuring your disk.

---

## Phase 0. Before you start

- [ ] Confirm F: has at least 350 GB free.
- [ ] Confirm virtualization is on in BIOS (AMD SVM).
- [ ] Download ISOs to E:\iso\ : Ubuntu Server 22.04 or 24.04 LTS, Windows 11 Enterprise Eval
      (or Server 2022 Eval).
- [ ] Install Python 3.11+ on C:. Create a venv. Do not use system Python.
- [ ] Note the path to `vmrun.exe`. Default is
      `C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe`.
- [ ] Open `docs/DECISIONS.md` and `docs/WORKLOG.md`. You will write in both as you go.

**Check:** `vmrun.exe -T ws list` runs and prints a total. If it errors, stop and fix VMware first.

---

## Phase 1. Virtual networks

Open VMware Workstation, then Edit menu, then Virtual Network Editor, then Change Settings
for admin rights.

- [ ] `vmnet2` = Host-only. **Turn DHCP OFF.** Subnet 10.20.10.0/24.
      Leave "Connect a host virtual adapter" ON. The harness needs to reach the Wazuh API.
- [ ] `vmnet3` = Host-only. DHCP OFF. Subnet 10.20.20.0/24. Tier B only, skip for now.
- [ ] `vmnet8` = NAT. Leave default. This is for installing and patching only.

Every VM gets a static IP. DHCP lease renewal is itself a logged event, and it fires
on its own schedule inside your measurement window.

Planned addresses:

| Host | IP |
|---|---|
| Windows host (vmnet2 adapter) | 10.20.10.1 |
| SIEM-01 | 10.20.10.10 |
| WIN-EP-01 | 10.20.10.20 |

**Check:** `ipconfig` on the host shows a VMware adapter on 10.20.10.x.

---

## Phase 2. Build SIEM-01 (Wazuh)

VM spec: 8 vCPU, 16 GB RAM, 200 GB thin disk, **stored on F:**. Ubuntu LTS.

- [ ] Create the VM on F:. Attach vmnet8 (NAT) for now so you can install.
- [ ] Install Ubuntu Server. Enable OpenSSH during install.
- [ ] Set static IP 10.20.10.10 on the vmnet2 adapter.
- [ ] Install Wazuh all-in-one with the official assistant:

```bash
curl -sO https://packages.wazuh.com/4.x/wazuh-install.sh && sudo bash ./wazuh-install.sh -a
```

- [ ] **Write down the version and the admin password the installer prints.** Put the version in
      `docs/DECISIONS.md`. Put the password in a password manager, never in this repo.
- [ ] **Disable the Wazuh repo immediately.** An auto-upgrade halfway through the experiment
      invalidates every run you already did:

```bash
sudo sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list && sudo apt update
```

- [ ] Turn on full archiving. Edit `/var/ossec/etc/ossec.conf` and set inside `<global>`:

```xml
<logall_json>yes</logall_json>
```

This is the single setting that makes T1 possible. Without it Wazuh keeps only events that
fired a rule. T1 counts what the machine *emits*, not what alerted.

- [ ] Restart: `sudo systemctl restart wazuh-manager`
- [ ] Set indexer replicas to 0 (single node) and shorten retention. Archives grow fast.

**Check:** `sudo ls -lh /var/ossec/logs/archives/` shows `archives.json` and it is growing.

---

## Phase 3. Build WIN-EP-01 (endpoint)

VM spec: 4 vCPU, 8 GB RAM, 80 GB thin disk, **stored on F:**.

- [ ] Create the VM on F:. Attach vmnet8 (NAT) for now.
- [ ] Install Windows. Install **VMware Tools**. This is required, `vmrun` guest commands
      will not work without it.
- [ ] Fully patch Windows now, while NAT is still connected. You will disconnect it later
      and it must never need updates again.
- [ ] Set static IP 10.20.10.20 on the vmnet2 adapter.
- [ ] Install Sysmon with a pinned config:

```powershell
.\Sysmon64.exe -accepteula -i sysmonconfig.xml
```

Copy that exact config into `lab/configs/`. Record its SHA256 hash. A Sysmon config change
is itself a telemetry change and would silently ruin comparisons across runs.

- [ ] Install the Wazuh agent, point it at 10.20.10.10, and add a `<localfile>` block for
      the Sysmon channel `Microsoft-Windows-Sysmon/Operational`.
- [ ] Install Atomic Red Team, then record the commit:

```powershell
Install-AtomicRedTeam -getAtomics
```

- [ ] Copy your fence tool into the guest. This is a small uniquely named binary or script
      that produces one distinctive Sysmon EventID 1 when run. You will use it to mark the
      start and end of every capture window from inside the telemetry itself, which is far
      more reliable than host clock time.

**Check:** run one atomic test, then confirm the event reaches `archives.json` on SIEM-01.
If it does not arrive, nothing later in this runbook will work.

---

## Phase 4. Pin and record everything

Write all of these into `docs/DECISIONS.md` before taking any snapshot:

- [ ] Wazuh version
- [ ] Sysmon binary version and config SHA256
- [ ] Atomic Red Team commit hash
- [ ] Windows build number
- [ ] Harness git commit (once written)

A version bump partway through means every earlier run is no longer comparable and
must be discarded. This list is your defense against that.

---

## Phase 5. Snapshots

**Disconnect the NAT adapter (vmnet8) before the golden snapshot.** If the endpoint can
reach the internet during a capture, Windows Update, Defender cloud lookups, certificate
revocation checks, and time sync all fire on their own schedules. Every one of them injects
noise into the exact window you are measuring.

- [ ] Shut down WIN-EP-01 cleanly.
- [ ] **Disconnect** vmnet8. Do not remove the adapter. Leave vmnet2 as the only connected
      network.

      Disconnect rather than remove because the lab interface is the *second* adapter on
      SIEM-01 (`ethernet0` is NAT, `ethernet1` is vmnet2), and its Linux interface name
      (`ens34` or similar) is what the netplan static-IP config in Phase 2 targets. Deleting
      an adapter can renumber the remaining one and break that config. Unchecking "Connected"
      in VM settings leaves the device present and the name stable. `(unverified whether
      removal actually renumbers on this setup; disconnect is the safe choice either way)`
- [ ] Boot once, confirm no internet, shut down.
- [ ] Take snapshot `golden-base`.
- [ ] Boot, apply Config S (Defender off, Windows Update off, scheduled tasks disabled),
      shut down, snapshot `cfg-suppressed`.
- [ ] Revert to `golden-base`. Boot, leave defaults on, shut down, snapshot `cfg-natural`.

Tree you should end with:

```
WIN-EP-01
└── golden-base
    ├── cfg-suppressed     (Config S)
    └── cfg-natural        (Config N)
```

**Do not make 16 snapshots for the 16 hardening changes.** Revert to a config snapshot and
apply the change by script instead. The script is version controlled and auditable, which is
what your reproducibility claim needs. Sixteen branching snapshot chains would also fill F:.

**Check:** `vmrun -T ws listSnapshots <path-to-vmx>` prints exactly the three above.

---

## Phase 6. The capture harness

Write this in Python on the host, in `src/`. It runs on the **Windows host, not in a VM**,
because `vmrun.exe` is local and the Wazuh API is reachable over vmnet2.

One capture window, in order:

1. `vmrun -T ws revertToSnapshot <vmx> cfg-suppressed`
2. `vmrun -T ws start <vmx> nogui`
3. Wait for VMware Tools, then **settle 180 seconds**. Boot produces an event storm.
   Do not count it.
4. Fire the **start fence**.
5. If this is a post-change run: apply the hardening change by script, reboot if needed,
   settle again.
6. Run the Atomic Red Team suite over the pinned technique list.
7. Fire the **end fence**.
8. **Drain 120 seconds.** The agent buffers and the manager writes to disk. Cutting the
   window at test completion loses the tail.
9. `vmrun -T ws stop <vmx>`
10. Over SSH to SIEM-01: rotate `archives.json`, gzip it, copy to
    `data/runs/<run_id>/`, then **truncate the file on SIEM-01**.
11. Write `data/runs/<run_id>/run_manifest.json` with every field listed in Phase 4.

Guard the harness: check free space on F: before each run and abort cleanly if low.
Running out of disk halfway through a 67 hour batch is the failure that hurts most.

**Check:** one full unattended run completes and produces a run folder plus a manifest.

---

## Phase 7. The feasibility spike (the go/no-go gate)

Do not build Tier B. Do not write the analysis engine yet. Answer two questions.

**Q1. What is the run to run coefficient of variation?**
Run the identical suite 5 times against the same restored snapshot with zero config change.
Do it under Config S and again under Config N. Compute CoV per event type. Save to
`data/summaries/cov_control_runs.csv`.

- CoV above zero under Config N: the statistics layer is justified in the lab, and naive
  differencing will produce measurable false positives. T1's headline result exists.
- CoV near zero under both: the statistics layer buys nothing in the lab. T1's proposal
  already commits to reporting that honestly, but a panel will read it as a null result.

**Q2. What is the real wall clock per run?**
Time 5 unattended end to end runs. Multiply by 101. Save to `data/summaries/run_timings.csv`.
101 runs at 40 minutes is about 67 hours. That works overnight and on weekends only if the
harness is fully unattended. Semi-automated, it does not finish before the defense.

- [ ] Record both answers in `docs/DECISIONS.md`.
- [ ] Make the T1 versus T3 call and write down the reason.

---

## Phase 8. T2 and T3 environment (no lab needed)

Both are offline static analysis. No SIEM, no log ingestion, no network during analysis.
Under 10 GB total. Runs on a laptop.

- [ ] WSL2 Ubuntu, or just the Windows host with Python 3.11+.
- [ ] `pip install lxml pyyaml networkx scikit-learn pandas`
- [ ] Clone the corpora and **pin each to a named commit**, then record the hashes in
      `docs/DECISIONS.md` and in the paper:

```bash
git clone https://github.com/wazuh/wazuh.git
git clone https://github.com/SigmaHQ/sigma.git
```

Pinning is not optional. Both repos change weekly. An unpinned corpus means your numbers
cannot be reproduced by anyone, including you. T3's own literature review cites sigmalint
pinning commit `994da16` for exactly this reason.

- [ ] Optional: one Wazuh VM to spot check T2 findings with `wazuh-logtest`. Not needed
      for the analysis itself.

---

## If something breaks

| Symptom | Most likely cause |
|---|---|
| `vmrun` guest commands fail | VMware Tools not installed, or wrong guest credentials |
| No events in `archives.json` | `logall_json` not set, or manager not restarted |
| Agent shows disconnected | Static IP wrong, or vmnet2 has DHCP still on |
| F: fills mid batch | Archives not truncated after each run (Phase 6 step 10) |
| Counts drift between runs | Something updated. Check the Phase 4 pin list |
| Credential Guard change fails | Nested virtualization not enabled. See OPEN-QUESTIONS.md |

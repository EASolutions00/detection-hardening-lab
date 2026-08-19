# Homelab Blueprint: Detection-Engineering Thesis Lab (T1 / T2 / T3)

Host: Ryzen 7950X (16C/32T), 64 GB RAM, VMware Workstation 17.5.1 Pro
Drives: C: NVMe (345 GB free) · E: HDD (2371 GB free) · F: NVMe (727 GB free)

Sourcing note: hardware figures for Wazuh come from Wazuh docs (linked inline). VM
sizing, run-time estimates, and the hardening-change catalogue are engineering
judgment, labeled `(unverified)` where they are not from a named source.

---

## 0. Which topic actually needs a lab

| Topic | Lab requirement | Verdict |
|---|---|---|
| T1 Differential event-stream alignment | Full purple-team lab, snapshot automation, ~101 capture runs | **Load-bearing.** Everything below exists for this. |
| T2 Severity inversion (Wazuh ruleset) | `git clone` + Python. One VM only to run `wazuh-logtest` for spot-checks. | Not load-bearing. |
| T3 Analytic-robustness scoring (Sigma/Wazuh) | `git clone` + Python. No SIEM at all. | Not load-bearing. |

T2 and T3 are declared in their own proposals as offline static analysis with
"no log ingestion, no network access during analysis." Build the lab only if you
are committing to T1, or if you are running the T1 feasibility spike (Section 7).

---

## 1. Resource budget

Reserve **12 GB and 4 threads for the Windows host** (Workstation UI, browser,
editor, the Python harness itself). That leaves ~52 GB and ~28 threads for VMs.

### Tier A — minimum viable T1 lab (build first)

| VM | Role | vCPU | RAM | Disk (thin) | Datastore |
|---|---|---|---|---|---|
| `SIEM-01` | Wazuh 4.x all-in-one (manager + indexer + dashboard), Ubuntu 22.04/24.04 LTS | 8 | 16 GB | 200 GB | F: |
| `WIN-EP-01` | Windows 11 Enterprise Eval or Server 2022 Eval. Sysmon + Wazuh agent + Atomic Red Team | 4 | 8 GB | 80 GB | F: |
| **Total** | | **12** | **24 GB** | 280 GB | |

Wazuh's own quickstart table gives 4 vCPU / 8 GiB / 50 GB for 1–25 agents
(https://documentation.wazuh.com/current/quickstart.html). That figure is for
**alerts only**. T1 needs `logall_json` archives enabled, which stores every
received event whether or not it triggers a rule, and the docs explicitly warn
this consumes significant storage and performance
(https://documentation.wazuh.com/current/user-manual/manager/event-logging.html).
16 GB and 200 GB is the headroom for that, not padding. `(unverified)` as a
precise figure; measure actual indexer heap and archive growth in week 1.

### Tier B — optional, add only if the spike says you have time

| VM | Role | vCPU | RAM | Disk | Datastore |
|---|---|---|---|---|---|
| `DC-01` | Server 2022 Eval, AD DS + DNS. Enables GPO-delivered hardening and identity telemetry (4768/4769/4776) | 2 | 6 GB | 60 GB | F: |
| `LNX-EP-01` | Ubuntu, auditd + Wazuh agent. Second OS for the "heterogeneous sources" claim | 2 | 3 GB | 40 GB | F: |
| `IDS-01` | Suricata on a mirrored segment, feeding Wazuh. Provides the network-IDS event class | 2 | 4 GB | 60 GB | F: |

Tier A + B = 18 vCPU, 37 GB. Plus 12 GB host = 49 GB of 64. Fits with margin.

**Rule: suspend all Tier B VMs during actual capture runs.** Concurrent VM
activity is a variance source, and variance is the thing T1 is measuring.

### The orchestrator is not a VM

`vmrun` lives on the Windows host. Run the Python harness on the host directly,
calling `vmrun` locally and the Wazuh API over the host-only network. This saves
a VM, saves 4 GB, and removes a hop from the snapshot control path.

---

## 2. Storage layout

| Drive | Type | Purpose | Never put here |
|---|---|---|---|
| **C:** | NVMe | Host OS, VMware install, Python + venv, harness source, pinned git clones of `wazuh/wazuh` ruleset and `SigmaHQ/sigma` | VM disks |
| **F:** | NVMe | **Active VM datastore.** All `.vmx`, `.vmdk`, snapshot deltas | Archives (they will eat it) |
| **E:** | HDD | Cold storage: per-run exported `archives.json.gz`, full-clone VM backups, ISO library, results, thesis doc | **Any running VM** |

**The single most consequential decision here: never run a VM off E:.** HDD seek
latency jitter injects timing nondeterminism into process scheduling, which
changes event ordering and counts. That noise lands directly in the
coefficient-of-variation figure T1's entire statistical justification rests on.
You would be measuring your disk, not your hypothesis.

F: has 727 GB free. 280 GB of Tier A VMs plus snapshot deltas plus a growing
`archives.json` will get tight. Mitigation is in the run protocol: export and
truncate archives after every run.

---

## 3. Network design

Three vmnets, configured in Workstation's Virtual Network Editor:

| vmnet | Type | Subnet (suggested) | Members | Purpose |
|---|---|---|---|---|
| `vmnet2` | Host-only, **DHCP off** | 10.20.10.0/24 | WIN-EP-01, DC-01, LNX-EP-01, SIEM-01 | Lab traffic + agent-to-manager. Host has an interface here so the harness reaches the Wazuh API. |
| `vmnet3` | Host-only, DHCP off | 10.20.20.0/24 | IDS-01 (promiscuous) | Suricata monitor segment (Tier B only) |
| `vmnet8` | NAT | default | **Disconnected during all captures** | Build and patch only |

Static IPs everywhere. DHCP lease renewal is an event source.

**Critical: take the golden snapshot with NAT disconnected.** If the endpoint can
reach the internet during a capture window, Windows Update, Defender cloud
lookups, connected-user-experience telemetry, certificate revocation checks, and
NTP all fire on their own schedules. Every one of them is unschedulable variance
injected into the exact window you are measuring.

---

## 4. Software stack

**SIEM-01 (Ubuntu LTS)**
- Wazuh 4.x all-in-one via the installation assistant, **version pinned**. The
  docs recommend disabling the Wazuh repo after install to prevent accidental
  upgrades (same quickstart page). Do this. A mid-experiment version bump
  invalidates every prior run.
- `ossec.conf`: `<logall_json>yes</logall_json>` — this is the setting that makes
  T1 possible at all. Without it Wazuh stores only events that triggered a rule,
  and T1's unit of analysis is the *event type emitted*, not the alert fired.
- Indexer: set replicas to 0 (single node). Reduce ILM retention aggressively.
- Optionally leave the dashboard installed for the defense demo but analyze from
  `archives.json` on disk, not through the indexer.

**WIN-EP-01**
- Sysmon with a pinned config (record the config hash in run metadata; a Sysmon
  config change is itself a telemetry change).
- Wazuh agent with a `<localfile>` block for
  `Microsoft-Windows-Sysmon/Operational`.
- Atomic Red Team via `Install-AtomicRedTeam -getAtomics`, **cloned at a pinned
  commit and then taken offline.** The Wazuh docs walk through exactly this
  Sysmon + ART + archives combination as a worked example
  (https://documentation.wazuh.com/current/user-manual/manager/event-logging.html).
- VMware Tools installed (required for `vmrun` guest operations).

**Host (Windows)**
- Python 3.11+, venv on C:
- `vmrun.exe` from `C:\Program Files (x86)\VMware\VMware Workstation\`

---

## 5. Snapshot topology

```
WIN-EP-01
├── SNAP: golden-base          (built, patched, NAT removed, ART pinned, sealed)
│   └── SNAP: cfg-suppressed   (Config S: Defender off, WU off, tasks disabled)
│   └── SNAP: cfg-natural      (Config N: defaults left on)
```

Do **not** create 16 post-change snapshots. Revert to the config snapshot, then
apply the hardening change by script. This keeps the change itself version-
controlled and auditable, which is what the proposal's reproducibility claim
requires, and avoids 16 branching delta chains on F:.

---

## 6. The run protocol

Each capture window, driven by the host harness:

1. `vmrun revertToSnapshot <vmx> cfg-suppressed`
2. `vmrun start <vmx> nogui`
3. Poll for VMware Tools ready, then **settle 180 s** (let boot-time event storm
   drain and stop counting it)
4. Emit **start fence**: run a uniquely-named binary/command that produces a
   distinctive Sysmon EventID 1. This timestamps the window from *inside the
   telemetry*, which is more reliable than host wall-clock.
5. If post-change phase: `vmrun runScriptInGuest` → apply the hardening change,
   reboot if required, settle again
6. `vmrun runScriptInGuest` → `Invoke-AtomicTest` over the pinned technique list
7. Emit **end fence** (second distinctive event)
8. **Drain 120 s.** Agent buffering and manager write to `archives.json` are not
   instantaneous. Cutting the window at ART completion loses tail events.
9. `vmrun stop <vmx>`
10. Over SSH to SIEM-01: rotate `archives.json`, `gzip`, pull to
    `E:\runs\<run_id>\`, then **truncate on the SIEM**
11. Write `run_manifest.json`: run_id, phase, change_id, git commit of harness,
    Sysmon config hash, ART commit, Wazuh version, fence timestamps, host load

`vmrun` supports `revertToSnapshot`, `start`, `stop`, `runProgramInGuest`,
`runScriptInGuest`, and `copyFileFromGuestToHost` on Workstation Pro 17
(Broadcom TechDocs, Workstation Pro 17 vmrun reference). Guest operations need
VMware Tools installed.

### Run count and time budget

Per T1's stated design: 16 changes × (3 pre + 3 post) = 96, plus 5 control runs
= **101 capture windows** minimum.

Estimated wall clock per run `(unverified — measure this in week 1)`:

| Phase | Estimate |
|---|---|
| Revert + boot | 2–4 min |
| Settle | 3 min |
| Change application + reboot | 0–5 min |
| ART suite | 10–40 min (depends on technique count) |
| Drain + export + truncate | 4–6 min |
| **Total** | **~25–60 min** |

101 runs × 40 min ≈ **67 hours of wall clock.** That is achievable overnight and
across weekends **only if the harness is fully unattended.** Semi-automated, it
does not finish. This is the hard constraint on T1.

---

## 7. The two-week feasibility spike (do this before committing)

Build Tier A only. Do not build Tier B. Do not write the analysis engine yet.
Run one hardening change and answer two pre-declared questions:

**Q1 — What is the run-to-run coefficient of variation?**
Execute the identical ART suite 5 times against the same restored snapshot with
zero configuration change. Compute CoV per event type. Do this under **both**
Config S (suppressed) and Config N (natural).

- CoV(N) meaningfully > 0 → the statistical layer has an in-lab justification,
  and the naive-differencing baseline will produce false positives you can
  measure. **T1's headline result exists.**
- CoV(S) ≈ 0 and CoV(N) ≈ 0 → the statistical layer confers no in-lab advantage.
  T1's proposal already commits to reporting this honestly, but a panel is
  likely to read it as a null result.

Reporting both configurations is a genuine methodological improvement over the
proposal as written. It pre-empts the sharpest available objection: that the
false-positive reduction you measure is an artifact of how aggressively you
suppressed background activity.

**Q2 — What is the real per-run wall clock?**
Time 5 unattended end-to-end runs. Multiply by 101. If the result exceeds the
hours you actually have between now and the December defense, T1 is not
deliverable and the answer is T3.

---

## 8. T1 ground-truth labeling (the part the proposal underspecifies)

Precision/recall requires a label for every event type in every run. You cannot
hand-label ~200–500 event types across 16 changes. Use two-tier labeling:

- **Positive class (provably lost):** event types you deliberately and verifiably
  removed by the change. Example: disabling the *Audit Process Creation*
  subcategory provably removes 4688. You know the ground truth because you caused
  it.
- **Negative class:** every other event type present in the pre-change profile.

This yields a defensible labeled set without exhaustive manual annotation.
Document it explicitly in Chapter 3 — a panelist will ask where the labels came
from, and "the tool told us" is not an answer.

### Candidate hardening-change catalogue (16)

`(unverified — general domain knowledge. Each must be pinned to a specific CIS
Benchmark or DISA STIG control ID, and each must be verified to actually change
telemetry in your lab. Some will produce no measurable change, which is a valid
finding to report.)`

1. Disable *Audit Process Creation* subcategory → removes 4688
2. Disable `ProcessCreationIncludeCmdLine_Enabled` → 4688 loses CommandLine
3. Disable PowerShell ScriptBlock logging → removes 4104
4. Disable PowerShell Module logging → removes 4103
5. Remove PowerShell v2 engine → closes the downgrade path
6. Enforce Constrained Language Mode → changes 4104 content
7. Disable WDigest → alters 4624 logon-type distribution
8. Enable Credential Guard → alters Sysmon EventID 10 (LSASS access)
9. Disable SMBv1 → removes SMB1 protocol events / IDS signatures
10. Restrict NTLM → removes/reduces 4776
11. Disable Windows Script Host → removes cscript/wscript process creation
12. Disable LLMNR and NBT-NS → removes name-resolution network events
13. Disable Remote Registry → removes a 4624 type-3 subset
14. Disable Print Spooler → removes spooler operational events
15. Narrow the Sysmon config (hardening the sensor itself) → removes EventIDs
16. Enforce RDP NLA → alters 4624/4625 distribution

Item 8 requires **nested virtualization** (Virtualize Intel VT-x/EPT or AMD-V/RVI
in VM settings) for VBS inside the guest. `(unverified on Zen 4 + Workstation
17.5.1 — test this before including item 8.)`

---

## 9. T2 / T3 environment (minimal)

No lab needed. On the host:

- WSL2 Ubuntu, or a single 2 vCPU / 4 GB Ubuntu VM if you prefer isolation
- `git clone` of `wazuh/wazuh` (ruleset) and `SigmaHQ/sigma`, both **pinned to a
  named commit** and the commit hash recorded in the paper. T3's own literature
  review notes that sigmalint pinned commit `994da16` for exactly this reason.
- Python 3.11+, `lxml`, `pyyaml`, `networkx`, `scikit-learn` (for Cohen's kappa
  in T3), `pandas`
- One Wazuh VM only if you want `wazuh-logtest` to spot-check T2 findings. Not
  required for the analysis itself.

Total footprint: under 10 GB. Both topics run on a laptop.

---

## 10. Build order

| Week | Task |
|---|---|
| 1 | Virtual Network Editor setup. Build SIEM-01, install Wazuh, pin version, enable `logall_json`, disable repo. |
| 1 | Build WIN-EP-01, Sysmon + agent + ART pinned. Verify events land in `archives.json`. |
| 2 | Golden snapshot. Config S / Config N snapshots. Write the `vmrun` harness (steps 1–11 above). |
| 2 | **Run the spike (Section 7). Record CoV and wall clock.** |
| 2 | **Go/no-go decision on T1 vs T3.** |
| 3+ | If T1: profile builder, then the statistical engine, then the dependency index. Data collection must start no later than end of September. |
| 3+ | If T3: parser, condition-tree traversal, STP knowledge base, kappa validation. |

---

## 11. Named risks

| Risk | Impact | Mitigation |
|---|---|---|
| Harness not unattended by end of Sept | T1 undeliverable | Spike gate at week 2 |
| CoV ≈ 0 under both configs | T1 headline result collapses to "justified only in production" | Report both configs; pre-declare the outcome as falsifiable, per the proposal's own framing |
| `archives.json` fills F: | Runs fail mid-experiment | Export + truncate every run; monitor free space in the harness and abort cleanly |
| Wazuh auto-upgrade mid-experiment | All prior runs invalidated | Disable the repo at install |
| Nested virt unavailable for VBS | Drop change #8 | Test in week 1; substitute another change |
| **T3-specific:** the manually annotated STP subset in SigmaHQ may be too small for a meaningful Cohen's kappa | T3's entire Objective 5 fails | **Verify the annotation count before committing to T3.** This is a hard prerequisite and is currently unverified. |

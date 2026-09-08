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
10. Over SSH to SIEM-01: **export the dated archive for the run's date** with
    `sudo -n /usr/local/sbin/telos-archive export YYYY-MM-DD`, pull the `.gz` to
    `E:\runs\<run_id>\`, and **verify** it against the `sha256_gz` and `lines`
    the export command printed. **Do not truncate anything.**
11. Write `run_manifest.json`: run_id, phase, change_id, git commit of harness,
    Sysmon config hash, ART commit, Wazuh version, fence timestamps, host load

### Why step 10 no longer truncates (changed 2026-09-03)

The original step said "rotate `archives.json`, gzip, pull, then truncate on the
SIEM". That was written before anyone looked at how Wazuh stores archives, and it
was wrong in two ways.

**Wazuh already rotates, at the day boundary, and `archives.json` is a hard link.**

```
-rw-r----- 2 wazuh wazuh 5272919 Sep  3 08:19 archives.json
          ^ link count 2: the same file also lives at YYYY/Mon/ossec-archive-DD.json
```

1. **A run crossing midnight splits across two files.** 101 runs of 25 to 60
   minutes will run overnight. Reading `archives.json` would export half a run and
   report success.
2. **Truncating `archives.json` empties the dated archive too**, because it is one
   file with two names. That step does not clear a scratch file, it destroys the
   day's permanent record.

**So the protocol reads by date and never truncates.** Disk is managed by Wazuh's
own rotation plus a retention policy, and the harness watches free space with
`telos-archive disk` and aborts cleanly when it gets low, which the risk table
already required.

**A second benefit, and it is worth stating in Chapter 3.** With truncation gone,
`telos-archive` has no destructive subcommand at all, so the single sudoers rule
grants the harness account **read and export only**. It cannot alter or delete the
evidence store. "How do you know your archives were not modified?" now has a
checkable answer instead of an assurance.

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

### Hardening-change catalogue

Rebuilt 2026-09-08. The previous list is preserved in git history. Four of its sixteen items
were the **opposite** of what the benchmarks require, one had no benchmark control at all, and
six removed the attack along with the telemetry. See OPEN-QUESTIONS item 1 for the analysis.

**A change qualifies as a blind-spot candidate only when all four hold:**
(a) it is a control from a named benchmark, with the control ID recorded;
(b) it removes or degrades an event type or a required field;
(c) at least one detection rule depends on that evidence;
(d) **the technique that rule covers is still executable after the change.**

**The pattern that separates the classes.** Class C changes alter *how* something happens.
Class B changes stop it happening at all. That is why almost every class C candidate is an
authentication control: authentication survives the change, it just proceeds differently.

---

#### Class C: positive cases, where a blind spot can exist

| # | Change | Control ID | Setting | Expected telemetry effect | Why the attack survives |
|---|---|---|---|---|---|
| C1 | Disable WDigest | **DISA V-253358** (Win11)<br>V-220800 (Win10) | `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\Wdigest\UseLogonCredential = 0` | 4624 logon-type distribution shifts | Credential theft is still attempted; the attacker gets hashes instead of plaintext |
| C2 | LAN Manager auth level, NTLMv2 only | **DISA V-253462** (Win11)<br>V-220938 (Win10)<br>**CIS 2.3.11.7** | `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\LmCompatibilityLevel = 5` | 4776 package name changes | Authentication continues at a higher level |
| C3 | LSA Protection (LSASS as protected process) | **CIS Win11 18.9.27.2**, Level 1 | `HKLM\System\CurrentControlSet\Control\Lsa\RunAsPPL = 1` | Sysmon Event 10 access to `lsass.exe` changes from granted to denied | LSASS access is still attempted; documented bypasses exist |
| C4 | Restrict NTLM, outgoing traffic to remote servers | **CIS 2.3.11.13**<br>DISA Win11 V-ID `(unverified)` | `HKLM\System\CurrentControlSet\Control\Lsa\MSV1_0\RestrictSendingNTLMTraffic` | 4776 reduced or removed | Authentication continues via Kerberos |
| C5 | Enforce RDP Network Level Authentication | `(unverified)` | `UserAuthentication = 1` | 4624 / 4625 distribution shifts | RDP is still used; authentication happens earlier |
| C6 | Reduce cached credentials to 0 | `(unverified)` | `CachedLogonsCount = 0` | Cached and offline logon events reduced | Logon still occurs, against the domain instead |
| C7 | Disable RC4 for Kerberos | `(unverified)` | Kerberos supported encryption types | 4768 / 4769 ticket encryption fields change | Kerberos authentication continues with AES |
| C8 | Enable Credential Guard | `(unverified)` | VBS-based | Sysmon Event 10 to `lsass.exe` changes | Credentials are still used, just isolated |

**Verified 2026-09-08:** C1, C2 and C3 have confirmed control IDs. C4 has a confirmed CIS
number and registry path; its Windows 11 DISA V-ID is not confirmed. C5 to C8 have correct
settings but **unverified IDs**.

**C8 is blocked** on nested virtualisation (Virtualize AMD-V/RVI in VM settings), still untested
on Zen 4 with Workstation 17.5.1. See OPEN-QUESTIONS item 2. Do not count on it.

---

#### Class B: negative controls, where telemetry is lost but no blind spot exists

These are kept **on purpose**, not by oversight. The change removes the telemetry *and* the
attack, so the correct impact score is near zero. They test whether the scorer can tell a lost
capability from a lost detection. A scorer that flags these is wrong.

| # | Change | Control ID | Expected telemetry effect | Why it is not a blind spot |
|---|---|---|---|---|
| B1 | Remove PowerShell v2 engine | `(unverified)` | Closes the downgrade path | The v2 downgrade attack is gone |
| B2 | Disable SMBv1 | `(unverified)` | Removes SMB1 protocol events | There is no SMB1 traffic to attack |
| B3 | Disable Windows Script Host | `(unverified)` | Removes cscript/wscript process creation | cscript cannot run |
| B4 | Disable LLMNR and NBT-NS | `(unverified)` | Removes name-resolution events | LLMNR poisoning is no longer possible |
| B5 | Disable Remote Registry | `(unverified)` | Removes a 4624 type-3 subset | The service is gone |
| B6 | Disable Print Spooler | `(unverified)` | Removes spooler operational events | The service is gone |

---

#### Removed from the catalogue

| Was | Why removed |
|---|---|
| Disable Audit Process Creation | **CIS requires this ON** (17.3.1 / 17.3.2). Disabling it is de-hardening. |
| Disable `ProcessCreationIncludeCmdLine_Enabled` | **CIS requires this ON** (18.9.3.1 / 18.8.3.1). |
| Disable PowerShell ScriptBlock logging | **DISA STIG WN10-CC-000326 / V-220860 requires this ON**, CAT II. |
| Disable PowerShell Module logging | Benchmarks require it enabled. |
| Narrow the Sysmon config | Genuine tool hardening, but **no CIS or DISA control exists**, so it cannot be described as drawn from a published baseline. |
| Enforce Constrained Language Mode | Class C by definition, but it changes 4104 **content** while the rate and the field both stay populated. The method measures presence, not meaning. Out of scope; see the Scope and Limitations note on value-level degradation. |

The CommandLine case is still useful as a **capability demonstration** of field-level detection,
clearly labelled as not one of the evaluated changes, because CIS requires that setting enabled.

---

#### Current count and what is still needed

| | Count |
|---|---|
| Class C with a verified control ID | **3** (C1, C2, C3) |
| Class C with a partial ID | 1 (C4) |
| Class C needing lookup | 4 (C5 to C8, one of them blocked) |
| Class B needing lookup | 6 |
| **Total catalogue** | **14** |

**Two more changes are needed to reach 16**, and every `(unverified)` ID must be resolved
before data collection. Candidates not yet assessed: ASR rule blocking Office child processes,
block macros originating from the internet, AppLocker or WDAC enforcement, restrict anonymous
SAM enumeration, enforce SMB signing, enforce LDAP signing and channel binding, disable AutoPlay
and AutoRun.

**How to resolve an ID.** Search the setting name at
`https://www.stigviewer.com/stigs/microsoft-windows-11-security-technical-implementation-guide/`
for the DISA V-ID, or the registry value name in the CIS Windows 11 Enterprise Benchmark PDF for
the CIS number. **Record the benchmark version with the ID**, because numbering changes between
versions: Audit Process Creation is 17.3.1 in one version and 17.3.2 in another.

**Known limitation to state in the paper.** Every strong class C candidate is an authentication
control. That is a consequence of the pattern above, not a sampling accident, but it means the
findings generalise to authentication telemetry rather than to hardening in general.

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

# Open Questions

Things that are not verified and that change the plan if the answer is bad.
When one is answered, move it to "Answered" at the bottom with the date and the evidence.

Ranked by how much damage the wrong answer does.

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

## 1b. Can Module 2 see field-level telemetry loss?

**Status:** Open. Raised 2026-08-20.

**Why it matters:** Module 2 builds a frequency profile of event-type rates. Removing the
CommandLine field from 4688 does not change the 4688 rate, and changing 4104 content does not
change the 4104 rate. Both are invisible to chi-square on a rate that did not move.

**How to answer:** Redefine the unit of analysis as (event type, required field present) rather
than event type alone. Decide before the harness is written, because it changes the profile
schema and therefore every stored run.

**What a bad answer means:** Content-level and field-level hardening changes must be dropped
from the catalogue, and the study says so explicitly.

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

## 2. Does nested virtualization work for Credential Guard on this host?

**Status:** Untested.

**Why it matters:** T1 hardening change #8 (Enable Credential Guard) needs VBS inside the
guest, which needs nested virtualization (Virtualize AMD-V/RVI in VM settings). Unverified
on Zen 4 with Workstation 17.5.1.

**How to answer:** Enable the setting in WIN-EP-01, boot, try to turn on Credential Guard,
check `msinfo32` for VBS running.

**What a bad answer means:** Drop change #8 and substitute another from the catalogue.
Low damage. Test it in week 1 so the substitution is not rushed.

---

## 3. What is the real indexer heap and archive growth under `logall_json`?

**Status:** Estimated, not measured.

**Why it matters:** The 16 GB RAM and 200 GB disk figures for SIEM-01 are headroom based on
judgment, not measurement. If archives grow faster than expected, F: fills mid experiment.

**How to answer:** Measure during Phase 2 and Phase 3 of the runbook. Watch
`/var/ossec/logs/archives/` size over one full capture window.

**What a bad answer means:** Truncate more aggressively, or shrink the technique list.
The harness should already abort cleanly on low disk (runbook Phase 6).

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

## Answered

### Why were the VMware VMnet1/2/3 adapters in Error state? (answered 2026-08-31)

**Answer: fixed by Virtual Network Editor → Restore Defaults, then reconfiguring vmnet2 and
vmnet3.** The working theory (a lingering Hyper-V virtual switch conflicting with VMware's
adapters) was never confirmed as the exact cause, but the standard repair worked.

**Evidence, verified 2026-08-31 after the student ran the fix:**

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

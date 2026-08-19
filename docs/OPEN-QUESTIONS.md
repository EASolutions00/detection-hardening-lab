# Open Questions

Things that are not verified and that change the plan if the answer is bad.
When one is answered, move it to "Answered" at the bottom with the date and the evidence.

Ranked by how much damage the wrong answer does.

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

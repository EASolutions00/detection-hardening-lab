# STATUS

Current blockers and dates. This file changes often. CLAUDE.md does not.
Last updated: 2026-09-26, third update of the day (from git log)

Every item here must also exist in OPEN-QUESTIONS.md or DECISIONS.md. This file only
says which ones matter right now.

---

## Deadline

Data collection must start no later than end of September 2026.

## Most urgent: scope (OPEN-QUESTIONS item 25)

The 2026-09-22 date check has passed, and its condition is met: **no capture window has run.**
The capture harness (runbook Phase 6) does not exist, `data/runs/` is empty, and the lab VMs
were not powered on between 2026-09-11 and 2026-09-26. Evidence in WORKLOG 2026-09-26.
Item 25 recommends a scope cut in this case. **Scope is not cut. No decision is in
DECISIONS.md.** It is the student's decision. With no fallback topic, scope is the only lever
left.

## The spike

T1 is approved and final. There is **no fallback** (DECISIONS.md 2026-09-26). The spike
measuring run-to-run variance and real wall clock has still not run. See
[runbook Phase 7](RUNBOOK-homelab.md). If it shows T1 cannot finish in time, the answer is
scope (item 25), not a different topic.

## Live blocker: OPEN-QUESTIONS item 21

Raised 2026-09-12. Every class C hardening change is an authentication control, and there
is **no domain controller**. `DC-01` is Tier B and was never built.
**The archive count ran 2026-09-26 and confirmed it:** 4768, 4769 and 4776 are zero on every
date, and the lab has **never made a network logon** (0 of 2,892 logons). C2, C4, C6 and C7
have nothing to act on. **Now a decision for the student** among item 21's four ways out.
Building DC-01 alone is not enough: the test suite must also make network logons.

**As configured on 2026-09-26, no class C change is measurable on this lab.** Item 21 removes
C2, C4, C6 and C7; the Sysmon finding below removes C3 and C8; C1 and C5 need logons that are
rare or absent.

## Second: OPEN-QUESTIONS item 18

Six of the eight class C changes state a telemetry effect that is a *value change*, and the
analyser records which fields were **populated**, not what they contained. Only C4 and C6
are rate changes, and item 21 shows both of those need the missing domain. Value keying
cannot rescue an event that never fires.
The planned capture (`RunAsPPL`, then read `GrantedAccess`) **cannot run as written**, found
2026-09-26 before WIN-EP-01 was touched: the pinned Sysmon config records **no Event 10 at all**
(0 of 14,102 Sysmon events), and `RunAsPPL = 1` writes a UEFI firmware variable the registry
cannot undo. Two decisions first: add an `lsass.exe` rule to the Sysmon config or drop C3 and
C8, and use `RunAsPPL = 2` in the lab.

## Also open

- Item 1, the catalogue. Rebuilt on 2026-09-08, but it holds 14 of the 16 changes and several
  control IDs are still `(unverified)`. It still blocks data collection.
- Item 26, new 2026-09-26. The harness's own `vmrun` guest calls most likely write a batch
  logon each, inside every capture window: 1,641 of them on 2026-09-02. Count and record them.
- Item 27, new 2026-09-26. The host's VMware network adapters broke twice with no known
  cause. Repaired, but the harness must check the path to SIEM-01 before each run.
- Item 28, new 2026-09-26. Events written before the Wazuh agent starts never reach the
  archive, so boot-time checks such as Wininit event 12 must be made inside the guest.

## Lab state

- SIEM-01 was booted 2026-09-26 for the item 21 check and was still running when chat 27d2595d
  ended. Check with `vmrun -T ws list` rather than trusting this line.
- Host VMnet2 is at `10.20.10.1` again after a hand repair (item 27). Pre-flight now checks it.

## Recently settled (details in DECISIONS.md)

- 2026-09-26: T1 is the final thesis. There is no fallback topic.
- 2026-09-14: the title is the panel's wording verbatim (item 0).
- 2026-09-14: the system is a Python application with a graphical interface beside the
  SIEM, not a web application (item 17).

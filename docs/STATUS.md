# STATUS

Current blockers and dates. This file changes often. CLAUDE.md does not.
Last updated: 2026-09-26 (from git log)

Every item here must also exist in OPEN-QUESTIONS.md or DECISIONS.md. This file only
says which ones matter right now.

---

## Deadline

Data collection must start no later than end of September 2026.

## Most urgent: scope (OPEN-QUESTIONS item 25)

The 2026-09-22 date check has passed, and its condition is met: **no capture window has run.**
The capture harness (runbook Phase 6) does not exist, `data/runs/` is empty, and the lab VMs
have not been powered on since 2026-09-11. Evidence in WORKLOG 2026-09-26.
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
is **no domain controller**. `DC-01` is Tier B and was never built. One archive count
settles it, and it decides how many changes exist to measure.

## Second: OPEN-QUESTIONS item 18

Six of the eight class C changes state a telemetry effect that is a *value change*, and the
analyser records which fields were **populated**, not what they contained. Only C4 and C6
are rate changes, and item 21 shows both of those need the missing domain. Value keying
cannot rescue an event that never fires.
One lab capture settles item 18: set `RunAsPPL = 1` and read what `GrantedAccess` actually
holds afterwards.

## Also open

- Item 1, the catalogue. Rebuilt on 2026-09-08, but it holds 14 of the 16 changes and several
  control IDs are still `(unverified)`. It still blocks data collection.

## Recently settled (details in DECISIONS.md)

- 2026-09-26: T1 is the final thesis. There is no fallback topic.
- 2026-09-14: the title is the panel's wording verbatim (item 0).
- 2026-09-14: the system is a Python application with a graphical interface beside the
  SIEM, not a web application (item 17).

# Open Questions

Things that are not verified and that change the plan if the answer is bad.
When one is answered, move it to "Answered" at the bottom with the date and the evidence.

Ranked by how much damage the wrong answer does.

---

## 1. How many SigmaHQ rules carry a manual STP robustness annotation?

**Status:** Unverified. Blocking.

**Why it matters most:** T3 is your fallback if T1 fails its spike gate. T3's Objective 5
is validating automated scores against manually annotated rules using Cohen's kappa. If
the annotated subset is too small, kappa is not meaningful and Objective 5 fails.

Right now **both** your primary and your fallback have an unverified gate. That means you
currently have zero verified options. This is the single most important thing to fix.

**How to answer:** Clone `SigmaHQ/sigma`, pin the commit, and count rules carrying the
Summiting the Pyramid annotation field. Offline. Minutes, not days.

**What a bad answer means:** T3 is not safe either. You would need a different validation
strategy (for example, annotate a subset yourself and report inter-rater agreement with a
second annotator), or T2 becomes the real fallback.

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

Nothing yet.

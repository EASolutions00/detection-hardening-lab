# Open Questions

Things that are not verified and that change the plan if the answer is bad.
When one is answered, move it to "Answered" at the bottom with the date and the evidence.

Ranked by how much damage the wrong answer does.

---

## 0. What is the exact approved title wording?

**Status:** Open. Cheap to close. Raised 2026-09-02.

**Why it matters:** the title now appears in the public README, on every document from here,
and eventually on the cover page and the library record. It should be settled once, not drifted.

**The panel proposed:**
> Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential
> Analysis Algorithm

**The problem:** "Using Differential Analysis Algorithm" is missing an article. English needs
"a" or "the" before a singular countable noun.

**Two corrections, both keeping the panel's vocabulary:**
1. Reorder, adding no words: *Detecting Security Blind Spots Through Differential Analysis of
   Pre- and Post-Hardening Events*
2. Minimal, add one word: *...Using **a** Differential Analysis Algorithm*

**Currently in use:** the panel's exact wording, unmodified, in `README.md`. Deliberate. A
title the panel has not seen should not appear in a public repo.

**How to answer:** ask the adviser as a question about wording, not as a correction of the
panel. For example: "Sir/Ma'am, for the final title, should it read 'Using a Differential
Analysis Algorithm'? I want the wording correct before it goes on all my documents."

**What a bad answer means:** nothing bad. If they keep their original wording, use it
everywhere and stop revisiting it.

**Note for Chapter 3:** the approved title names a general method ("Differential Analysis
Algorithm") rather than a specific one. The specific algorithm must therefore be named and
defined explicitly in the methodology chapter, since the title no longer does it.

---

## 1. Which 16 hardening changes survive the corrected blind-spot definition?

**Status:** Open, but substantially advanced 2026-09-08. Raised 2026-08-20 while stress-testing
T1 against a formal definition of security hardening. This supersedes the older item 4 below in
priority, and absorbs it.

### Progress, 2026-09-08

The catalogue in `lab/blueprint.md` was rebuilt. The four anti-hardening items and the one with
no benchmark control are removed. Class B items are retained deliberately as **negative
controls**, where telemetry is lost but the correct impact score is near zero, which tests
whether the scorer can distinguish a lost capability from a lost detection.

**Three control IDs verified against DISA STIG Viewer and CIS benchmark sources:**

| Change | Control ID |
|---|---|
| Disable WDigest | DISA **V-253358** (Win11), V-220800 (Win10) |
| LAN Manager auth level, NTLMv2 only | DISA **V-253462** (Win11), V-220938 (Win10), CIS 2.3.11.7 |
| LSA Protection, LSASS as protected process | CIS Win11 **18.9.27.2**, Level 1 |

Restrict NTLM outgoing has a confirmed CIS number (2.3.11.13) and registry path, but its
Windows 11 DISA V-ID is not confirmed.

**The pattern that generates more candidates:** class C changes alter *how* something happens;
class B changes stop it happening at all. This is why nearly every class C candidate is an
authentication control, and it is a **stated limitation**: the findings generalise to
authentication telemetry, not to hardening in general.

**Still needed:** two more changes to reach 16, and every remaining `(unverified)` ID resolved
before data collection begins. Current total is 14.

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

## 21. Every class C change is an authentication control, and there is no domain controller

**Status:** Open. Raised 2026-09-12 during a documentation sweep. **Ranked above item 18 because
item 18's recommended fix does not reach this problem.**

**What was verified.**

```
F:\TeLoS Homelab   ->   SIEM-01, WIN-EP-01
```

Two virtual machines. `DC-01` appears only in the Tier B table at `lab/blueprint.md:52`, marked
"optional, add only if the spike says you have time". That same table says DC-01 is what
"enables identity telemetry (4768/4769/4776)". It was never built, and no entry in `DECISIONS.md`
or `WORKLOG.md` records building a domain.

**Why it matters. Apply both filters together and the measurable catalogue empties.**

`blueprint.md:295` explains why every class C candidate is an authentication control: class C
changes alter *how* something happens, and authentication survives the change while proceeding
differently. That pattern was recorded as a limitation on generality. **Nobody checked whether
this lab can produce authentication telemetry at all.**

| Change | Stated effect | What it needs | On this lab |
|---|---|---|---|
| C4 Restrict outgoing NTLM | "4776 reduced or removed" | Outgoing NTLM to a remote server | The only other machine is Ubuntu and shares nothing. Baseline already zero |
| C6 Cached credentials to 0 | "cached and offline logon events reduced" | Domain cached credentials. Its own note at `blueprint.md:310` reads "against the domain instead" | No domain, so nothing to reduce |
| C7 Disable RC4 for Kerberos | "4768 / 4769 fields change" | A key distribution centre | Those events cannot appear on a standalone machine |
| C2 NTLMv2 only | "4776 package name changes" | NTLM validation traffic | Local SAM validation only, rate unmeasured |

Item 18 leaves **C4 and C6** as the only two rate changes the analyser can see. Both are in the
table above. So the measurable class C set is currently **zero**, and the experiment would report
UNCHANGED across the whole catalogue. The study's conclusion would then be produced by a missing
virtual machine and a keying decision, not by anything true about Windows.

Item 1 already sets the bar: fewer than about 8 class C changes and the precision and recall
comparison is underpowered.

**Why item 18's fix does not help here.** Value-level keying works when the event still fires and
its contents change. It does nothing when the event never fires. **Zero to zero has no value to
key on.** This item is therefore answered first, and item 18 second.

### The cheap check, before building anything

Run against the Phase 3 archive already on SIEM-01. The pattern goes in a file and never on the
command line, per item 1b:

```bash
sudo -n /usr/local/sbin/telos-archive tail 1 2026-09-02      # read the exact field spelling
printf '"eventID":"4768"\n"eventID":"4769"\n"eventID":"4776"\n' > /tmp/telos-ids.txt
sudo -n /usr/local/sbin/telos-archive count /tmp/telos-ids.txt 2026-09-02
```

**Zero, or low single digits:** confirmed. **Hundreds:** 4776 fires locally often enough to
measure, and only C7 is dead.

### Four ways out, not equal

1. **Build DC-01.** Tier B already specifies 2 vCPU, 6 GB, 60 GB, and F: has room. Restores C2,
   C4, C6 and C7. With item 18 answered, the measurable set goes from 0 to about 7. **Cost:** one
   to two days, plus domain-joining WIN-EP-01 changes the baseline, so the golden snapshot must be
   re-taken and every version re-pinned. **This must happen before the golden snapshot, never
   after.**
2. **One Windows file server, no domain.** Gives the endpoint somewhere to send outgoing NTLM, so
   C4 becomes measurable. Half a day, buys one change, no Kerberos and no cached credentials.
3. **Re-scope to local-only controls.** **C3 (LSA Protection) is the strongest**, because Sysmon
   Event 10 access to `lsass.exe` is entirely local. C1 writes 4624 for local interactive logons.
   C5 works if RDP is driven from the host. All three are value changes, so this path needs item
   18 answered as option 1. Yields two or three positives, not eight.
4. **Report the restriction.** State in Chapter 3 that the laboratory was a standalone endpoint,
   that authentication telemetry requiring a domain was out of reach, and restrict every claim to
   what was measured.

**Recommendation: 1, conditional on the check**, with 3 as the fallback if there is no time left
to rebuild the golden image.

**What a bad answer means:** if the count comes back at zero and nothing changes, the experiment
runs to completion and reports that hardening does not create blind spots. That is the worst
available outcome, because it is a confident result with a cause nobody recorded.

**Blocks:** the size of the catalogue, the golden snapshot, and therefore the start of data
collection.

---

## 20. WIN-EP-01 does not audit process creation, and two headline claims depend on it

**Status:** Open. Raised 2026-09-11, measured while testing item 19.

**What was measured.** 200 process spawns across three test runs produced **zero** Security 4688
events. Confirmed directly rather than inferred from their absence:

```
auditpol /get /subcategory:"Process Creation"
  Detailed Tracking
    Process Creation                        No Auditing
    Process Termination                     No Auditing

ProcessCreationIncludeCmdLine_Enabled : NOT SET
```

For contrast, on the same machine: `Logon` is `Success and Failure`, `Special Logon` is `Success`,
`Audit Policy Change` is `Success`. So auditing is on in general. Process creation specifically is
not.

**Why it matters, and it is not a lab detail.**

1. **The canonical event key does not exist on this endpoint.** `PROMPT-new-chat.md` section 4 and
   `DECISIONS.md` 2026-09-04 both use `Security-4688[CommandLine,NewProcessName]` as *the* example
   of an event key. 4688 never fires here.
2. **Item 18's showcase case cannot be demonstrated.** Disabling
   `ProcessCreationIncludeCmdLine_Enabled` is described as the one change the composite key was
   designed around. That setting is already unset, and the event it would degrade is not being
   generated.
3. **Catalogue item 1 cannot be tested either.** "Disable Audit Process Creation" cannot be
   disabled, because it is already off.
4. **The machine is currently non-compliant with the CIS control that item 1 cites** (17.3.1 or
   17.3.2, which require Success auditing). The baseline is not the hardened starting point the
   catalogue assumes.

**What is carrying process creation instead.** Sysmon Event ID 1, which recorded all 100 spawns in
every test run. This is **item 1c arriving from an unexpected direction**: the redundant source is
not compensating for a hardening change, it is compensating for a baseline that was never
configured.

**How to answer:** decide whether the golden image should enable Process Creation auditing.
- If **yes**: `auditpol /set /subcategory:"Process Creation" /success:enable`, set
  `ProcessCreationIncludeCmdLine_Enabled = 1`, re-take the baseline, and re-verify before Phase 5.
  This also makes catalogue item 1 testable again and fixes the CIS non-compliance.
- If **no**: rewrite the canonical key example and item 18's showcase case around
  `Sysmon-1[CommandLine,Image]`, and state plainly that 4688 is not collected.

**What a bad answer means:** if this is left as it is and the documents are not changed, the
proposal's worked example describes an event the experiment will never observe, and a panelist who
asks to see one real 4688 event key from the data cannot be shown one.

---

## 19. Can the Unified Write Filter replace snapshot restore on a physical endpoint? (ANSWERED, see the Answered section)

**Status:** **Answered 2026-09-11. Yes. All six steps passed.** Evidence in the Answered section at
the bottom of this file and in WORKLOG 2026-09-11. The stress test below is kept rather than
deleted, because measurement confirmed four of its six risks, corrected one in our favour, and
widened another. Raised 2026-09-10.

**Why this exists.** `proposal-form-FINAL.md:240` states a precondition: target hosts must be
**virtual machines under a hypervisor supporting snapshots**. That is a large restriction and it
is stated in the preconditions table but **not** in Scope and Limitations, so a reader of the
limitations never learns of it. Snapshot restore is not a convenience. It is the control that
makes the before-and-after comparison valid, because it holds everything constant except the
hardening change.

**What UWF is.** Unified Write Filter, a Microsoft feature built into Windows. It intercepts
writes to a protected volume, redirects them to an overlay in RAM or on disk, and discards the
overlay on reboot. That is the same behaviour as Deep Freeze, shipped by Microsoft, driven by
`uwfmgr.exe`.

**Why it might already be available here.** Microsoft supports UWF on **Enterprise, Education and
IoT Enterprise**. `DECISIONS.md:326` records that WIN-EP-01 runs **Windows 11 Education**, build
`10.0.26100.9168`, chosen 2026-09-02 for an unrelated reason (Enterprise Evaluation expires after
90 days). **The edition decision may have handed this over for free.**

**Two jobs it would do, and only two:**

1. **Answer the deployment question.** It makes the method usable on a physical endpoint, so the
   precondition can be widened from "virtual machines under a hypervisor" to "the ability to
   return the host to a known state, by hypervisor snapshot, write filter, or disk image."
2. **Possibly unblock C8.** Credential Guard is blocked on nested virtualisation, item 2 below.
   **A physical machine with UWF could test C8 when a VM cannot.**

**It is not for the lab.** `vmrun` reverts in seconds. UWF costs a reboot per run plus a
servicing-mode sequence per change. Do not replace what already works.

### Six ways it breaks, from the stress test on 2026-09-10

1. **UWF reverts the hardening change too.** The experiment applies a registry setting. UWF sends
   registry writes to the overlay and discards them at reboot, so rebooting for a clean state also
   removes the thing being tested. **The documented fix is servicing mode**, in which UWF stops
   filtering for one boot cycle and changes made in that session become permanent. Cost: two extra
   reboots per hardening change, not per run. Getting this wrong measures nothing while looking
   normal.

2. **The overlay can fill mid-run, and nothing currently looks for it.** The overlay is a fixed
   size. Sysmon and the Windows event logs write constantly during a capture, and the Sysmon
   channel is already 64 MB (item 9). When the overlay fills, UWF writes **Event ID 2, "The UWF
   overlay size has reached CRITICAL level"**. **A run that fills the overlay is corrupt and would
   produce plausible numbers.** Any capture protocol using UWF must check for Event ID 2 and
   discard the run if it appears. This is the risk to worry about most, because a silently bad run
   producing believable output is the exact failure this whole thesis is about.

3. **Unsent events die at the reboot.** The Wazuh agent queues events it has not yet forwarded.
   That queue is on C:, therefore in the overlay, therefore discarded. The existing 120 s drain
   after the suite (`CLAUDE.md`, rule 5) mitigates it, but it is **a fourth silent loss channel**
   alongside items 8 and 13 and should be named as one.

4. **UWF may change the telemetry it is meant to preserve.** It is a filter driver in the storage
   stack. Whether a write redirected to the overlay still produces Sysmon Event 11, and whether
   the driver itself generates events, is unmeasured. **This does not threaten the comparison**,
   because UWF is on for both phases and cancels out. **It threatens external validity**, because
   the study claims its findings apply to machines that do not run UWF.

5. **Windows here is unactivated.** `DECISIONS.md:326` records Education, **unactivated**. Whether
   a DISM optional feature will enable on unactivated Windows is unverified. If it will not, this
   item closes immediately.

6. **The niche is narrow.** If a dedicated physical test machine is available, a VM is usually
   faster and the tooling already exists. UWF only wins where the hardware itself matters, which
   is why C8 is the case that justifies it.

### Test sequence, cheapest kill first

Run these in order in a working chat. **Stop at the first failure.** Each step can end the item.

| # | Check | Proves | If it fails |
|---|---|---|---|
| 1 | Does the feature exist on this build? `Get-WindowsOptionalFeature -Online \| Where-Object FeatureName -like "*Filter*"` in an **admin** PowerShell inside WIN-EP-01 | The capability is present. `State` may read `Disabled`, meaning present but off | Wrong edition or build. Item closes, fall back to disk imaging |
| 2 | Does it **enable** on unactivated Windows? | Activation is not a blocker | Item closes here. This is the likeliest silent killer |
| 3 | Enable, reboot, confirm a test file written before the reboot is gone after it | The basic revert works at all | Configuration problem, or the overlay is misconfigured |
| 4 | Servicing mode: apply one registry change, reboot, confirm it **survived** | Risk 1 is solvable, and hardening changes can be applied | The whole approach fails. There is no way to test a change UWF keeps deleting |
| 5 | Run one full capture under UWF, then check for **Event ID 2** | Risk 2 is under control at the current overlay size | Enlarge the overlay or move it to disk, then repeat |
| 6 | Capture the same stimulus with UWF on and with UWF off, and compare the profiles | Risk 4. Whether UWF changes what gets logged | Record it as a stated limitation on external validity, not as a failure |

**Widen the search string in step 1** to `*Filter*` rather than `*WriteFilter*`. If the feature
name is not what we expect, a narrow search returns nothing and would be read as "not available"
when it really means "wrong search string."

**What changes if it passes:** `proposal-form-FINAL.md:240` is rewritten to widen the
precondition, and the same statement is added to Scope and Limitations, where it is currently
missing. C8 gets a possible path that does not depend on nested virtualisation.

**What changes if it fails:** nothing breaks. The lab keeps using `vmrun`. The precondition stays
as written, and the VM requirement should still be added to Scope and Limitations, because it is
a real restriction that the limitations section does not currently state.

---

## 18. Six of the eight class C changes produce a telemetry effect the analyser cannot measure

**Status:** Open. Raised 2026-09-10. It is not a documentation problem. If the answer is bad, the
experiment produces UNCHANGED for most of the catalogue and the study reports that hardening does
not create blind spots, which would be an artifact of the key design and not a fact about the
world.

**Answer item 21 first.** This item was the most serious in the file until 2026-09-12, when item 21
found that the two changes it leaves measurable, C4 and C6, both need a domain controller that does
not exist. Value-level keying cannot rescue an event that never fires, so the order is 21 then 18.

**The test already exists in this project.** `lab/blueprint.md:349` removed Constrained Language
Mode with this reason:

> "it changes 4104 **content** while the rate and the field both stay populated. **The method
> measures presence, not meaning.**"

That test was applied once and never applied to the rest of the catalogue. Applying it now, using
each item's own stated telemetry effect from `blueprint.md:305-312`:

| # | Change | Stated telemetry effect | Shape | Analyser sees it? |
|---|---|---|---|---|
| C1 | Disable WDigest | "4624 logon-type distribution **shifts**" | `LogonType` value changes, field stays populated | **No** |
| C2 | NTLMv2 only | "4776 package name **changes**" | `PackageName` value changes | **No** |
| C3 | LSA Protection | "Sysmon 10 access **changes from granted to denied**" | `GrantedAccess` value changes | **No** |
| C4 | Restrict NTLM outgoing | "4776 **reduced or removed**" | Rate change | **Yes** |
| C5 | RDP NLA | "4624 / 4625 distribution **shifts**" | `LogonType` value changes | **No** |
| C6 | Cached credentials to 0 | "cached and offline logon events **reduced**" | Rate change | **Yes** |
| C7 | Disable RC4 for Kerberos | "4768 / 4769 ticket encryption **fields change**" | Value change, **and 4768/4769 are absent from `DEFAULT_TRACKED_FIELDS` entirely** | **No** |
| C8 | Credential Guard | "Sysmon 10 to lsass **changes**" | Value change. Also blocked on nested virtualisation, item 2 | **No** |

**Why the analyser cannot see a value change.** `eventkey.py:121` records which tracked fields were
*populated*. `is_populated()` returns true for any non-empty value, and `DECISIONS.md:48` states
explicitly that **numeric zero counts as populated, giving `GrantedAccess 0` as the example**. So
`GrantedAccess` going from `0x1410` to `0x0` leaves the key identical and the rate identical. The
analyser correctly reports UNCHANGED on the evidence it has.

**The one change that does work is deliberately excluded.** The composite key was designed around
disabling `ProcessCreationIncludeCmdLine_Enabled`, which empties CommandLine while 4688 keeps
firing. `blueprint.md:345` removed it because **CIS requires that setting enabled**, so it is
de-hardening, and `blueprint.md:351` keeps it only as a "capability demonstration ... clearly
labelled as not one of the evaluated changes."

So the method's showcase case is not in the experiment, and most of the experiment is not
measurable by the method.

**Three ways out, and they are not equal:**

1. **Add value-level keying for a small set of fields.** A field belongs in the key by *value*
   only when detection rules match on specific values, which is knowable from the Sigma rule set
   the same way tracked fields already are. Bucket the value rather than storing it raw, so the key
   space stays small. Cost: a key-format change, which `DECISIONS.md:64` says is cheap now and
   impossible after collection starts.
2. **Re-scope the study to rate-level blind spots only.** Keep C4 and C6, find more rate-change
   candidates, and state value-level degradation as an explicit limitation. Cost: the catalogue
   drops to two verified items and needs rebuilding a third time.
3. **Measure detection outcomes as well as telemetry.** A rule that stops firing is observable even
   when the telemetry rate does not move. Cost: this is a different thesis.

**Recommendation: option 1**, because the value change *is* the blind spot in every one of these
cases, and because the field-value information is already in the archived events. Option 2 discards
six verified control IDs to protect a design decision.

**How to answer:** run C3 in the lab, capture Sysmon Event 10 before and after `RunAsPPL = 1`, and
read what `GrantedAccess` actually contains afterwards. If the field is empty or the event stops,
presence keying already works and this item closes. If it carries a different number, option 1 is
required. **This is one capture and it settles the whole item.**

**Blocks:** the REVISED-to-FINAL diff, the proposal's Module 2 text, and the start of data
collection.

---

## 22. The stimulus is asserted identical and never verified

**Status:** Open. Raised 2026-09-12. **This one contaminates results rather than reducing them**,
so it ranks with item 18 rather than with the cleanup items.

**Where the claim is made.** `T1-PANEL-RESPONSE.md:513` answers panel question Q6 with three
mechanisms for making two runs comparable, and calls the run manifest "the single strongest answer
to the question":

> "**Machine-driven stimulus.** The same test IDs, in the same order, with the same delay between
> them, run by a scheduler. No human types anything during a capture."

`proposal-form-FINAL.md:205` states the same premise: "Identical activity comes from running the
same scripted adversary emulation suite in both windows, so any difference is attributable to the
configuration change rather than to different behaviour."

**Why it fails. The same commands are not the same behaviour.** If a hardening change makes an
atomic test fail, exit early, or take a different path, that test emits fewer events. The manifest
hashes still match, because the parameters did not change. The comparison proceeds. The analyser
sees a rate drop and reports LOST.

**The correct reading is "the attack did not happen", not "the evidence disappeared."** Those are
opposite findings and nothing in the current design can tell them apart.

This is the same distinction the class B and class C split exists to make, applied at run level
instead of at catalogue level. `blueprint.md:293` requires that "the technique that rule covers is
**still executable** after the change", which is a judgement made once when the catalogue is
written. It is never measured per run.

**It cuts both ways, and that is worth stating.** Item 21's class B changes are kept as negative
controls precisely because they remove the attack along with the telemetry. If a class C change
partly blocks its own atomic test, that change quietly behaves like a class B one and the labelling
is wrong for that run only.

**How to answer:** make stimulus success part of the run record, not an assumption.

1. Record **per-atomic exit status and duration** from `Invoke-AtomicTest` in
   `run_manifest.json`. The runner already returns both.
2. Record a **stimulus fingerprint**, for example the count of process creations between the start
   and end fences, or the count of Sysmon Event 1 records carrying the run id.
3. Measure the fingerprint's own spread across the 5 control runs, where nothing changed. That
   spread is the tolerance.
4. **Void the run** when the fingerprint moves by more than that tolerance, and do not analyse it.
   A voided run is recorded with its reason, not silently dropped.

**Cheap now, impossible later.** The exit statuses exist only while the run is happening. A run
archived without them cannot be checked afterwards, so this must be in the harness from the first
version.

**What a bad answer means:** without it, every LOST finding carries an unanswerable question at the
defense. A panelist asks "how do you know the attack still ran?" and the honest answer is "the same
commands were issued", which is not the same claim.

**Blocks:** the Phase 6 harness design, and the manifest field list in runbook Phase 4.

---

## 17. Is the system a server-side web application? Nobody ever decided.

**Status:** Open. Raised 2026-09-09 by an automated scan of every thesis document. Ranked at the
top because **it is already written as settled fact in the document that will be submitted**, and
it is the only item here where the record was never made at all.

**What three live documents assert:**

| File | Line | Text |
|---|---|---|
| `proposal-form-FINAL.md` | 217 | "The system is a **server-side web application**." |
| `T1-PANEL-RESPONSE.md` | 174 | "It is a **server-side web application**." |
| `T1-REVISIONS-LIST.md` | 111 | "The system is a server-side web application." |

**What the record says:** nothing. A search of `DECISIONS.md` and this file for "web
application", "web-based", "web interface" and "System Type" returns only Wazuh deployment-mode
entries. **There is no decision.**

**How it became fact.** It was marked ASSUMPTION four times in `T1-PROPOSAL-REVISION.md`,
confirmation was asked for twice and never given, it was never entered here, and it was then
written into a submission document without the marking. This is the exact failure that rule 3 in
`CLAUDE.md` exists to prevent: *a draft marked ASSUMPTION is not a decision.*

**Why it matters more than wording.** It answers panel questions Q1 and Q8 directly, and it sets
scope. A web application implies a front end, sessions, and a deployment story, none of which
exist in `src/telos/`. What exists is a Python package with a command line. `proposal-form-FINAL.md`
lines 221 to 223 already say the analytical core "also runs from the command line without the web
interface" and that the headless mode produces every measurement in the study. **So the document
commits to building a web application whose only stated role is to not be used for the results.**

**How to answer:** ask the adviser, in the same message as the title wording. "Sir/Ma'am, does the
system need a web or graphical interface, or is a command-line tool with generated reports
acceptable for this scope?"

**What a bad answer means:** if a web interface is required, it is a second system to build,
document and defend, on top of a lab and an analyser, before end of September. If it is not
required, three documents need one paragraph changed each and the scope shrinks.

**Do not run the REVISED-to-FINAL diff until this is answered.** The claim appears in both files,
so the answer changes the diff.

---

## 15. Which submission documents still carry the superseded event key?

**Status:** Open. Raised 2026-09-09 while checking the activity diagram. Ranked here because a
submitted document that contradicts another submitted document is a defense problem, not a
tidiness problem.

**What happened.** The unit of analysis changed on 2026-09-04 to (event type + populated tracked
fields). Anything written before that date describes a system that cannot see a field-level
blind spot, which is the case the thesis is named after.

**Checked and clean:**

| File | State |
|---|---|
| `src/telos/eventkey.py`, `differential.py` | Correct. This is the source of truth. |
| `proposal-form-FINAL.md` | Correct. Line 61 "event keys", line 350 describes populated fields. |
| `T1_Activity_Diagram_Revised_Sheet1/2.svg` | **Fixed 2026-09-09**, regenerated from a script. |
| `T1_Figure_Analysis_Pipeline.svg` | **Fixed 2026-09-09.** Had "event-type key"; had `λ₀(e) = count / window` where `differential.py:115` computes `a / n1`, count per **run**; omitted the global gate entirely; omitted the 30-event INCONCLUSIVE rule and the field-loss pairing. |
| `T1_Figure_Noise_Floor.svg` | **Fixed 2026-09-09.** Had "WinSec 4104", a log channel that does not exist for that event; explained INCONCLUSIVE by band width instead of the 30-event minimum; labelled rows by event type; drew the LOST marker above zero. |

**All four T1 figures are now generated** by scripts in `thesis/T1/figures/`, sharing
`svgkit.py`. A design change is a string edit and a re-run.

**Checked and stale:**

| File | Problem |
|---|---|
| `T1_Detection of Hardening-Induced Blind Spots REVISED.docx` | Embeds `T1_Activity_Diagram_Swimlane.png` from **2026-08-15**, not the revised sheets. Confirmed by size match: `word/media/image1.png` is 326,941 bytes. **This is the remaining piece of this item.** |
| `thesis/T1/proposal-form-REVISED.md` | Line 416, "the key is the triple of telemetry source, numeric event...". Superseded by FINAL, so this only matters if REVISED is ever reused. |

**Not yet checked:** `T1-PANEL-RESPONSE.md`, `T1-REVISION-DRAFT.md`, `T1-REVISIONS-LIST.md`
Revision 14 (known separately to say field **values** where the code uses field **presence**).

**Note on the PNGs.** The four PNG renders in the documents folder were made from the stale SVGs
and are now renamed `*.SUPERSEDED-2026-08-28.png`, so the wrong picture cannot be inserted by
accident. Word inserts SVG directly and keeps it as vector, so no PNG is needed.

**How to answer:** grep each for "event type", "event-type key", and "field value", and compare
against `eventkey.py`. Not against another document.

**What a bad answer means:** every stale file found before submission costs minutes. One found by
a panelist during the defense costs the credibility of every other figure in the document.

---

## 16. Should `global_gate()` distinguish "no change" from "could not test"?

**Status:** Open. Raised 2026-09-09. Lower damage than the items above, but it changes a reported
result, so it is a real decision and not a cleanup.

**Read with item 23**, which is the other half of the same function: this item is about the gate's
failure modes being conflated, item 23 is about its success being unearned. Fix them together, in
one change to `global_gate()`, rather than touching that function twice.

**The problem.** `global_gate()` returns not-passed for three different situations:

| Line | Situation | What it means |
|---|---|---|
| `differential.py:74` | Fewer than two informative keys | Could not test |
| `differential.py:84` | Both phases emitted nothing | Could not test, and something is badly wrong |
| `differential.py:91` | Chi-square could not compute | Could not test |

All three produce `gate_passed=False`, which the activity diagram renders as **"Record no
significant change"**. Only the ordinary case where chi-square runs and returns `p >= alpha` is
actually "no significant change".

The code's own comment at `differential.py:93` says the run should be recorded as **inconclusive
at the profile level**, but `AnalysisResult` carries no field that can say so.

**Why it matters.** "This hardening change was safe" and "this run could not be tested" are
opposite claims. Reporting a dead agent as a clean result is the same class of error the whole
thesis is about: absence of signal read as absence of problem.

**Why the diagram was not changed to match.** Relabelling the box would make the figure claim a
distinction the code does not make. That is the exact failure being fixed elsewhere. Code first,
figure second.

**How to answer:** add a profile-level outcome to `AnalysisResult` with three values (CHANGED,
UNCHANGED, NOT_TESTABLE), have `global_gate()` return which, add tests for all three, then
regenerate the figure with `make_activity_diagram.py`.

**What a bad answer means:** if this is left as is, every "no significant change" in the results
chapter needs a footnote explaining that it may also mean the run failed. That is a worse
sentence to defend than the fix is to write.

---

## 23. `global_gate()` ignores the alpha it is given, and is the only stage with no noise model

**Status:** Open. Raised 2026-09-12. Two defects in one function. The first is a plain bug, the
second is a design question. Ranked here with item 16, which is about the same function.

### Defect one: the alpha parameter does not reach the gate

`analyse()` takes `alpha` at `differential.py:253` and passes it to `classify()` at line 284. But
line 273 calls the gate with no alpha:

```python
passed, gate_p, gate_stat = global_gate(pre, post, keys)
```

and its signature at line 56 accepts none, so line 96 compares against the module constant:

```python
def global_gate(pre: Phase, post: Phase, keys: list[str]) -> tuple[bool, float, float]:
    ...
    return bool(p < ALPHA), float(p), float(chi2)
```

So `analyse(alpha=0.01)` moves every per-key test and **silently leaves the gate at 0.05**.

**Why it matters beyond tidiness.** `proposal-form-FINAL.md:283` promises that the thresholds are
"configurable parameters of the system, not constants of the method, and the sensitivity of
precision and recall to each is examined during evaluation". A sensitivity sweep on alpha would
produce a curve in which one stage of the pipeline never moved, and nothing in the output would
say so.

**Fix:** add `alpha: float = ALPHA` to `global_gate()`, pass it from `analyse()`, and add a test
that a gate which passes at 0.05 does not pass at a small enough alpha.

### Defect two: the gate has no noise model, unlike every other stage

The per-key test uses the dispersion and the coefficient of variation measured from the control
runs. **The gate uses neither.** It is the only stage in the pipeline that ignores the measured
variance floor, which is the project's central idea.

**Why that may break it.** Chi-square power grows with sample size. The demo measures a CoV of
0.33 to 1.55 percent, so ordinary run-to-run variation shifts the profile proportions by a small
but non-zero amount. With thousands of events per phase, a shift that size can reach `p < 0.05`.
**A gate that passes on noise is not a gate**, and everything downstream is conditioned on it.

Item 16 is the other half of the same problem: the gate's *failure* modes are conflated. This item
is about its *success* being unearned.

**How to answer, and it costs no new infrastructure.** Run `global_gate()` on control run 1 versus
control run 2, where nothing changed, and on every other control pair. Five control runs give ten
pairs.

- **The gate does not pass on any pair:** it is sound at these counts. Record the result and close
  this half.
- **The gate passes on some pair:** it is measuring noise. Then either calibrate its threshold from
  the control pairs instead of fixing alpha at 0.05, or report an effect size such as Cramér's V
  beside the p value and state plainly that the gate answers only "did anything change at all".

**This is a Phase 7 spike deliverable**, not separate work. The control runs are already required
for Q1.

**What a bad answer means:** if the gate passes on noise and this is never checked, the global test
is presented as a safeguard that does no filtering. A panelist who knows how chi-square behaves at
large N will ask, and "we did not test it" is a bad answer when the control data needed to test it
was collected anyway.

---

## 1b-remainder. Harness counting rules that survive the schema decision

**Status:** Open, but no longer a schema question. The schema itself was decided 2026-09-04,
see Answered. What remains are two counting rules the Phase 6 harness must obey.

**Measured evidence, 2026-09-02,** from the first live archive on SIEM-01.

1. **One emitted event produces exactly one line in `archives.json`.** There is no duplicate
   collection to de-duplicate. Verified with a `logger` marker read from a root shell.
2. **A search can create the thing it is searching for.** `sudo grep -c "MARKER" archives.json`
   returned `2`, then `3`, from a single `logger` event. `sudo` writes every command line to
   journald, Wazuh collects journald, so each search added a new event containing the marker.
   Reading from a `sudo -i` root shell, where individual commands are not logged by `sudo`,
   returned the correct `1`.

**Harness rule that follows:** the Phase 6 harness must never place a marker, technique name, or
search pattern on a command line it runs under `sudo` on a monitored host. Read the archive from
a root shell, or pass the pattern from a file with `grep -f` so only the filename appears in the
logged command. Breaking this rule does not error. It silently inflates counts.

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

## 1d. Does journald rate limiting silently drop events during a capture?

**Status:** **Answered 2026-09-03. No, not as the lab is currently scoped.** Measured, and the
premise of the question turned out to be partly wrong. Resolution at the end of this item.

**Why it matters:** SIEM-01 collects operating system events from **`journald` only**. Verified
from `ossec.conf`, which lists exactly three sources:

| Source | Format |
|---|---|
| `journald` | `journald` |
| `/var/ossec/logs/active-responses.log` | `syslog` |
| `/var/log/dpkg.log` | `syslog` |

There is no `/var/log/syslog` and no `/var/log/auth.log`. Older Wazuh guidance assumes those
files, and it does not apply here.

**journald discards messages by design when a service exceeds its rate limit.** It writes a short
"Suppressed N messages" notice and drops the rest. Dropped messages never reach Wazuh, never
reach `archives.json`, and never appear in any result. That is telemetry loss caused by
configuration, which is the exact subject of this thesis, sitting **inside the measurement
pipeline itself**.

If a Phase 6 run generates events faster than the limit, the run loses events for a reason that
has nothing to do with the hardening change being tested. The loss would look exactly like a
finding.

**How to answer:** read the effective `RateLimitIntervalSec` and `RateLimitBurst` on SIEM-01 and
on WIN-EP-01's forwarder path, then generate a burst at the rate a real Atomic Red Team suite
produces and check `journalctl` for suppression notices. Either raise or disable the limit and
record it as a pinned baseline value, or keep it and prove the run rate stays under it.

**What a bad answer means:** if the limit is being hit at realistic run rates and is not
addressed, every T1 result is contaminated by an unmeasured, uncontrolled loss channel. This is
a threat to validity, not a performance issue.

### Resolution, 2026-09-03

**The premise was partly wrong, and correcting it is most of the answer.** This item assumed the
endpoint's telemetry travels through journald on SIEM-01. It does not. The Phase 3 evidence in
`archives.json` shows how WIN-EP-01's events actually arrive:

```
"decoder":{"name":"windows_eventchannel"}   ...   "location":"EventChannel"
```

They come over port 1514 into the manager's own queue. **journald on SIEM-01 carries only
SIEM-01's own operating system events**, which a capture run barely touches. The original worry,
that a busy run would overrun journald and lose endpoint data, cannot happen by that path.

**Measured on SIEM-01, 2026-09-03:**

| Item | Value |
|---|---|
| `RateLimitIntervalSec` | **30s** (default, not overridden anywhere) |
| `RateLimitBurst` | **10000** (default, not overridden anywhere) |
| Meaning | more than 10,000 messages from **one service** within 30 s and the rest are dropped |
| **Suppression notices ever recorded on this machine** | **0** |
| Journal storage | persistent (`/var/log/journal` exists), 79.5 MB |
| Only non-default journald setting | `ForwardToSyslog=yes` |

Every journald setting is at its built-in default. The limit has **never** been reached, across
every boot in the journal.

**A separate finding from the same output.** `rsyslog` is installed and active, and
`ForwardToSyslog=yes` means **every journald message is written twice**, once to the journal and
once to `/var/log/syslog`, which is already 1.77 MB. Wazuh does **not** read `/var/log/syslog`,
so this is duplicate disk writes, not duplicate collection. Minor, but it is disk churn inside
every capture window and it belongs in the baseline description.

**What is left of this item, and when it comes back.** If a Linux endpoint is ever added
(`LNX-EP-01` in `lab/blueprint.md` Tier B), its `auditd` and OS events **would** pass through
journald on that machine, and this question becomes live again for that host. It is answered for
the current Tier A lab only.

**Related, and still open:** the loss-channel worry is real, just in different places. See items
9 (Sysmon channel, 64 MB circular) and 13 (agent buffer, 500 events/s).

---

## 2. Does nested virtualization work for Credential Guard on this host?

**Status:** Untested.

**Why it matters:** T1 hardening change #8 (Enable Credential Guard) needs VBS inside the
guest, which needs nested virtualization (Virtualize AMD-V/RVI in VM settings). Unverified
on Zen 4 with Workstation 17.5.1.

**A second path exists, added 2026-09-10.** If nested virtualization does not work, C8 could be
tested on a **physical** machine instead, using the Unified Write Filter to return it to a known
state rather than a hypervisor snapshot. See **item 19**. That path has its own six risks and its
own test sequence, so it is not a free substitute, but it means a nested-virtualization failure no
longer forces C8 to be dropped.

**How to answer:** Enable the setting in WIN-EP-01, boot, try to turn on Credential Guard,
check `msinfo32` for VBS running.

**What a bad answer means:** Drop change #8 and substitute another from the catalogue.
Low damage. Test it in week 1 so the substitution is not rushed.

**Baseline established 2026-09-02 during Phase 3.** WIN-EP-01 was deliberately built with
`vhv.enable = "FALSE"`, so the guest has no virtualization extensions and **VBS cannot start on
its own**. This matters because Windows 11 enables VBS by default on capable hardware, and if it
were already running in the golden image, change #8 would have nothing left to switch on and
would measure nothing.

Confirmed from two independent sources on the built machine:

```
Win32_DeviceGuard : VirtualizationBasedSecurityStatus = 0, SecurityServicesRunning = 0
systeminfo        : Virtualization-based security: Status: Not enabled
Confirm-SecureBootUEFI : True
Get-Tpm           : TpmPresent = False
```

Secure Boot is on and there is no TPM, which is the intended configuration (see DECISIONS.md,
same date). TPM 2.0 is recommended rather than required for VBS `(unverified)`, so the test is
still worth running.

**The test is now a two-step change, not one.** Set `vhv.enable = "TRUE"` with the VM powered
off, boot, and **first check whether Windows has switched VBS on by itself**. If it has, the
golden snapshot has to be re-examined, because the baseline would no longer be "VBS off".

---

## 3. What is the real indexer heap and archive growth under `logall_json`?

**Status:** Partly measured 2026-09-02. Idle baseline now known. Load figure still unmeasured.

**Why it matters:** The 16 GB RAM and 200 GB disk figures for SIEM-01 are headroom based on
judgment, not measurement. If archives grow faster than expected, F: fills mid experiment.

**Measured on SIEM-01, 2026-09-02, idle, no agents connected:**

| Item | Value |
|---|---|
| `archives.json` growth | 32,604 to 39,367 bytes in 60 seconds, about **9.7 MB per day** |
| Archives on disk | 88 KB |
| Indexer data (`/var/lib/wazuh-indexer`) | 3.4 MB |
| Root filesystem after the full build | 195 GB total, 27 GB used, **159 GB free** |
| Largest single consumer | `/var/ossec/queue/vd`, **12 GB**, the CVE feed. Module now disabled, data kept. |

**What this changes:** the disk is not the near-term risk it was assumed to be. At the idle rate
archives take decades to matter, and the 200 GB allocation is now 195 GB usable rather than the
97 GB the installer actually gave it (see DECISIONS.md, LVM extend).

**Measured again 2026-09-02, Phase 3, with WIN-EP-01 connected:**

| Condition | Measurement | Rate |
|---|---|---|
| No agents, idle (Phase 2) | 32,604 to 39,367 bytes in 60 s | **9.7 MB/day** |
| One agent, idle, agent scan modules **enabled** | 48,358,184 to 48,433,173 bytes in 180.4 s | **34.3 MB/day** |
| **One agent, idle, agent scan modules DISABLED** | 49,615,051 to 49,654,191 bytes in 180.4 s | **17.9 MB/day** |
| One Phase 3 capture window (2 fences, 1 atomic test, 120 s drain, 1 report script) | 47,305,482 to 48,259,184 bytes, about **954 KB** | not a rate, a per-activity cost |

**Disabling the agent's own scan modules cut idle volume roughly in half**, from 34.3 to 17.9
MB/day, which is about two thirds of everything the agent was contributing over the no-agent
baseline. See item 8.

`archives.json` was already **47.3 MB** when Phase 3 began, from roughly one day of running.

**Read the third row carefully. It is not a daily rate.** It spans a burst of activity, and
extrapolating it to a day would give about 500 MB/day, which is wrong. The steady figure with an
agent connected is the second row.

**What this changes:** one connected, idle agent costs about 3.5 times the no-agent baseline.
With 162 GB free, the idle rate alone would take years to matter. The risk is the burst rate
multiplied by 101 runs, and that still cannot be known until a full capture window with a real
technique list exists.

**Still unmeasured, and this is the part that counts:** growth during a full Atomic Red Team
suite, not one discovery test. That number cannot be known until a real Phase 6 run exists.

**How to answer the rest:** measure `archives.json` growth across one full capture window in
Phase 6, then set retention from that number. Retention was deliberately **not** set in Phase 2
for this reason. See DECISIONS.md, same date.

**What a bad answer means:** Truncate more aggressively, or shrink the technique list.
The harness must abort cleanly on low disk (runbook Phase 6). That check is now load-carrying,
because it is the only thing standing between a burst and a filled disk.

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

## 5. Is snapd still refreshing packages on its own schedule?

**Status:** **Answered 2026-09-03.** Four units disabled. One failed lookup per SIEM-01 boot
remains, deliberately, and a protocol rule covers it. Resolution at the end.

**Why it matters:** `snapd` was found installed on SIEM-01 (version `2.76`, upgraded to
`2.76.3` in the Phase 2 patch run). snapd refreshes its snaps automatically, several times a
day, without asking. That is the same problem as the apt timers, which were disabled on
2026-09-02, and the same problem as the Wazuh vulnerability feed, which was disabled the same
day. This one was **not** dealt with.

All featured snaps were skipped at install, but snapd itself and its base snaps are present and
its refresh timer is live.

**How to answer:** check `systemctl list-timers | grep snap` and `snap refresh --time` on
SIEM-01. Then either hold refreshes indefinitely, or remove snapd entirely if nothing depends on
it. Record whichever is chosen in DECISIONS.md with the reversal command.

**What a bad answer means:** a snap refresh inside a capture window changes packages on the
machine mid-run and generates its own events. Same failure mode as an unattended apt upgrade:
silent, scheduled, and it invalidates every run collected before it.

### Measured 2026-09-03. The problem is real but it is not the one written above.

```
snap list           : empty, NO snaps are installed at all
snap refresh --time : last: n/a   next: n/a
snapd version       : 2.76.3+ubuntu24.04
```

**Nothing can refresh, because nothing is installed.** The feared "snap refresh mid-run" cannot
happen. But the journal shows what snapd is actually doing:

```
Sep 03 08:02:30 siem-01 snapd[5068]: state ensure error:
  Get "https://api.snapcraft.io/api/v1/snaps/sections": net/http: request canceled while
  waiting for connection (Client.Timeout exceeded while awaiting headers)
```

**snapd contacts Canonical on its own loop even with zero snaps installed, and it is already
failing.** After Phase 5 disconnects NAT it will fail **every time, forever**, and each failure
is a journald message that Wazuh collects into `archives.json`. That is the same failure mode as
the Wazuh vulnerability feed disabled in Phase 2: an internet-dependent service on a deliberately
isolated machine, logging on a timer.

`snapd.snap-repair.timer` is also `enabled`, and it contacts Canonical independently of installed
snaps.

**Removing snapd is the wrong fix.** `apt-cache rdepends --installed snapd` returns
`ubuntu-server-minimal`, `ubuntu-server`, `apparmor` and `command-not-found`. Removing the package
would drag out the server metapackages.

**How to close it: stop the daemon, keep the package.** Disable and stop the units that reach the
network, leave `snapd.apparmor.service` and `snapd.seeded.service` alone so boot ordering and
AppArmor are untouched:

```bash
sudo systemctl disable --now snapd.service snapd.socket snapd.snap-repair.timer snapd.autoimport.service
```

Then reboot and confirm the machine comes up, Wazuh is active, and no further `api.snapcraft.io`
lines appear. **The `phase3-complete-2026-09-02` snapshot makes this safe to attempt**: if boot
breaks, revert.

**This cannot be done by the harness account.** The sudoers rule installed on 2026-09-02 grants
`/usr/local/sbin/telos-archive` and nothing else, so it is a student step by design.

### Resolution, 2026-09-03. Fixed as far as it is worth fixing.

The four units were disabled and the machine rebooted. State afterwards:

```
snapd.service             enabled=disabled   active=inactive
snapd.socket              enabled=disabled   active=ACTIVE
snapd.snap-repair.timer   enabled=disabled   active=inactive
snapd.autoimport.service  enabled=disabled   active=inactive
snapd.seeded.service      enabled=enabled    active=active
```

**The socket is still active, and the exclusion list was the reason.** `snapd.seeded.service` was
deliberately left alone to protect boot ordering, and it **requires** `snapd.socket`, which
socket-activates `snapd.service` anyway:

```
systemctl list-dependencies --reverse snapd.socket
  snapd.socket
  ├─snapd.seeded.service
  └─snapd.service
```

**What actually happens now, per boot:**

```
08:40:32  state ensure error: Get "https://api.snapcraft.io/..."  timeout
08:41:02  snapd.service: Deactivated successfully.
snapcraft.io contacts this boot : 1
```

One failed lookup, then snapd shuts itself down. **The repeating timer behaviour is gone**, which
was the actual problem. What is left is a single event at boot.

**Deliberately stopping here, and this is a judgement call rather than a fix.** Removing the last
one means disabling `snapd.seeded.service`, which sits in the boot path on a machine that holds
every piece of evidence the thesis has. Risking a boot failure on the SIEM to remove one log line
that occurs outside every capture window is a bad trade.

**It is outside every capture window because of a protocol rule that this makes explicit:**

> **SIEM-01 must not be rebooted during a capture campaign.** Only WIN-EP-01 is reverted and
> booted per run. If SIEM-01 ever has to restart mid-campaign, the runs on either side of that
> restart carry one extra `snapcraft.io` failure event, and that must be noted in the run
> manifest rather than discovered later.

Added to `lab/blueprint.md` and runbook Phase 6.

**If it ever needs closing completely:** `sudo systemctl disable --now snapd.seeded.service`, then
reboot and confirm the machine comes up and Wazuh is active. The `timesync-off-2026-09-03`
snapshot makes that recoverable.

---

## 6. How do SIEM-01 and WIN-EP-01 keep their clocks together after Phase 5?

**Status:** **Answered and fixed 2026-09-03.** The six switches are set on both machines, and the
drift half is answered by not depending on the manager's clock at all. Resolution at the end.

**Why it matters:** SIEM-01 currently reports `NTP service: active` and
`System clock synchronized: yes`, synchronising over the internet through the NAT adapter. Phase
5 disconnects that adapter. After that, `systemd-timesyncd` has no reachable time server and the
clock is free to drift, as is WIN-EP-01's.

Runbook rule 5 (fence capture windows in telemetry, not host clock) protects the **window**. It
does not protect **cross-machine correlation**, which is a different thing. Matching an endpoint
event to a manager event depends on the two clocks agreeing.

**How to answer:** pick one of three.
1. Accept drift and correlate only within a single host. Cheapest. Restricts the analysis.
2. Run a time source on the Windows host, reachable at `10.20.10.1`. Keeps both guests aligned
   without giving them internet.
3. Re-enable VMware Tools time sync (`tools.syncTime` is currently `FALSE` in `SIEM-01.vmx`).
   **Note the catch:** a clock step is itself a logged event and could land inside a capture
   window, which is probably why it was disabled in the first place.

**Progress 2026-09-02.** WIN-EP-01 was set to `UTC`, matching SIEM-01's `Etc/UTC`, so the two
machines at least share a reference frame. `tools.syncTime = "FALSE"` is set in both `.vmx`
files.

**A gap found the same day, and it is the sharp part of this item.** `tools.syncTime = "FALSE"`
stops the **periodic** clock sync. It does **not** stop VMware Tools from stepping the guest clock
on snapshot revert, on resume, or at Tools startup. Those are separate switches, and **neither
`.vmx` sets any of them**:

```
time.synchronize.restore
time.synchronize.resume.disk
time.synchronize.tools.startup
time.synchronize.continue
```

**Why this is worse than ordinary drift.** Phase 6 reverts a snapshot before **every single
run**. If VMware Tools steps the clock on each revert, a time-change event lands at the very
start of every capture window, in all 101 runs. That is a scheduled, uncontrolled event injected
into the exact window being measured, and it would be present in the pre-change and post-change
runs alike, so it would not cancel out cleanly either.

**How to answer this part:** set the four switches to `FALSE` in both `.vmx` files with the VMs
powered off, then revert a snapshot and check whether the guest clock moved and whether a
time-change event was written. Do this before the Phase 5 golden snapshot.

**What a bad answer means:** if drift is ignored and cross-host correlation is needed later, the
timestamps cannot be repaired after the fact. Decide before Phase 6, not after.

### Resolution, 2026-09-03

**Part one, the switches. Done.** All six are now `FALSE` in **both** `.vmx` files, alongside
`tools.syncTime`. Verified to survive a full power cycle, which matters because VMware rewrites
the `.vmx` on every power off:

```
tools.syncTime                  = "FALSE"
time.synchronize.continue       = "FALSE"
time.synchronize.restore        = "FALSE"
time.synchronize.resume.disk    = "FALSE"
time.synchronize.resume.host    = "FALSE"
time.synchronize.shrink         = "FALSE"
time.synchronize.tools.startup  = "FALSE"
```

VMware Tools can no longer step either guest's clock in any situation. Backups of both files were
kept as `<name>.vmx.telos-20260903T081807Z.bak`.

**Part two, the drift. The three options offered above were the wrong question.** Look at what an
archive line actually contains, from the Phase 3 evidence:

```
endpoint clock : "systemTime":"2026-09-02T13:30:38.7096614Z"
manager clock  : "timestamp":"2026-09-02T13:30:40.599+0000"
```

**Both clocks are in every single event.** So the fix is not to synchronise the two machines, it
is to **stop depending on the manager's clock**.

**Harness rule, to be enforced in Phase 6:** every capture window boundary and every measurement
uses the **endpoint's own** `systemTime` or `utcTime` from inside the event. The manager's
`timestamp` field is used for **nothing** except measuring pipeline latency, and that figure is
only meaningful while the clocks are known to agree. Under this rule SIEM-01's drift cannot reach
the results, because it never enters them.

This is runbook rule 5 applied properly: fence in the telemetry, not on a host clock.

**Option 2 is therefore rejected**, not deferred. Running a time server on the Windows host at
`10.20.10.1` would put a live network service on a segment the thesis describes as isolated, to
solve a problem the rule above removes.

**One thing that must be decided in Phase 5, and it is currently only an implication.** A **cold**
snapshot, taken powered off, boots the guest fresh and VMware sets the virtual clock from the host
at power-on, so the clock is right without Tools touching it. A **live** snapshot, taken with
memory, restores a stale clock. The blueprint's run protocol reverts then starts, which implies
cold, but nothing says so. **The golden snapshot must be taken cold, and that has to be written
into Phase 5 as a requirement rather than left to inference.**

---

## 14. Wazuh rotates `archives.json` daily, by hard link, and the run protocol assumes it does not

**Status:** **Answered 2026-09-03. The run protocol changed: export by date, never truncate.**
Resolution at the end of this item.

**Why it matters:** `lab/blueprint.md` run-protocol step 10 says "rotate `archives.json`, gzip,
pull to `E:\runs\<run_id>\`, then **truncate on the SIEM**". That assumes one growing file per
run. Wazuh does not work that way.

**Observed.** `archives.json` was 49,654,191 bytes on 2026-09-02 and 5,166,709 bytes the next
morning. It did not shrink, it was rotated at the day boundary:

```
drwxr-x--- 3 wazuh wazuh    4096 Sep  1 19:36 2026
-rw-r----- 2 wazuh wazuh 5272919 Sep  3 08:19 archives.json
-rw-r----- 2 wazuh wazuh       0 Sep  3 07:59 archives.log
```

**Note the link count of 2 on `archives.json`.** It is a **hard link** to today's file inside the
dated tree, almost certainly `2026/Sep/ossec-archive-03.json`. Both names point at the same inode.

**Two consequences, and the second one destroys data:**

1. **A run crossing midnight splits across two files.** With 101 runs of 25 to 60 minutes each,
   unattended overnight batches are exactly when this happens. The harness would export half a
   run and not notice.
2. **Truncating `archives.json` also empties that day's stored archive**, because it is the same
   inode. The run protocol's truncate step does not clear a scratch file, it deletes the day's
   permanent record. Safe only if the export already succeeded and was verified.

**How to answer:**
- Have the harness read the **dated file** for the run's date rather than `archives.json`, or
  detect a date boundary inside a window and export both files.
- Verify the export, by hash or line count, **before** any truncate.
- Better: stop truncating at all and let Wazuh's own rotation manage the files, exporting the
  dated archives instead. That removes a destructive step from a 101-run unattended loop.
- `/usr/local/sbin/telos-archive` needs a subcommand to list and read the dated tree. It cannot
  today, and the harness account has no other root access by design.

**What a bad answer means:** a run silently exports partial data, or the truncate step destroys a
day of archives that was never successfully copied. Both are unrecoverable after the fact.

### Resolution, 2026-09-03

**Decision: the harness exports by date and never truncates anything.**

`lab/scripts/telos-archive` was rewritten. `truncate` and `rotate` are **removed entirely**, and
these were added:

| Subcommand | What it does |
|---|---|
| `dated-list` | every dated archive with size and whether it is gzipped |
| `dated-path DATE` | resolve `YYYY-MM-DD` to its archive path |
| `export DATE` | copy that day's archive to `/tmp` as `.gz`, then print `bytes_gz`, `sha256_gz` and `lines` so the caller can **verify** the copy rather than assume it |
| `disk` | free space on the filesystem holding the archives |

`tail`, `count` and `show` now take an optional `DATE` and read gzipped dated archives through
`zcat`. **If a window crosses midnight, export both dates.**

**The second benefit is worth naming in Chapter 3.** With truncation gone, the tool has **no
destructive subcommand at all**, so the single sudoers rule grants the harness account **read and
export only**. It cannot alter or delete the evidence store. The question "how do you know your
archives were not modified?" now has a checkable answer rather than an assurance.

**What this moves rather than removes.** Disk management now depends entirely on Wazuh's own
rotation plus a retention policy that is still deferred (see item 3). The harness must check free
space before every run with `telos-archive disk` and abort cleanly when low. That guard was
already in the blueprint risk table; it is now load-bearing.

**Updated in:** `lab/blueprint.md` section 6 step 10, runbook Phase 6 step 10, and
`lab/scripts/telos-archive`.

**Installation is a student step**, because replacing a root-owned file needs sudo and the
harness account has none:

```bash
sudo install -o root -g root -m 755 /home/eli/telos-archive /usr/local/sbin/telos-archive
```

---

## 7. Does vmnet3 have a host adapter connected, and should it?

**Status:** **Answered 2026-09-03.** Yes it has one, nothing uses vmnet3, and the record has been
corrected rather than the machine. Resolution at the end of this item.

**Why it matters:** the Phase 1 record and the runbook describe vmnet3 as host-only with **no
host adapter**. The host says otherwise, verified 2026-09-02:

```
VMware Network Adapter VMnet3   Up   10.20.20.1/24
```

The adapter is connected and the Windows host holds an address on that network. If vmnet3 was
meant to be isolated, that claim is currently false and any statement in the thesis about
isolation on that segment would be wrong.

Nothing uses vmnet3 yet, so nothing is broken today.

**Separate but related, recorded here so it is not lost:** VMnet8 originally had **no** host
adapter, which is why the first SSH attempt to `192.168.243.129` timed out. It was enabled
deliberately on 2026-09-02 via "Connect a host virtual adapter to this network". That is a host
configuration change and it is now part of the host baseline.

**How to answer:** decide whether vmnet3 is meant to be isolated. If yes, untick its host
adapter in the Virtual Network Editor and correct the Phase 1 record. If no, correct the record
to say the adapter is connected on purpose. Either way the document and the machine must agree.
Do it before the Phase 5 golden snapshot.

**What a bad answer means:** low technical damage, real thesis damage. A written isolation claim
that the machine does not support is the kind of thing a panelist can check.

### Resolution, 2026-09-03

**Verified on the host:**

```
VMware Network Adapter VMnet3   Up   10.20.20.1/24

Which VMs are attached to vmnet3?
  SIEM-01.vmx   : VMnet8, VMnet2
  WIN-EP-01.vmx : VMnet8, VMnet2
```

**No virtual machine is attached to vmnet3 at all.** It is a configured network with a host
adapter and nothing on it.

**The record was corrected, not the machine.** Re-reading runbook Phase 1, it never actually said
vmnet3 has no host adapter. It said vmnet2 should keep its adapter and left vmnet3 unstated, and
the contradiction was with an inference rather than with anything written. Phase 1 now states
explicitly that vmnet3 **has** a host adapter at `10.20.20.1/24` and is unused.

**Nothing was unticked**, for two reasons. Nothing is on that network, so there is no isolation
claim to defend today, and unticking requires the Virtual Network Editor with administrator
rights, which is a manual step with no benefit right now.

**The condition under which this reopens:** if `IDS-01` is ever built on vmnet3 as a promiscuous
monitor segment (`lab/blueprint.md` Tier B) **and** the thesis claims that segment is isolated,
the host adapter must be unticked at that point and the claim re-verified. That condition is
written into runbook Phase 1 so it cannot be missed.

---

## 8. The Wazuh agent's own scheduled modules fire inside every capture window

**Status:** **Closed 2026-09-03.** Four modules disabled and verified on 2026-09-02. The
agent-upgrade remainder is answered procedurally, because it has no agent-side switch. See both
resolutions at the end of this item.

**Why it matters:** the agent's default configuration runs five scan modules on their own
timers. With `logall_json` on, every event they produce lands in `archives.json`. These are
events generated by the **measuring instrument**, not by the machine under test.

Read from `ossec.conf` on WIN-EP-01 on 2026-09-02:

| Module | Setting | Fires inside a 25 to 60 minute capture window? |
|---|---|---|
| **FIM synchronization** | `<interval>5m</interval>` | **Yes, five to twelve times every run** |
| **FIM real time** | `Real-time file integrity monitoring started` | **Yes, continuously, on every file change** |
| syscollector | `interval 1h`, `scan_on_start yes` | Often, and always right after a revert |
| SCA (policy `cis_win11_enterprise.yml`) | `interval 12h`, `scan_on_start yes` | **Always**, because every run starts from a revert |
| rootcheck | enabled, runs at start | **Always**, same reason |
| syscheck full scan | `frequency 43200` (12 h) | **Always**, same reason |
| cis-cat, osquery | `disabled yes` | No |

**`scan_on_start yes` is the sharp part.** Every Phase 6 run begins with a snapshot revert and a
boot, so SCA, rootcheck, syscollector and the FIM scan run at the start of **every** run, and the
FIM sync then fires every 5 minutes throughout. Observed directly in `ossec.log` after the
2026-09-02 13:19 boot: rootcheck, an SCA scan lasting 25 seconds, a syscollector evaluation and a
FIM scan all completed within 21 seconds of the agent starting.

This noise lands in the coefficient of variation, which is the number T1's whole statistical
argument rests on.

**A second, separate problem in the same log.** `wazuh-modulesd:agent-upgrade: Module Agent
Upgrade started.` The manager can push a new agent version to the endpoint. That is the Windows
twin of the Wazuh apt repo disabled on SIEM-01 in Phase 2, and an agent version bump partway
through invalidates every earlier run under runbook rule 2.

**What a bad answer means:** run-to-run event counts differ for reasons unrelated to any
hardening change, and the difference is not even constant, because a 12-hour timer lands in some
runs and not others. That is contamination of the primary measurement, not a performance issue.

### Resolution, 2026-09-02

Four modules disabled in the agent's `ossec.conf`, each with a comment in the file explaining
why. Verified from what the agent reports about itself after restart, not from the file:

```
2026/09/02 13:56:21  (6001): File integrity monitoring disabled.
2026/09/02 13:56:21  rootcheck: Rootcheck disabled.
2026/09/02 13:56:21  syscollector: Module disabled. Exiting...
2026/09/02 13:56:21  sca: Module disabled. Exiting.
```

The measurement path is untouched. `Application`, `Security`, `System`,
`Microsoft-Windows-Sysmon/Operational` and `active-responses.log` are all still analyzed, and the
agent reports `Connected to the server` with `status='connected'`.

`ossec.conf` is now **11,848 bytes, SHA256
`1F36416E1BC59443D98AD0307638F5C5C788BEE12C545140AD993A1E4E8F2658`**, committed as
`lab/configs/wazuh-agent-ossec.conf`. The previous version is kept in the guest as
`ossec.conf.telos-pre-item8`.

**Two of those four were more than noise, and this is the part worth remembering.** `sca`
evaluates a **CIS Windows 11 policy**, so its results change when a hardening change is applied.
`syscheck` monitors the registry, so it would **observe the hardening script making its change**.
Both would have produced events that appear only in post-change runs. That is not background
noise. That is the instrument reacting to the thing being measured, and it would have looked like
a finding.

**Still open, with reduced scope.** The log still shows:

```
wazuh-modulesd:agent-upgrade: INFO: (8153): Module Agent Upgrade started.
```

There is **no agent-side switch** for it. The module waits for an upgrade command from the
manager. The only control is on the manager: never issue one. An agent version bump partway
through invalidates every earlier run under runbook rule 2.

### Resolution of the remainder, 2026-09-03

**There is nothing to disable, and nothing automatic to prevent.** The agent-upgrade module is a
listener. Wazuh never pushes an upgrade on its own. One only happens if a person triggers it:
the `agent_upgrade` command line tool on the manager, the Wazuh API, or the **Upgrade** button in
the dashboard.

So the control is procedural, and it needs two parts because a rule nobody can check is not a
control:

1. **Never run `agent_upgrade`, never call the upgrade API, and never click Upgrade in the Wazuh
   dashboard for the whole campaign.** The dashboard button is the realistic risk, because it is
   one click away while looking at an agent's page.
2. **Record the agent version in every run manifest**, read from the agent itself at the start of
   the run. That turns "an upgrade cannot happen" into "an upgrade would be visible in the data",
   which is the difference between an assumption and a check. Phase 4 already lists the agent
   version as a pinned value; this makes it a per-run field as well.

**What a bump would cost:** every run collected before it becomes non-comparable under runbook
rule 2. Detecting it in the manifest means discarding the runs after the bump instead of
discovering months later that the whole set is mixed.

---

## 12. Active response lets the manager run commands on the endpoint

**Status:** **Fixed 2026-09-03.** Disabled and verified. Resolution at the end of this item.

**Why it matters:** the agent's config has

```xml
<active-response>
  <disabled>no</disabled>
</active-response>
```

Active response lets the **manager execute commands on WIN-EP-01**. That is the measuring
instrument modifying the machine under test, possibly in the middle of a capture window. It is
worse than the scan modules in item 8, because those only added events. This changes state.

Nothing has fired so far. The risk is that a default manager rule triggers one during a real
Atomic Red Team run, which is exactly when the manager is most likely to see something it reacts
to.

**How to answer:** either set `<disabled>yes</disabled>` on the agent, or list which active
responses the manager actually has configured and prove none can trigger. The first is one line
and is reversible; the second is more work but keeps the deployment closer to a real one.

**What a bad answer means:** an untracked state change lands inside a capture window, and the
post-change run differs for a reason that is not the hardening change and is not recorded
anywhere.

### Resolution, 2026-09-03

`<active-response><disabled>yes</disabled>` in the agent config, with a comment in the file saying
why. Confirmed by the agent itself after restart:

```
2026/09/03 08:04:36 wazuh-agent: INFO: (1350): Active response disabled.
```

All five collection channels still analyzed, `status='connected'`. `ossec.conf` is now **12,115
bytes, SHA256 `CED16E0B41384BF421192317E3754732D0E3155A85BA98F2CEEDFA846B0278B1`**, committed as
`lab/configs/wazuh-agent-ossec.conf`. Previous version kept in the guest as
`ossec.conf.telos-pre-item12`.

**To reverse:** one word in the file, or restore `ossec.conf.telos-pre-item12`.

---

## 13. The agent has its own rate limiter, a third silent loss channel

**Status:** Open, unmeasured. Raised 2026-09-02.

**Why it matters:** the agent config contains

```xml
<client_buffer>
  <disabled>no</disabled>
  <queue_size>5000</queue_size>
  <events_per_second>500</events_per_second>
</client_buffer>
```

If a run produces more than **500 events per second**, the agent throttles. If the **5000-event**
queue then fills, events are dropped before they are ever sent.

**There are now three loss channels between the endpoint and `archives.json`**, and they are the
same failure in three places:

| Where | Limit | Item |
|---|---|---|
| Sysmon event channel on the endpoint | 64 MB, `Circular` | 9 |
| **Wazuh agent buffer** | **500 events/s, 5000 queued** | **13** |
| journald on SIEM-01 | `RateLimitIntervalSec` and `RateLimitBurst`, unread | 1d |

Every one of them drops events silently, and every drop looks exactly like telemetry lost to a
hardening change.

**How to answer:** during a full capture window, measure the peak event rate on the endpoint and
watch `ossec.log` for buffer-full warnings. Then either raise the limits and pin the new values,
or prove the run stays under them. Note that disabling the buffer entirely removes flow control
rather than removing the loss, so it is not automatically the safer choice.

**What a bad answer means:** the same as 1d and 9. An unmeasured, uncontrolled loss channel
inside the measurement pipeline. A threat to validity, not a performance issue.

---

## 9. The Sysmon event channel is 64 MB and overwrites itself

**Status:** Open, and unmeasured under load. Raised 2026-09-02 during Phase 3.

**Why it matters:** this is the Windows twin of item 1d.

```
LogName       : Microsoft-Windows-Sysmon/Operational
MaximumSizeMB : 64
LogMode       : Circular
```

`Circular` means the oldest events are overwritten when the channel fills. If a capture run
produces more than 64 MB of Sysmon events before the Wazuh agent has read them, the oldest are
overwritten and **never sent to the manager**. They never reach `archives.json` and never appear
in any result.

The loss would look exactly like a hardening effect, and it would be biased toward the **start**
of the window, which is where the start fence and the first technique executions are.

**How to answer:** measure the channel's byte growth across one full capture window with a real
technique list. Then either raise `MaximumSizeInBytes` and record it as a pinned baseline value,
or prove the run stays under 64 MB. Note that raising it is itself a configuration change that
must be recorded and applied identically to Config S and Config N.

**Related measurement already taken:** endpoint-to-archive latency is about **1.6 to 1.9
seconds** (fence recorded on the endpoint at `13:30:38.7096614Z`, stamped by the manager at
`13:30:40.599`; end fence `13:30:47.711` and `13:30:49.311`). The agent is not far behind, which
lowers but does not remove the risk.

**What a bad answer means:** an unmeasured, uncontrolled loss channel inside the measurement
pipeline, exactly like 1d. Threat to validity, not performance.

---

## 10. Defender Tamper Protection will silently defeat Config S

**Status:** **Answered 2026-09-03.** Turned off, and the fix was verified by a functional test,
not by reading a flag. Resolution at the end.

**Why it matters:** `lab/blueprint.md` section 5 defines Config S as "Defender off, Windows
Update off, tasks disabled". On WIN-EP-01, `Get-MpComputerStatus` reports:

```
RealTimeProtectionEnabled : True
IsTamperProtected         : True
```

**Tamper Protection blocks scripted changes to Defender's protection settings.** A script that
turns real-time protection off will fail, and it will not necessarily fail loudly. Config S would
then be a snapshot that is not actually suppressed, while the analysis assumes it is.

Tamper Protection cannot be switched off from a script. It is a manual toggle in the Windows
Security window inside the VM.

**One thing that does still work, verified:** `Add-MpPreference -ExclusionPath` was accepted while
Tamper Protection was on. So exclusions are not blocked, but protection state changes are.

**How to answer:** before the Config S snapshot, turn Tamper Protection off by hand in the guest,
then verify from a script that `Set-MpPreference -DisableRealtimeMonitoring $true` actually takes
effect by reading `Get-MpComputerStatus` back. Never assume the write succeeded.

**What a bad answer means:** Config S and Config N are the same machine wearing different labels,
and the whole suppressed-versus-natural comparison in blueprint section 7 collapses without
anyone noticing.

### Resolution, 2026-09-03

Turned off by hand in Windows Security inside the guest, which is the only way it can be done.

**Reading the flag was not accepted as proof.** `IsTamperProtected : False` is necessary but not
sufficient. What Phase 5 actually needs is for a **script** to change a Defender setting and have
the change stick. So a functional test was run: flip one harmless setting, read it back, then put
it exactly as it was.

```
IsTamperProtected             : False
RealTimeProtectionEnabled     : True
DisableCpuThrottleOnIdleScans : True -> False -> restored to True
RESULT: scripted changes to Defender ARE accepted. Config S will work.
ExclusionPath                 : C:\AtomicRedTeam   (still in place)
WazuhSvc                      : Running, status='connected'
```

**Rule carried into Phase 5, because a flag can be re-enabled:** after applying Config S, **read
every setting back and confirm it took effect** before taking the snapshot. Never assume a
`Set-MpPreference` succeeded. Written into runbook Phase 5.

**Note:** Windows may re-enable Tamper Protection on its own after some updates. It is worth
re-checking immediately before the golden snapshot rather than trusting today's result.

---

## 11. SIEM-01 restarted twice with no shutdown recorded (ANSWERED, see the Answered section)

**Status:** **Answered 2026-09-02.** Host power loss for the second event, a deliberate power off
for the first. Evidence and reasoning are in the Answered section at the bottom. Kept here so the
numbering stays stable.

**Why it matters:** a SIEM that stops in the middle of a capture run loses that run. If it
happens on its own schedule, it can ruin an unattended overnight batch and the loss may not be
noticed for hours.

**Evidence, 2026-09-02:**

```
journalctl --list-boots
 -2  2026-09-02 10:27:16 UTC -> 11:26:59 UTC
 -1  2026-09-02 11:56:53 UTC -> 13:05:17 UTC
  0  2026-09-02 13:19:11 UTC -> running

last -x reboot
  reboot system boot  Wed Sep  2 13:19   still running
  reboot system boot  Wed Sep  2 11:56   still running     <- no shutdown recorded
```

The VM was started once, at about 10:27. Two further restarts are unaccounted for. **The previous
boot's journal ends abruptly** at 13:05:17 with no shutdown sequence at all, and the hypervisor's
own `vmware-0.log` also stops mid-stream at 12:56 with no power-off lines. Both are the signature
of a process that was terminated rather than shut down.

**Ruled out already:** memory. `MemSched` in the VMware log shows about 12 GB locked against a
55 GB ceiling with two VMs running, SIEM-01 reports 12 GB free of 15 GB, and
`journalctl | grep -c 'out of memory\|oom-kill'` returns `0`. The only errors in the previous
boot were harmless SMBus and Bluetooth kernel messages.

**Side effect already caused:** `/tmp` is cleared on boot, which silently deleted a staged script
and made an install command fail with a confusing error. Lab files now go to the home directory,
not `/tmp`.

**How to answer:** confirm whether I powered off or reset the VM through the VMware
interface at those times. If not, watch `vmware.log` and `journalctl --list-boots` across the next
few sessions and look for a pattern.

**What a bad answer means:** if the VM is stopping on its own, Phase 6 needs a watchdog that
detects a dead SIEM and aborts the run cleanly, rather than writing a run manifest for a run whose
data was never collected.

---

## Answered

### Can the Unified Write Filter replace snapshot restore on a physical endpoint? (answered 2026-09-11, item 19)

**Answer: yes. All six steps passed, and it costs less than the item assumed.**

Tested on WIN-EP-01, Windows 11 **Education**, build `10.0.26100.9168`, licence status
**Notification**, that is unactivated. Every step run from the host through
`vmrun runProgramInGuest`, which was found to give a **full administrator token**, so no step
needed a person at the guest console.

| # | Question | Result |
|---|---|---|
| 1 | Does the feature exist on this build | **Pass.** `Client-UnifiedWriteFilter`, `State : Disabled`. 5 of 137 features matched `*Filter*` |
| 2 | Does it enable on unactivated Windows | **Pass.** Enabled with `-All`. Parent is `Client-DeviceLockdown`. `uwfmgr.exe` present after reboot, 230,904 bytes |
| 3 | Does a write made before a reboot disappear after it | **Pass.** Six markers, files and registry, `HKLM` and `HKCU`, all gone |
| 4 | Can a change be made to survive | **Pass, without servicing mode.** `uwfmgr registry commit` and `file commit` |
| 5 | Does one capture-length window fill the overlay | **Pass.** 40 minutes, peak **191 MB of 1024 MB**, **zero UWF events** |
| 6 | Does UWF change what Sysmon logs | **Pass.** 100 of 100 stimulus events logged with the filter both on and off |

**Six risks were stated when the item was raised. Measurement changed four of them.**

**Risk 1, UWF reverts the hardening change too. Solved, and the stated cost was wrong.** The item
budgeted "two extra reboots per hardening change" for servicing mode. **The real cost is zero.**
`uwfmgr registry commit <key> <value>` and `uwfmgr file commit <path>` write one specific change
through to the disk while the filter stays on, with no reboot and no exclusion list. Proved with a
control: two markers committed survived a reboot, two written identically and not committed did not.

**Risk 2, the overlay fills mid-run. Real but far smaller than feared, and the mechanism was
misunderstood.** An overlay holds the **current difference between the machine and its disk, not the
sum of everything written to it**. Consumption was observed to *fall* when files it held were
deleted. Measured on this machine:

```
boot          about 138 MB, once, almost all in the second minute after power-on
idle          2.35 MB per minute
under load    0.45 MB per minute (440 process spawns and file cycles in 20 minutes)
default overlay : 1024 MB, in RAM, warning at 512 MB, critical at 1024 MB
```

**The event channel names to watch are `Microsoft-Windows-UnifiedWriteFilter/Operational` and
`/Admin`.** Both existed, both enabled, both held **0 records** throughout. Overlay usage is readable
live with `uwfmgr overlay get-consumption` and `get-availablespace`, so a harness can measure it at
both ends of a window rather than only checking for Event ID 2 afterwards.

**Risk 3, unsent events die at the reboot. Confirmed and wider than written.** It is not only the
Wazuh agent's queue. **The entire local event log is discarded.** A run's Sysmon events written under
the filter were absent after the next reboot, while the channel still held events from nine days
earlier, so this was not ageing out of a circular buffer. Anything not forwarded to the SIEM before
the restart does not exist afterwards.

**Risk 4, UWF changes the telemetry it is meant to preserve. Not supported.** An identical
100-iteration stimulus was run with the filter off and with it on. Counting only the events the
stimulus produced, both runs logged **exactly 100** Sysmon Event 1. Apparent differences in the
totals were background activity.

**Risk 5, unactivated Windows. Closed.** `slmgr /dlv` reports `License Status: Notification`,
`Notification Reason: 0xC004F034`. The DISM feature installed anyway. Activation is not a blocker.

**Risk 6, the niche is narrow. Unchanged.** `vmrun` still reverts in seconds and remains correct for
this lab. UWF's case is a physical host, and C8 (Credential Guard) remains the one candidate that
justifies it (item 2).

**What this changes.** `proposal-form-FINAL.md:240` can widen its precondition from "virtual machines
under a hypervisor supporting snapshots" to "the ability to return the host to a known state, by
hypervisor snapshot, write filter, or disk image", **and the same statement must be added to Scope
and Limitations, where the restriction is currently missing either way.** That edit is a separate
decision and was deliberately not made during testing.

**Honest limits on this result, which should be stated wherever it is used.**

1. **No real capture was run**, because no capture harness exists. The 40-minute window used a
   synthetic load.
2. **That load deleted the files it created. A real Atomic Red Team run leaves artifacts behind**,
   and those consume overlay permanently. **0.45 MB per minute is a floor, not a forecast.**
3. **Only Sysmon Event 1 was verified end to end.** This machine's Sysmon configuration does not log
   file creation, and does not watch arbitrary registry keys, so those paths could not be compared.
4. **Servicing mode itself was never tested.** It remains the only known route for a hardening
   change that is not a single registry value or a single file, such as one applied by `auditpol` or
   Group Policy.

**A false finding that was caught, recorded because the method matters more than the result.**
Comparing event **totals** between the filter-on and filter-off runs showed Sysmon registry event 13
at 1 versus 99 and looked like UWF suppressing registry telemetry. A third run added a control: two
keys written in the same loop, one filtered by UWF and one added to UWF's exclusion list. **Neither
was logged**, so this Sysmon configuration never watched those keys and UWF was not involved. **A
difference in a total is not a finding.**

### 1b. Can Module 2 see field-level telemetry loss? (answered 2026-09-04)

**Answer: not as originally designed. The schema was changed so it can.**

The unit of analysis is now the event type **plus which tracked fields were populated**, written
`Security-4688[CommandLine,NewProcessName]`. Full reasoning in DECISIONS.md, same date.

**The failure, demonstrated in code.** Keyed on event type alone, a change that empties
ScriptBlockText inside PowerShell 4104 leaves the rate at 838 per window in both phases. The
analyser reports UNCHANGED, correctly on the evidence it has, and the blind spot is invisible.
Test: `test_field_loss_is_invisible_to_event_type_keying`.

**The fix, demonstrated in code.** Same rates, same statistics, composite key:

```
PowerShell-4104[Path,ScriptBlockText]   838 -> 0     LOST
PowerShell-4104[Path]                     0 -> 838   NEW
lost field(s): ScriptBlockText
```

Test: `test_field_loss_is_caught_by_field_aware_keying`. The demo prints this as an explicit
FIELD-LEVEL LOSS section rather than leaving a reader to pair an unexplained LOST with an
unexplained NEW.

**What it cost:** one new module (`src/telos/eventkey.py`), a rewritten synthetic generator, and
29 new tests. **No change to `differential.py`, `variance.py` or `baseline.py`** — they treat the
key as an opaque string, which was verified before starting.

**Honest limit carried into the paper:** this is a profiling improvement, not a statistical one,
and the naive baseline benefits from it equally. The composite key improves what can be *seen*;
the variance model and correction improve what can be *trusted*. Two separate contributions,
to be claimed separately.

**Not resolved by this:** value-level degradation, where a field stays populated but its content
changes (Constrained Language Mode altering 4104 content, for example). Out of scope, and the
paper should say so.

### Why did SIEM-01 restart twice with no shutdown recorded? (answered 2026-09-02, item 11)

**Answer: two different causes, neither of them a fault in the VM.** The 13:05 stop was a **host
power loss**, the power cable was pulled by accident. The 11:27 stop was a **deliberate power
off**.

**Evidence.** Windows records unexpected shutdowns explicitly, so this was answerable from the
guest's own System log rather than from reasoning:

```
2026-09-02 11:27:05 UTC  Id=1074  StartMenuExperienceHost.exe (WIN-EP-01) has initiated the
                                  power off of computer WIN-EP-01 on behalf of user WIN-EP-01\eli
2026-09-02 11:56:56 UTC  Id=6005  The Event log service was started.

2026-09-02 13:19:07 UTC  Id=41    The system has rebooted without cleanly shutting down first.
2026-09-02 13:19:10 UTC  Id=6008  The previous system shutdown at 12:36:56 PM was unexpected.
```

Event ID 41 with 6008 is exactly the power-loss signature. Both guests also came back within two
seconds of each other, WIN-EP-01 at `13:19:03` and SIEM-01 at `13:19:05`, which is a host-level
event and not a VM-level one.

**One thing not to over-read.** `6008` names `12:36:56` as the last shutdown, which is earlier
than SIEM-01's final journal line at `13:05:17`. That is not a contradiction. Windows writes that
"still alive" timestamp on a timer, so it is a lower bound on when the machine died, not the
moment it died.

**What stays as a risk, and it is not the same question.** A 67-hour unattended capture campaign
has no protection against host power loss. A run interrupted this way is lost, and the harness
would not know unless it checks. This belongs in the Phase 6 design as a watchdog requirement:
detect a guest that died mid-run and abort that run cleanly rather than writing a manifest for
data that was never collected. It is not an open question about a fault, it is a known property
of the environment.

**Side effect worth remembering:** `/tmp` on SIEM-01 is cleared on boot. A reboot silently deleted
a staged script and made an install command fail with `cannot stat`. Stage lab files in the home
directory, never `/tmp`.

### Why were the VMware VMnet1/2/3 adapters in Error state? (answered 2026-08-31)

**Answer: fixed by Virtual Network Editor → Restore Defaults, then reconfiguring vmnet2 and
vmnet3.** The working theory (a lingering Hyper-V virtual switch conflicting with VMware's
adapters) was never confirmed as the exact cause, but the standard repair worked.

**Evidence, verified 2026-08-31 after running the fix:**

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

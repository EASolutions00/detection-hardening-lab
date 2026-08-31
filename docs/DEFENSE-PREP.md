# Pre-Oral Defense Prep: T1, T2, T3

Everything needed to defend any one of the three titles. Written for the pre-oral topic
proposal defense at AMA University Online Education. Student: Elijah Amorsolo, OED20-0012616.

How to use this file:
1. Read Section 2 until you can explain every term without reading.
2. Read the full section for all three topics. The panel picks, not you.
3. Drill Section 7. That is where defenses are won or lost.
4. Read Section 8 before you walk in. Those are the holes in your own papers.

Everything here is traced to a source. Repo files are named. Papers carry the reference from
the proposal. Anything that is engineering judgment is marked `(unverified)`.

---

## 0. What you must be able to do in the room

A pre-oral topic defense is not a defense of results. You have no results yet. The panel is
judging four things:

1. **Is the problem real?** Can you show it exists outside your imagination.
2. **Is it a computer science problem?** Is there an algorithm, not just a configuration task.
3. **Can this student finish it?** Scope, resources, time.
4. **Can it be measured?** What number proves you succeeded or failed.

Every answer you give should land on one of those four. If a question confuses you, ask
yourself which of the four it is really about, then answer that.

Three sentences you should be able to say for any of the three titles, without notes:
- The problem in one sentence.
- The method in one sentence.
- The number that proves it worked in one sentence.

---

## 1. The three titles in one line each

| # | Short name | Full title | Needs a lab? |
|---|---|---|---|
| T1 | Hardening-induced blind spots | Detection of Hardening-Induced Blind Spots via Differential Sequence Alignment of Pre- and Post-Change Security Event Streams | Yes. Full purple team lab. |
| T2 | Severity inversion | Automated Detection of Severity Inversion in the Wazuh Default Ruleset Using Parent-Child Dependency-Graph Analysis and Topological Consistency Scoring | No. Offline static analysis. |
| T3 | Analytic-robustness scoring | Automated Analytic-Robustness Scoring of Sigma and Wazuh Detection Rules Using a Rule-Feature Dependency Model Based on the Summiting the Pyramid Methodology | No. Offline static analysis. |

They are alternatives. One gets built. This is stated in [thesis/README.md](../thesis/README.md).

**Important status note.** T1 is your primary choice and is gated behind a feasibility test
that has not run yet. T3 was the planned fallback, but on 2026-08-19 you measured that SigmaHQ
carries STP robustness tags on only 6 of 3,783 rules, which kills T3's Objective 5 as written
(see [docs/DECISIONS.md](DECISIONS.md) and [docs/OPEN-QUESTIONS.md](OPEN-QUESTIONS.md)). So the
honest current state is: T1 is primary, and the second choice between T2 and T3 is not settled.
If a panelist asks which is your second choice, say exactly that. Do not invent a ranking.

---

## 2. Shared background you must be able to explain

One sentence each, in plain words. If you cannot say these without notes, you are not ready.

**SOC (Security Operations Center).** The team and the function that watches for attacks and
responds to them.

**SIEM (Security Information and Event Management).** A platform that collects log data from
many machines, puts it in one format, and checks it against detection rules. When a rule
matches, it raises an alert.

**XDR (Extended Detection and Response).** A newer name for the same idea, extended across
endpoint, network, and identity data.

**Wazuh.** A free and open-source SIEM and XDR platform, built from the older OSSEC project.
Its rules are written in XML. Each rule has a number and a severity level. Levels run 0 to 15
(general knowledge from the Wazuh documentation; confirm the exact page before the defense).

**Detection rule.** A written statement of what malicious activity looks like in log data.

**Detection engineering.** The practice of writing, testing, versioning, and retiring detection
rules like software. Often called detection-as-code.

**Sigma.** An open, vendor-neutral rule format written in YAML. One Sigma rule can be converted
into the query language of many different platforms. SigmaHQ is the public repository of them.

**Sysmon.** A Microsoft tool that makes Windows write much more detailed events about process
creation, network connections, and file changes than Windows writes by default.

**Windows Event ID.** A number identifying an event type. Examples you must know:
- 4688 process creation
- 4624 successful logon, 4625 failed logon
- 4104 PowerShell script block logging, 4103 PowerShell module logging
- 4776 NTLM credential validation
- Sysmon Event ID 1 process creation, Sysmon Event ID 10 process access (used for LSASS access)

**MITRE ATT&CK.** A public catalogue of the tactics and techniques attackers actually use. It
gives everyone a shared vocabulary for saying what you can and cannot detect.

**Coverage.** The share of relevant ATT&CK techniques for which you have at least one detection
rule. Usually shown as a shaded matrix (ATT&CK Navigator layer).

**Atomic Red Team.** A free library of small scripted tests. Each test safely reproduces one
attacker technique so you can see whether your detection fires.

**BAS (Breach and Attack Simulation).** Commercial tooling that runs attack simulations
continuously to check that detections still work.

**System hardening.** Changing configuration to reduce the attack surface. Turning off old
protocols, restricting scripting, tightening policy.

**CIS Benchmarks.** Published hardening baselines from the Center for Internet Security.

**DISA STIG.** Published hardening baselines from the US Defense Information Systems Agency.

**Pyramid of Pain.** David Bianco, 2013. Orders indicator types by how much it costs the
attacker to change them. File hashes and IP addresses at the bottom, cheap to change. Tools and
behaviour at the top, expensive to change.

**Summiting the Pyramid (STP).** A methodology from MITRE Engenuity Center for Threat-Informed
Defense that turns the Pyramid of Pain idea into a defined scoring scheme for a detection
analytic, with levels for host-based and network-based detections.

**Analytic robustness (evasion resistance).** How hard it is for an attacker to evade a rule.
Different from coverage, which only asks whether a rule exists.

**Static analysis.** Examining an artifact without running it. Used on program source code, and
here used on rule files.

**Precision, recall, F1.** Precision is: of the things I flagged, how many were real. Recall is:
of the real things, how many did I find. F1 is the balance of the two, the harmonic mean.

**False positive rate.** How often the system flags something that was not real.

**Chi-square test of homogeneity.** A statistical test that asks whether two groups have the
same distribution of counts, or whether the difference is more than chance.

**Poisson rate ratio.** For count data, the ratio of two rates, with confidence bounds. It gives
the size of the change, not just whether a change exists.

**Benjamini-Hochberg false discovery rate correction.** When you run hundreds of tests at once,
some will look significant by chance alone. This procedure controls the share of your findings
that are false.

**Coefficient of variation (CoV).** Standard deviation divided by the mean. A unit-free measure
of how much a number bounces around between repeats.

**Cohen's kappa.** Measures agreement between two raters and corrects for agreement that would
happen by chance. Used when you compare an automated label against a human label.

**Directed graph.** Points (vertices) joined by one-way arrows (edges).

**Topological ordering.** An ordering of a directed graph in which every parent comes before its
children. Kahn's algorithm computes it.

**Strongly connected component.** A group of vertices that can all reach each other, which means
a cycle. Tarjan's algorithm finds them. You need this because a strict topological order does
not exist when there are cycles.

---

## 3. T1 in full: Hardening-Induced Blind Spots

**Full title.** Detection of Hardening-Induced Blind Spots via Differential Sequence Alignment
of Pre- and Post-Change Security Event Streams.

Source: [thesis/T1/proposal.txt](../thesis/T1/proposal.txt).

### 3.1 The one-paragraph version

You harden a machine to make it safer. Hardening changes configuration. Configuration decides
which events the machine writes. So a hardening change can silently remove the evidence that a
detection rule depends on. The rule stays enabled and still appears on the coverage report, but
it can no longer fire. Nothing errors. Nobody finds out until an incident. This system captures
the event stream before the change and after the change under the same scripted attack
stimulus, compares the two with statistical tests, and reports which event types were lost and
which detection rules and ATT&CK techniques go blind as a result.

### 3.2 Threat model, said the way a security architect says it

Use the standard definitions. An asset is anything of value that must be protected. Detection
capability is **not** an asset. It is a control. Do not mix the two in the room.

- **Primary asset (ISO 27005):** the information held on the monitored systems, and the business
  processes that depend on it.
- **Supporting assets:** the endpoints and servers, and the security event telemetry they
  generate. Log data counts as an information asset in its own right, because it is the evidence
  used for investigation and it carries retention obligations.
- **Control at risk:** the detection rules and the SIEM that evaluates them. NIST CSF 2.0 DETECT
  function, DE.CM continuous monitoring.
- **Threat actor:** an intruder whose activity is no longer evidenced. Note that the attacker
  does not cause the blind spot here. The defender causes it, by hardening.
- **The mechanism, in framework terms:** hardening is a PROTECT activity under PR.PS Platform
  Security. PR.PS-04 requires that log records are generated and made available for continuous
  monitoring. A configuration change made to satisfy one PROTECT control can break PR.PS-04,
  which starves DE.CM. The control fails and emits no signal.
- **Impact:** dwell time rises, response is delayed, and the loss to the primary asset is larger
  than it would have been.
- **Framework fit:** MITRE ATT&CK for expressing which techniques go unobserved, NIST CSF 2.0
  for where the failure sits. Say the split out loud: this is a DETECT problem created by a
  PROTECT action.

The one sentence worth memorizing: **hardening strengthens PROTECT and can silently weaken
DETECT, and nothing in the current process measures that trade.**

Source for PR.PS-04, which replaced PR.PT-1 in CSF 1.1:
https://csf.tools/reference/nist-cybersecurity-framework/v2-0/pr/pr-ps/pr-ps-04/

### 3.3 Why the current process misses it

From the proposal, current practice verifies a hardening change in two ways only:
1. A compliance check that the setting is now in effect.
2. A functional regression test that business applications still work.

Neither looks at detection. Where detection is checked at all it is ad hoc, and it depends on
one engineer remembering which rules consume which event sources. Some organizations have a
rule health report that flags rules which have not fired recently, but a rule that has not fired
because no attack happened looks exactly the same as a rule that cannot fire any more.

### 3.4 Problems and objectives, paired

The institutional template requires exactly 5 problems and 5 specific objectives, and objective
N answers problem N. Memorize the pairing. A panelist can ask "which objective answers problem
3" and you must not hesitate.

| # | Problem | Objective |
|---|---|---|
| 1 | Hardening silently removes telemetry, with no error, alert, or failure sign | Build the differential sequence alignment algorithm over normalized frequency profiles that finds absent or reduced event types |
| 2 | The existing change process checks compliance and application function, never detection | Put the algorithm inside an automated validation workflow with scripted adversary simulation, so coverage checking becomes an explicit stage |
| 3 | Manual before-and-after comparison does not scale | Automate the comparison across the complete event-type space |
| 4 | Naive count differencing gives too many false alarms because normal variance moves counts | Add chi-square homogeneity testing, Poisson rate ratio with confidence bounds, and Benjamini-Hochberg correction, and measure the false positive reduction against the naive baseline |
| 5 | Even when a loss is found, nothing links it to the affected rules and techniques | Build blind-spot impact scoring that maps lost event types to dependent rules and ATT&CK techniques, and produces a ranked report |

### 3.5 The five modules

1. **Telemetry Acquisition and Experiment Control.** Defines a validation run. Restores the VM
   snapshot, triggers the attack simulation, pulls events from the Wazuh API, tags everything
   with run ID and phase label (pre, post, control).
2. **Event Normalization and Profiling.** Parses Windows Security events, Sysmon events, and
   network IDS alerts. Builds a normalized frequency profile: rate of each event type per unit
   of observation time. Computes per-event-type variance from control runs.
3. **Differential Alignment and Statistical Analysis.** The core. Aligns the two profiles across
   the union of event types, handles types present in only one, runs chi-square and Poisson rate
   ratio per event type, applies Benjamini-Hochberg across all comparisons, classifies each
   event type, and also implements the naive baseline for comparison.
4. **Blind-Spot Impact Scoring and Coverage Mapping.** Holds the dependency index from event
   type to detection rule to ATT&CK technique. For each lost event type, walks the index,
   computes a weighted impact score from rule severity, number of rules affected, and tactic
   significance. Ranks findings.
5. **Reporting, Visualization, and Experiment Validation.** Ranked report, side-by-side profile
   views, ATT&CK Navigator layer export. Also holds the ground-truth injection facility and
   computes precision, recall, F1, and false positive rate for both the proposed method and the
   baseline.

### 3.6 The experiment, in numbers

Memorize these. They are the most likely thing to be asked.

| Item | Value |
|---|---|
| Hardening changes tested | 16, each applied in isolation, drawn from CIS Benchmarks and DISA STIGs |
| Repeats per phase | 3 pre-change and 3 post-change |
| Control runs (for the variance model) | 5 |
| Total capture runs | 16 x 6 = 96, plus 5 controls = **101** |
| Settle time after boot | 180 seconds |
| Drain time after the attack suite | 120 seconds |
| Estimated wall clock per run | 25 to 60 minutes `(unverified, must be measured)` |
| Projected total | about 67 hours at 40 minutes per run `(unverified)` |

Source for the run protocol and the time budget: [lab/blueprint.md](../lab/blueprint.md)
sections 6 and 7.

Why 3 repeats per phase: so that within-phase variation is represented in the comparison
instead of being assumed to be zero. Why 5 controls: to build the variance model for each event
type from runs where nothing changed at all.

### 3.7 The lab

| VM | Role | vCPU | RAM | Disk |
|---|---|---|---|---|
| SIEM-01 | Wazuh 4.x all-in-one on Ubuntu LTS | 8 | 16 GB | 200 GB |
| WIN-EP-01 | Windows 11 Enterprise Eval, Sysmon, Wazuh agent, Atomic Red Team | 4 | 8 GB | 80 GB |

Host: Ryzen 7950X, 16 cores and 32 threads, 64 GB RAM, VMware Workstation 17.5.1 Pro.

Wazuh's own quickstart table gives 4 vCPU, 8 GiB, and 50 GB for 1 to 25 agents
(https://documentation.wazuh.com/current/quickstart.html). That figure is for alerts only. T1
needs `<logall_json>yes</logall_json>`, which stores every received event whether or not it
triggered a rule, and the Wazuh docs warn that this costs storage and performance
(https://documentation.wazuh.com/current/user-manual/manager/event-logging.html). The 16 GB and
200 GB numbers are headroom for that. They are `(unverified)` as precise figures.

Four rules in the lab that fail silently if broken (from [CLAUDE.md](../CLAUDE.md)):
1. No VM ever runs from E:, because it is a hard disk and its timing jitter would land inside
   the variance number the whole study rests on. VMs live on F:, which is NVMe.
2. Pin every version before the golden snapshot. A later version bump discards every earlier run.
3. `logall_json` must be on. T1 counts what the machine emits, not what alerted.
4. The golden snapshot is taken with NAT disconnected, so Windows Update, Defender cloud
   lookups, and NTP do not fire inside a capture window.
5. Capture windows are fenced in the telemetry itself, not by host clock. A uniquely named
   command produces a distinctive Sysmon Event ID 1 at the start and at the end.

### 3.8 Ground truth: where the labels come from

This is the question that separates a prepared student from an unprepared one. You cannot hand
label 200 to 500 event types across 16 changes. The plan is two-tier labeling
([lab/blueprint.md](../lab/blueprint.md) section 8):

- **Positive class:** event types the change verifiably removed. You know the truth because you
  caused it.
- **Negative class:** every other event type present in the pre-change profile.

Say plainly: "the labels come from the changes I applied, not from the tool's own output."

**Corrected on 2026-08-20. Use this version, not the older one.** Telemetry loss on its own is
not a blind spot. If you disable SMBv1, SMB1 events stop, but SMB1 attacks stop too, so the rule
should be retired rather than flagged. A blind spot needs four conditions:

> (a) the change is a control from a named benchmark, with its control ID recorded, (b) the
> change removes or degrades an event type or a required field, (c) at least one detection rule
> depends on it, and (d) **the technique that rule covers is still executable after the change.**

Condition (d) is the one that separates this study from a log diff. Memorize it.

The 16 changes are then split into two classes, and both are reported:

| Class | Meaning | Role in the study |
|---|---|---|
| B | Telemetry lost and the attack surface went with it | **Negative control.** The impact score should correctly come out near zero. |
| C | Telemetry lost while the technique remains executable | **The true blind spots.** These are the positive cases. |

That split is a result, not a weakness. The sentence to aim for in Chapter 4: "of 16
benchmark-mandated hardening changes, X removed telemetry along with the attack surface and Y
removed telemetry while the attack remained possible."

### 3.9 Evaluation

- **Baseline:** naive event-count differencing. An event type is called lost whenever its
  post-change count is lower than its pre-change count. No variance model, no significance test.
- **Measures, declared before the evaluation begins:** precision, recall, F1 score, false
  positive rate, and the share of the event-type space successfully analyzed.
- **Design:** developmental (the output is a working system) and experimental (compared against
  a named baseline under controlled conditions).

### 3.10 The falsifiable claim, and why you must not soften it

Before any hardening change is tested, you run a control-versus-control experiment. The same
attack suite, the same restored snapshot, no configuration change at all. You measure the
coefficient of variation of each event type across those runs. That is the variance floor of the
laboratory. The proposal declares both outcomes in advance:

- **If the variance floor is not trivial:** counts differ when nothing changed. The naive
  baseline will report those differences as losses. The false positive reduction achieved by
  your method is then the headline result of the study.
- **If the variance floor is near zero:** the statistical layer buys nothing inside the lab. The
  study reports that plainly, and the statistics are justified only for production deployment,
  where the variance floor is not controlled by snapshot restoration. That restriction is
  recorded as a limitation of your own contribution.

This is deliberate. Do not edit it out and do not hedge it in the room. It is the strongest
answer to the sharpest objection a panel can raise, which is "you built the experiment so that
nothing varies, so why do you need statistics at all."

There is one improvement over the proposal as written that you should mention: run the control
experiment under two configurations, Config S (suppressed: Defender off, Windows Update off,
scheduled tasks disabled) and Config N (natural: defaults left on). Reporting both stops the
panel from saying that your false positive reduction is an artifact of how hard you suppressed
background activity. Source: [lab/blueprint.md](../lab/blueprint.md) section 7.

### 3.11 External validity, stated before they ask

Every measurement comes from a lab where each host is restored to a known state and driven by a
fixed script. Production has none of those properties. Real user activity, scheduled tasks,
patching, and backups all add variance that the lab deliberately removes. The consequence is
one-sided and you should say it first: the naive baseline is hurt by exactly the variance the
lab suppresses, so the false positive rate you measure for the baseline is the lowest it could
ever be. Your measured improvement is therefore a lower bound on the production benefit, not an
estimate of it. Measuring the production benefit needs a real deployment, which is outside the
scope and is named as future work.

### 3.12 Prior work and the gap you fill

**Uetz, Herzog, Hackländer, Schwarz, Henze (2024). "You Cannot Escape Me: Detecting Evasions of
SIEM Rules in Enterprise Networks."** USENIX Security 24, pp. 5179-5196, Distinguished Artifact
Award. Preprint arXiv:2311.10197.
Numbers: of 292 Windows process-creation Sigma rules, 110 (38 percent) fully evadable and 19
(7 percent) partially evadable. Their tool AMIDES detected 70 percent of evasions (358 true
positives, 154 false negatives out of 512) with zero false alerts against roughly 74.4 million
benign events. Rule attribution was top-1 for 63 percent and within top-10 for 95 percent.
**The gap:** AMIDES finds blind spots created by an active attacker in live event streams. You
find blind spots created by the defender's own hardening change, before an attacker arrives,
through a controlled before-and-after experiment.

**Wudali, Kravchik, Malul, Gandhi, Elovici, Shabtai (2025). "Rule-ATT&CK Mapper (RAM)."**
arXiv:2502.02337. Uses LLMs in a multi-stage pipeline to map SIEM rules to ATT&CK techniques,
evaluated on Splunk Security Content, best results with GPT-4-Turbo.
**The gap:** RAM stops at annotating rules. You traverse that same mapping as a weighted
dependency graph to rank remediation and quantify how a telemetry loss cascades into lost
technique coverage.

**Gherabi (2025). "Improving Threat Detection in Wazuh Using Machine Learning Techniques."**
Journal of Cybersecurity and Privacy 5(2), article 34, DOI 10.3390/jcp5020034.
Numbers: Random Forest 97.2 percent accuracy, DBSCAN 91.06 percent accuracy with a false
positive rate of 0.0821, latency under 100 ms, 95 percent of events within 500 ms, roughly
linear scaling to 500 events per second.
**The gap:** this work improves the quality of alerts that do fire. You detect the absence of
telemetry that should have fired, which produces no alert at all and therefore no false positive
to measure.

**De Ramos and Esponilla (2022). "Cybersecurity Program for Philippine Higher Education
Institutions."** IJERE 11(3), pp. 1198-1209, DOI 10.11591/ijere.v11i3.22863, Scopus-indexed.
Qualitative multiple-case study of Philippine State Universities and Colleges.
**The gap:** it establishes the local need and the beneficiary context. It is not technical
precedent. Say that difference yourself before a panelist says it for you.

**Yuhong, Zhuo, Monreal (2023). "Design of the Network Security Architecture for Smart Campus in
the Philippines."** Journal of Knowledge Learning and Science Technology 2(1), pp. 26-34,
DOI 10.60087/mrb0hh55. Indexing status of the venue is `(unverified)`.
**The gap:** a design-level architecture proposal, no examination of whether configuration
changes degrade the telemetry that intrusion detection depends on.

### 3.13 T1's weakest points, and the honest answer to each

| Objection | Honest answer |
|---|---|
| "You restore the same snapshot and run the same script. Nothing can vary. The statistics are decoration." | That is exactly why the control-versus-control experiment runs first and why both outcomes are declared in advance. If the variance floor is near zero, I report that the statistical layer is justified only in production, and I say so without softening it. |
| "67 hours of runs. Can you actually finish?" | It is achievable overnight and across weekends only if the harness is fully unattended. That is the hard constraint, and it is why the two-week feasibility spike measures real wall clock before I commit. If the projection exceeds the time available, I switch topics. |
| "Where do the labels come from?" | Two-tier labeling. Positive class is event types the change verifiably removed, because I caused the removal. Negative class is everything else in the pre-change profile. |
| "Are your 16 hardening changes real controls?" | Each is pinned to a specific CIS Benchmark or DISA STIG control ID, and the addendum lists all 16 with their IDs. **See Section 3.14 before answering this one.** |
| "If you disable SMBv1 and SMB1 events stop, is that a blind spot?" | No. The attack surface went with the telemetry, so the rule should be retired, not flagged. That is why my definition requires the technique to still be executable after the change. Those cases are my negative controls. |
| "The endpoint runs Sysmon. If you lose 4688, Sysmon Event ID 1 still records process creation. So nothing is blind." | Correct, and that is why the impact score includes a compensating-source check. A lost event type with a redundant source scores near zero. No comparable tool does that check. |
| "Your profile counts event-type rates. What about a change that empties a field instead of removing an event?" | The unit of analysis is (event type, required field present), not event type alone, so field-level degradation is measurable. Content-level changes that alter neither are outside scope and I say so. |
| "Real hardening is applied as a whole baseline, not one setting at a time." | Isolation is required for attribution, so main effects are what I measure. Interaction effects are named as a limitation, and I add one condition where the full baseline is applied at once, compared against the same pre-change profile. |
| "Patching is hardening. Your lab disables Windows Update." | True, and it is a stated scope limit. Patch-induced telemetry change is the same phenomenon and is the strongest generalization of the method, named as future work. |
| "Is this just a script that diffs two log files?" | The contribution is not the subtraction. It is the variance model, the significance testing with multiple-comparison correction, and the graph traversal that converts a statistical finding into a ranked security impact. |
| "What if a hardening change produces no telemetry difference?" | That is a valid finding and it gets reported. Not every hardening change costs visibility, and knowing which ones are free is useful. |

### 3.14 The correction you carry into the room

Read this before you defend T1. It was found on 2026-08-20 and it changes what you say in your
opening.

**What was wrong.** Four items in the change catalogue in
[lab/blueprint.md](../lab/blueprint.md) section 8 are the opposite of what the benchmarks
require. Verified against the benchmarks:

| Catalogue item | What the benchmark actually requires |
|---|---|
| 1. Disable Audit Process Creation | CIS requires it set to include Success. Level 1. Numbered 17.3.1 or 17.3.2 depending on version. |
| 2. Disable `ProcessCreationIncludeCmdLine_Enabled` | CIS requires Enabled. Level 1. 18.9.3.1, or 18.8.3.1 in some versions. |
| 3. Disable PowerShell ScriptBlock logging | DISA STIG WN10-CC-000326 / V-220860, CAT II, requires Enabled. |
| 4. Disable PowerShell Module logging | Same family. Benchmarks require enabling it. Exact ID `(unverified)`. |

Turning audit logging off is de-hardening, not hardening. Item 15 (narrow the Sysmon config) is
genuine security-tool hardening but has no CIS or DISA control, so it cannot be called
benchmark-drawn.

**What is not wrong.** Nothing in the submitted proposal names a specific control, event ID, or
setting. The catalogue exists only in the blueprint, which was never submitted. The only
sentences at risk are the two that say the 16 changes are drawn from CIS Benchmarks and DISA
STIGs (Objective 4 and Scale of the Experiment). Those stay true once the catalogue is
corrected, and the count stays at 16. **The title, the five problems, the five objectives, and
the five modules are all unchanged.**

**The one sentence a hostile reader can use.** Module 5 says the system provides "a ground-truth
injection facility that deliberately disables known detections through controlled hardening
changes." The answer: the loss is induced deliberately so the ground truth is known, and every
inducing change must be a real benchmark control where the technique is still executable.

**Your opening, if the panel picks T1.** Three sentences, calm, then move on.

> "One correction before I begin. While preparing, I checked my planned hardening changes
> against the actual CIS and DISA controls and found that four of them were the reverse of what
> the benchmarks require. I have replaced those and tightened my definition of a blind spot,
> which now requires that the attack is still possible after the change, not just that the
> telemetry disappeared. The title, the problems, and the objectives are unchanged, and the
> corrected catalogue is in the addendum I handed out."

**If asked why it was not caught before submission.** One sentence, no apology past it: the
catalogue was engineering judgment recorded in a working file and marked unverified, and
verifying it was already a logged open question.

**The artifact to bring.** One page, 16 rows, four columns: change, control ID, class (B or C),
expected telemetry effect. That page answers the catalogue question, the SMBv1 question, and the
"are these real controls" question at the same time.

---

## 4. T2 in full: Severity Inversion in the Wazuh Ruleset

**Full title.** Automated Detection of Severity Inversion in the Wazuh Default Ruleset Using
Parent-Child Dependency-Graph Analysis and Topological Consistency Scoring.

Source: [thesis/T2/proposal.txt](../thesis/T2/proposal.txt).

### 4.1 The one-paragraph version

A Wazuh rule can declare that it depends on another rule, using `if_sid` or `if_matched_sid`.
So the ruleset is a directed graph, not a flat list. Severity levels are assigned by hand, one
rule at a time, by people who cannot see the whole graph. A rule can therefore end up at a
severity that makes no sense given its ancestors, which means a serious alert is never escalated
to a human. This system builds the parent-child graph, propagates expected severity bounds along
it, evaluates a formal consistency rule at every vertex, classifies each violation, scores it,
and produces a ranked report.

### 4.2 Threat model

- **Primary asset:** the information held on the monitored systems, and the business processes
  that depend on it.
- **Control at risk:** alert triage and escalation. The rule fires correctly, so DE.CM works.
  The failure is downstream, in how the alert is routed to a human.
- **Threat actor:** any intruder whose activity produces an alert graded too low to be read.
- **Mechanism:** severity decides whether an alert is written silently to storage, put in a
  queue, escalated, or sent out of hours. A wrong grade means the alert exists and nobody
  sees it.
- **Impact:** the organization has the appearance of coverage without the substance.
- **Scarce resource, not an asset:** analyst attention. Analysts receive more alerts than they
  can read, which is the documented condition called alert fatigue, and severity is what
  allocates that attention.

### 4.3 Why the current process misses it

Existing Wazuh validation checks three things: that rule files match the schema and load, that
no two rules claim the same ID, and, through `wazuh-logtest`, which rule matches one sample log
line. None of those looks at severity at all. To check severity coherence by hand you would open
the rule file, find the rule, read its declared parent, open a different file to find that
parent, compare levels, and repeat along the whole ancestor chain, across several thousand
rules. No engineer does this. So inconsistencies are found by accident, usually when an alert
that should have been escalated arrives too low to trigger notification.

### 4.4 Problems and objectives, paired

| # | Problem | Objective |
|---|---|---|
| 1 | Levels are assigned manually per rule, nothing verifies coherence with the rules they depend on | Build a formal severity-consistency predicate plus a severity-bound propagation algorithm that infers the valid range for each rule |
| 2 | Dependencies form a multi-level graph, so a defect can originate several hops away and an immediate-parent check cannot find it | Build the directed parent-child graph with topological ordering, explicit cycle handling, and orphan handling, enabling multi-hop analysis |
| 3 | Manual auditing does not scale to several thousand rules, so the true defect count is unknown | Automate across the complete ruleset and measure runtime, throughput, and analyzable coverage against a naive flat-scan baseline |
| 4 | Existing tooling covers schema, duplicate IDs, single-input matching, and structure, but not severity | Build topological consistency scoring that assigns a severity-inversion score and produces a ranked report with dependency subgraphs |
| 5 | No formal criterion separates a deliberate escalation from a genuine defect | Formulate a taxonomy that separates the two and evaluate classification accuracy with precision, recall, and F1 against a manually labeled subset and a seeded-defect benchmark |

### 4.5 The five modules

1. **Rule Set Parsing and Normalization.** Walks the rule directory, parses each XML file,
   extracts rule ID, level, dependency declarations, groups, description, override attributes.
   Records unparsed files instead of stopping, and reports analyzable coverage as an explicit
   number.
2. **Dependency Graph Construction.** Each rule becomes a vertex, each dependency becomes an
   edge. Computes topological order with Kahn's algorithm, finds cycles with Tarjan's algorithm
   and condenses each cycle to one component so ordering stays well defined, and classifies
   vertices as root, intermediate, leaf, or orphaned.
3. **Severity Propagation and Consistency Analysis.** The core. Works in topological order,
   propagates inferred severity bounds forward from ancestors and backward from descendants,
   evaluates the consistency predicate at each vertex, records every violation with the path
   that produced it. Also implements the flat-scan baseline.
4. **Taxonomy Classification and Scoring.** Separates legitimate escalation (a low-severity
   general classifier giving rise to a high-severity specific child) from genuine defects such
   as unreachable high-severity descendants and silent de-escalation along a chain. Scores each
   by the size of the level discrepancy, the depth and length of the chain, and the number of
   descendants implicated. Ranks by score.
5. **Evaluation, Reporting, and Visualization.** Renders the ranked report and the dependency
   subgraph for each finding, exports machine-readable output for a CI pipeline, and holds the
   seeded-defect injection facility. Computes precision, recall, F1 for the proposed method and
   the baseline, plus runtime, throughput, and analyzable coverage.

### 4.6 Evaluation

- **Baseline:** naive flat scan. Compare each rule only against its immediate parent. This is
  exactly the comparison a human would do by hand, which makes it a fair and meaningful
  baseline.
- **Ground truth, two sources:** a manually labeled subset that you create, and a seeded-defect
  benchmark in which you inject known inversions and measure how many are recovered.
- **Measures:** precision, recall, F1, runtime, throughput, analyzable coverage.

### 4.7 Prior work and the gap you fill

**Tyagi. "Static Quality Assessment of Sigma Detection Rules."** SSRN abstract ID 6823718, tool
named sigmalint, evaluated on the SigmaHQ corpus of 3,132 rules at pinned commit 994da16. It is
a preprint; peer-review status is `(unverified)`.
Numbers: every SigmaHQ rule passes the validity gate, corpus mean static-quality score 99.18 out
of 100, two rule IDs (META004 and FP003) account for 89.8 percent of all findings, top three
reach 93.2 percent, and a seeded-defect benchmark with nine mutation operators gives 0.993 mean
target-rule recall across 450 in-scope mutations.
**The gap:** sigmalint treats rules largely as independent units and scores redundancy pairwise.
You target the dependency graph and multi-hop severity propagation, a defect class that a
per-rule or pairwise scorer structurally cannot find. Position yourself as graph-aware severity
consistency analysis, not as another flat linter.

**Uetz et al. (2024), AMIDES.** Same paper as in T1. Numbers repeat: 292 process-creation Sigma
rules analyzed, 110 (38 percent) fully evadable, 19 (7 percent) partially, and process-creation
rules were 41 percent of all rules at the time of analysis.
**The gap:** they target evasion of matching logic with a live machine-learning system. You
target severity coherence with offline static graph analysis, a defect that shows up even when
the rule matches perfectly.

**Saavedra and Ferreira (2022). "GLITCH: Automated Polyglot Security Smell Detection in
Infrastructure as Code."** ASE '22, DOI 10.1145/3551349.3556945. Parses Ansible, Chef, Docker,
Puppet, and Terraform into one intermediate representation, then runs rule-based static checks.
**The gap:** GLITCH finds local, mostly single-file smells such as hard-coded secrets, using
pattern matching. You analyze a cross-file directed dependency graph and reason about an ordinal
property that must stay consistent along multi-hop chains, which needs topological ordering and
bound propagation, not pattern matching.

**Miranda, Tayag, Canlas (2025). "Cybersecurity Skills in New Graduates: A Philippine
Perspective."** IJAAS 14(4), pp. 1217-1228, DOI 10.11591/ijaas.v14.i4.pp1217-1228.
**The gap:** it evidences the Philippine expertise shortage that makes manual auditing
structurally impossible for local SOCs. It measures the human capital gap and proposes no
tooling. You supply the tool.

**De Ramos and Esponilla (2022).** As in T1. Local setting and need, not technical precedent.

### 4.8 T2's weakest points, and the honest answer to each

| Objection | Honest answer |
|---|---|
| "You create your own ground truth. Did you grade your own homework?" | This is the real weakness and I will not hide it. Two mitigations: a seeded-defect benchmark where the truth is known because I injected it, and, if the panel requires it, a second annotator with a reported inter-rater agreement statistic. |
| "Is a severity inversion actually a bug, or is it intentional design?" | That is exactly why Objective 5 exists. The taxonomy separates deliberate escalation from genuine defect. Without that taxonomy the findings cannot be counted honestly. |
| "Is this hard enough for a thesis? It sounds like a linter." | The algorithmic content is the graph work: topological ordering, cycle condensation, bidirectional bound propagation, and a formal consistency predicate. A flat linter is the baseline I compare against, not the contribution. |
| "How many defects will you find? What if the answer is zero?" | Unknown before running it, and I will report the real number. Zero is a publishable result: it would mean the Wazuh ruleset is severity-coherent, which nobody has verified before. |
| "Why Wazuh?" | Because its rules declare parent dependencies, which creates the graph the method needs, and because it is free, which makes it the platform actually used by schools, small businesses, and public agencies in the Philippines. |

---

## 5. T3 in full: Analytic-Robustness Scoring

**Full title.** Automated Analytic-Robustness Scoring of Sigma and Wazuh Detection Rules Using a
Rule-Feature Dependency Model Based on the Summiting the Pyramid Methodology.

Source: [thesis/T3/proposal.txt](../thesis/T3/proposal.txt).

### 5.1 The one-paragraph version

Coverage asks whether a technique is detected at all. Robustness asks how hard it is to evade
that detection. A rule keyed to a file name dies when the attacker renames the file. A rule
keyed to process behaviour survives. Coverage reports treat both as equal, so they overstate how
well defended an organization is. This system parses Sigma and Wazuh rules, walks the Boolean
condition tree to find which fields the rule genuinely depends on, maps each field to a
robustness level under the Summiting the Pyramid methodology, computes a per-rule score using
the weakest required observable, aggregates to per-technique scores, and names the specific
field that limits each rule along with a suggested replacement.

### 5.2 Threat model

- **Primary asset:** the information held on the monitored systems, and the business processes
  that depend on it.
- **Control at risk:** the detection rules themselves. What is measured is the durability of the
  control, not whether it exists.
- **Threat actor:** an intruder who evades a brittle rule at negligible cost, for example by
  renaming a file.
- **Mechanism:** the rule depends on an observable the attacker can change for free, so the
  control fails on first contact while still counting as coverage.
- **Impact:** defensive investment goes to the wrong place, because a technique marked covered
  is defended by a rule that costs nothing to bypass.
- **Governance angle:** posture reporting to management, auditors, and regulators is built on
  coverage figures. Under NIST CSF 2.0 that reporting sits in the GOVERN function. Inaccurate
  coverage figures make governance decisions unsound. Truthful reporting is an outcome, not an
  asset, so do not call it one.

### 5.3 Why the current process misses it

Robustness today is a human opinion. An engineer reads the rule, decides whether an attacker
could evade it, and that opinion is never written down, never on a defined scale, and not
reviewable. The Summiting the Pyramid methodology gives a defined procedure, but it is applied
by hand, one analytic at a time. Rule linters check schema, metadata, and ATT&CK mapping form.
Test frameworks check that a rule matches malicious samples and not benign ones. None of them
measure durability against an attacker who changes the observable.

### 5.4 Problems and objectives, paired

| # | Problem | Objective |
|---|---|---|
| 1 | Robustness is assessed manually and subjectively, so assessments differ between engineers and cannot be reproduced | Build a rule-feature dependency model that parses rules and extracts, by traversing the Boolean condition structure, the fields each rule truly depends on |
| 2 | Applying the published methodology by hand does not scale to several thousand rules, so most rules carry no assessment | Automate the assignment of each observable to its STP level and the computation of a per-rule score |
| 3 | Coverage reporting counts a technique as covered regardless of how evadable the covering rule is | Aggregate per-rule scores into per-technique measures that qualify coverage |
| 4 | Engineers get no indication of which field makes a rule brittle, so no actionable guidance | Build a recommendation component that names the limiting field and proposes higher-level substitutions from the same event schema |
| 5 | No automated method can be validated against an authoritative reference, so accuracy cannot be measured | Evaluate agreement with the manually assigned STP annotations published in the Sigma corpus, using classification accuracy and Cohen's kappa, and report analyzable coverage |

### 5.5 The five modules

1. **Rule Ingestion and Parsing.** Reads Sigma YAML and Wazuh XML, normalizes both into one
   structure of metadata, log source, detection definitions, and condition expression. Handles
   field modifiers, wildcards, and value lists. Records unparsable rules instead of stopping.
2. **Feature Dependency Extraction.** Builds the Boolean condition tree and walks it to find
   which fields matching genuinely depends on. Separates required (conjunctive) terms from
   alternatives (disjunctive) and negations, which must not be scored as requirements. Resolves
   the log source declaration to fix the event schema, because the same field name can mean
   different things under different schemas.
3. **Robustness Mapping and Scoring.** The core. A knowledge base maps observables to STP host
   and network levels. Each rule is scored under a weakest-dependency rule, because a rule is
   only as durable as the weakest observable it requires. Unresolvable observables are handled
   explicitly. Scores roll up to technique and tactic level, and the limiting observable is
   recorded.
4. **Recommendation and Substitution.** For each rule limited by a low-level observable,
   searches the same event schema for higher-level fields that could express the same detection
   intent, and presents them with the score improvement each would give. It proposes, it does
   not apply. The engineering judgment stays with the analyst.
5. **Validation, Reporting, and Visualization.** Ranked report, per-technique summary, ATT&CK
   Navigator layer shaded by robustness instead of by presence. Validation mode computes
   accuracy, Cohen's kappa, and a confusion matrix against the annotated reference subset, plus
   analyzable coverage.

### 5.6 The problem you already found, and how to handle it

**This is the single most important thing to know about T3.**

On 2026-08-19 you shallow-cloned `SigmaHQ/sigma` at commit
`da9bb07d642a2826e89702445d32c795209ec108` and counted the rules carrying a real STP annotation.
The STP annotation is a Sigma tag of the form `stp.<level>` inside a rule's `tags:` list.

**Result: 6 rules out of 3,783. That is 0.16 percent.**

| Tag | Count |
|---|---|
| stp.1u | 3 |
| stp.1k | 1 |
| stp.2a | 1 |
| stp.4u | 1 |

Method note worth saying out loud if asked: a naive `grep stp.` returns 19 files, but 13 are
false hits on `cmstp.exe` and `chrmstp.exe`, which many rules mention. The real count needs the
tag line `- stp.<digit>`, not the substring.

**What it means.** Objective 5 as written cannot be executed. Cohen's kappa across 6 data points
spread over 4 different levels is not a meaningful agreement statistic. Full evidence is in
[docs/OPEN-QUESTIONS.md](OPEN-QUESTIONS.md), Answered section, and the consequence is recorded
in [docs/DECISIONS.md](DECISIONS.md).

**What to say if the panel picks T3.** Do not hide this and do not let a panelist find it first.
Say it yourself, early, in this shape:

> "Objective 5 as written cannot run. I verified this myself on 19 August. SigmaHQ carries STP
> tags on 6 of 3,783 rules, 0.16 percent. Cohen's kappa on 6 points across 4 levels is not
> meaningful. So Objective 5 needs redesign before this topic proceeds. The realistic option is
> to build the reference standard myself, with a second annotator on a sampled subset, and
> report inter-rater agreement on that. That turns part of the study manual and it weakens the
> claim that I validate against someone else's labels, so I want the panel to know the cost
> before choosing this title."

Finding this before the defense and reporting it is a strength, not a weakness. It shows you
verify your own assumptions. Present it that way, plainly, without apology.

### 5.7 Prior work and the gap you fill

**Uetz et al. (2024), AMIDES.** Same paper. For T3 the load-bearing number is that about half of
the roughly 300 analyzed Windows process-creation Sigma rules were evadable (110 fully at 38
percent, 19 partially at 7 percent, of 292). AMIDES caught exactly 70 percent of evasions (358
true positives, 154 false negatives) with zero false alerts against 74,431,740 true negatives,
roughly 145,000 times as many benign as malicious events.
**The gap:** AMIDES is a runtime machine-learning detector that needs live benign events and a
running SIEM. You score evasion resistance offline, from the rule's condition logic alone, with
no logs and no training data.

**Virkud, Inam, Riddle, Liu, Wang, Bates (2024). "How Does Endpoint Detection Use the MITRE
ATT&CK Framework?"** USENIX Security 24, ACM DL DOI 10.5555/3698900.3699118.
Numbers: commercial products cover 48 to 55 percent of the 191 techniques in enterprise ATT&CK
v11, Sigma's crowdsourced coverage was higher at 79 percent, 53 techniques (27.7 percent) were
not implemented in any commercial product, and coverage falls to 25 to 26 percent once low- and
medium-risk rules are filtered out.
**The gap:** they critique coverage and analyze labeling consistency, but stop short of a
per-rule reproducible robustness score. You supply that ordinal measure and a Navigator layer
shaded by robustness.

**Tyagi, sigmalint.** Same as in T2, with the same figures.
**The gap:** sigmalint scores correctness, false-positive risk, and metadata completeness. It
does not score analytic robustness and does not model the condition tree to find which
observables matching truly depends on. You fill exactly that dimension and add STP-based
weakest-dependency aggregation.

**De Ramos and Esponilla (2022)** and **Miranda et al. (2025).** Local Philippine context, as
described above.

### 5.8 T3's weakest points, and the honest answer to each

| Objection | Honest answer |
|---|---|
| "How will you validate your scores?" | As written, against the STP-annotated subset in SigmaHQ. I verified that subset is 6 rules of 3,783, so that objective needs redesign. See Section 5.6 for the full answer. |
| "You are just re-implementing someone else's methodology." | The methodology is published, and its authors named automation as outstanding work. The contribution is the dependency model that decides which observables a rule truly requires, which is the hard part, plus the aggregation rule and the substitution recommendations. |
| "Is a static score meaningful without testing against a real attacker?" | No, and I say so. The score measures the dependency structure of the rule, not empirical evasion success. Empirical validation against live evasions is what AMIDES does, and it is named as future work, not claimed here. |
| "How do you handle a field you cannot resolve?" | It is recorded as unscorable and counted in analyzable coverage, which I report as an explicit number instead of quietly dropping those rules. |

---

## 6. Numbers to memorize

| Number | Meaning | Where it comes from |
|---|---|---|
| 16 / 3 / 3 / 5 / 101 | T1: changes, pre repeats, post repeats, controls, total runs | T1 proposal, Objective 4 and Project Context |
| 180 s / 120 s | T1 settle after boot, drain after the attack suite | lab/blueprint.md section 6 |
| about 67 hours | T1 projected total wall clock `(unverified)` | lab/blueprint.md section 6 |
| 292 / 110 (38%) / 19 (7%) | Sigma process-creation rules analyzed, fully evadable, partially evadable | Uetz et al. 2024 |
| 70% / 358 / 154 / 512 | AMIDES evasion detection rate and counts | Uetz et al. 2024 |
| 74.4 million | benign events AMIDES ran against with zero false alerts | Uetz et al. 2024 |
| 48-55% vs 79% | commercial vs Sigma ATT&CK coverage, v11, 191 techniques | Virkud et al. 2024 |
| 25-26% | coverage after filtering low- and medium-risk rules | Virkud et al. 2024 |
| 3,132 rules at commit 994da16 | sigmalint's pinned SigmaHQ corpus | Tyagi |
| 99.18 / 100 | sigmalint corpus mean quality score | Tyagi |
| 6 of 3,783 (0.16%) | SigmaHQ rules carrying an STP tag, measured by you | docs/OPEN-QUESTIONS.md, commit da9bb07 |
| 97.2% / 91.06% / 0.0821 | Gherabi's Random Forest accuracy, DBSCAN accuracy, DBSCAN false positive rate | Gherabi 2025 |

---

## 7. Question bank

Short answers. Say the short answer first, then stop. Add detail only if they ask again.

### About the topic in general

**Q. What is your thesis in one sentence?**
Pick the chosen title and give the one-paragraph version from Section 3.1, 4.1, or 5.1, cut to
one sentence.

**Q. Why is this computer science and not IT administration?**
Because the contribution is an algorithm. For T1 it is variance modeling plus hypothesis testing
with multiple-comparison correction plus graph traversal. For T2 it is topological ordering,
cycle condensation, and bidirectional bound propagation. For T3 it is Boolean condition-tree
traversal for dependency extraction and ordinal classification. The configuration work is the
setting, not the contribution.

**Q. Who will use this?**
Detection engineers as the primary operator, security or systems engineers, SOC analysts tier 1
and 2, and the SOC manager for prioritization. Each proposal has a target-user table. Know the
top two.

**Q. Why does this matter in the Philippines?**
Because the platforms involved are free and open source, which is what schools, small and medium
enterprises, and public agencies here can actually afford. Two local studies establish the
setting: De Ramos and Esponilla (2022) on the readiness of State Universities and Colleges, and
Miranda et al. (2025) on the local cybersecurity skills shortage. Both establish need, not
technical precedent, and I say that difference myself.

**Q. What is your research design?**
Developmental and experimental. Developmental because the output is a working system built
through requirements, design, implementation, and evaluation. Experimental because the finished
system is compared against a named baseline under controlled conditions, using outcome measures
declared before evaluation begins.

**Q. What is your baseline?**
T1: naive event-count differencing. T2: naive flat scan against the immediate parent only.
T3: the manually assigned STP annotations as the reference standard. Naming a baseline is what
makes the study experimental rather than a demonstration.

**Q. How will you know you failed?**
Say the pre-declared failure condition for the chosen topic. T1: if the coefficient of variation
across control runs is near zero, the statistical layer buys nothing in the lab and I report
that. T2: if the taxonomy cannot separate legitimate escalation from defect, the findings cannot
be counted honestly. T3: if the reference standard is too small, Objective 5 cannot run, which
I already measured and disclosed.

### About scope and feasibility

**Q. Can you finish this by December?**
The Gantt runs August to December 2026. Data collection must start no later than end of
September 2026. For T1 the binding constraint is that the capture harness must be fully
unattended, and a two-week feasibility spike measures the real wall clock before I commit. For
T2 and T3 there is no lab and no data collection window, so the schedule is easier.

**Q. What have you built so far?**
Be exact and do not inflate. Phase 0 of the runbook is complete: host readiness verified, 64 GB
RAM, Ryzen 7950X, VMware Workstation 17.5.1, Python 3.13.14, ISOs staged, `vmrun` confirmed
working, and the Windows hypervisor disabled so VMware runs directly on the hardware. No code
has been written yet. The repository, the runbook, the decision log, and the open-questions
list are live and public at https://github.com/EASolutions00/detection-hardening-lab.

**Q. Why is your repository public before the defense?**
The professor confirmed there is no intellectual property rule against it and no
similarity-check problem, because a match between the final paper and my own public repository
is not treated as an issue. It is recorded in DECISIONS.md with the reason and the cost if
wrong.

**Q. What happens if your primary topic fails its gate?**
I switch. That is why the gate exists and why it runs in week 2, not in October. The second
choice between T2 and T3 is not settled yet, and I would rather say that than invent a ranking.

### T1 specific

**Q. Why 101 runs? Why not fewer?**
16 changes times 3 pre-change plus 3 post-change repeats is 96, plus 5 control runs is 101. The
3 repeats put within-phase variation into the comparison instead of assuming it is zero. The 5
controls build the variance model for each event type.

**Q. Why not just read the configuration to know what telemetry is lost?**
Because configuration does not tell you what the machine actually emits under real activity.
The mapping from setting to emitted event type is not documented anywhere in full, and it
depends on the workload. This measures what is emitted rather than predicting it.

**Q. Why 180 seconds of settle and 120 seconds of drain?**
Settle lets the boot-time event storm finish, so it is not counted inside the window. Drain
covers agent buffering and the manager's write to `archives.json`, which are not instant.
Cutting the window at the end of the attack suite loses tail events. Both figures are
`(unverified)` engineering judgment and will be checked during the spike.

**Q. Why fence the window with events instead of the host clock?**
Because host clock and guest clock drift, and the event you care about is timestamped inside the
guest. A uniquely named command produces a distinctive Sysmon Event ID 1 at the start and end,
so the window boundary is defined inside the telemetry itself.

**Q. What is `logall_json` and why does it matter?**
It is the Wazuh setting that stores every received event, not only the ones that triggered a
rule. T1's unit of analysis is the event type emitted, not the alert fired, so without it the
study cannot be done. Wazuh's documentation warns that it costs storage and performance, which
is why SIEM-01 is sized at 16 GB and 200 GB.

**Q. Why must VMs not run from the E: drive?**
E: is a hard disk. Its seek latency jitter changes process scheduling, which changes event
ordering and counts. That noise would land directly in the coefficient of variation figure the
statistical justification rests on. I would be measuring my disk, not my hypothesis. VMs run on
F:, which is NVMe.

**Q. Why disconnect NAT during captures?**
Because Windows Update, Defender cloud lookups, connected-user-experience telemetry, certificate
revocation checks, and NTP all fire on their own schedules. Every one of them injects variance
into the exact window being measured.

**Q. Why pin versions?**
A Wazuh, Sysmon, Atomic Red Team, or Windows build change mid-experiment makes earlier runs not
comparable to later ones. Every earlier run would have to be discarded. Versions and hashes are
recorded before the golden snapshot is taken.

**Q. Is one endpoint enough?**
For the stated claim, yes, because the claim is about the relationship between a configuration
change and the telemetry that host emits. More hosts and a second operating system are Tier B in
the blueprint and are added only if the spike shows there is time. Generalization across
environments is named as future work.

### T2 specific

**Q. What is severity inversion, exactly?**
A rule whose declared severity level is not consistent with the levels of the rules it depends
on, in a way that makes a serious alert arrive too low to be escalated.

**Q. Why is an immediate-parent check not enough?**
Because dependencies form a multi-level graph. A defect can originate several hops away from
where it becomes observable. A check limited to a rule and its immediate parent is structurally
incapable of finding that class of defect. That is why the flat scan is the baseline.

**Q. What do you do about cycles in the graph?**
A strict topological order does not exist when cycles are present. Tarjan's algorithm finds the
strongly connected components, and each cycle is condensed to one component so that ordering and
bound propagation stay well defined.

**Q. What is your consistency predicate?**
A formal statement of the range of severity levels a rule may hold given the bounds inferred
from its ancestors and descendants. A rule violates it when its declared level falls outside the
inferred bounds. The exact form is part of Objective 1 and is defined during design.

**Q. How do you avoid calling deliberate design a defect?**
The taxonomy in Objective 5. A low-severity general classifying rule that gives rise to a
high-severity specific child is legitimate escalation, not a defect. Genuine defect categories
include unreachable high-severity descendants and silent de-escalation along a chain.

### T3 specific

**Q. What is analytic robustness?**
How much effort an attacker must spend to make a rule stop working. It is different from
coverage, which only asks whether a rule exists.

**Q. Why the weakest observable and not an average?**
Because a rule only fires when all its required conditions match. If one required field is
trivially changed, the attacker changes that one field and the rule fails, no matter how strong
the other fields are. A rule is only as durable as the weakest observable it requires.

**Q. Why does negation matter in the condition tree?**
Because a field mentioned under a negation or inside an alternative branch does not constrain
matching in the same way as a field the rule requires. Scoring every mentioned field the same
way would produce wrong scores. That is why the system builds a condition tree instead of
listing field names.

**Q. How will you validate?**
See Section 5.6. Say the 6-of-3,783 finding yourself, then state the redesign option.

### Methodology and statistics

**Q. Why chi-square and Poisson rate ratio together?**
Chi-square answers whether the difference is more than chance. The Poisson rate ratio answers
how big the change is, with confidence bounds, which is the interpretable effect size for count
data. Significance without effect size is not actionable.

**Q. Why the Benjamini-Hochberg correction?**
Because hundreds of event types are tested at once, and at a 5 percent threshold some will look
significant by chance alone. Benjamini-Hochberg controls the share of the findings that are
false, which is the right target here because the output is a ranked list for a human to work
through, not a single yes-or-no decision.

**Q. Why Cohen's kappa instead of plain accuracy?**
Because plain accuracy is inflated when the labels are unevenly distributed. Kappa corrects for
the agreement that would happen by chance alone.

**Q. Why precision and recall instead of accuracy?**
Because the interesting class is rare. Accuracy can be high while the system misses almost every
real case. Precision, recall, and F1 describe the behavior on the class that matters.

### Ethics and safety

**Q. Is running attack simulations legal and safe?**
Yes, in this setting. Atomic Red Team runs inside an isolated lab I own, on host-only virtual
networks with internet access disconnected during captures. Nothing runs against a third party.
Every host is restored from a snapshot after each run.

**Q. Is there personal data involved?**
No. The telemetry comes from lab virtual machines with no real users and no production data.

---

## 8. Known weak spots in your own documents

Fix what you can before the defense. Disclose the rest before a panelist finds it.

1. **The 16 hardening changes are not all pinned to a control ID, and four of them are the
   reverse of what the benchmarks require.** Full detail and the verified control IDs are in
   Section 3.14 and in OPEN-QUESTIONS.md item 1. **This is the highest-value fix available to
   you right now, and it is offline work.** Rebuild the catalogue: drop items 1 to 4, relabel
   item 15, add real controls where the technique survives the change, and tag every row with a
   control ID and a class. Keep the count at 16 so the submitted proposal text stays true.
2. **Nested virtualization for Credential Guard is untested** on this host (Zen 4 plus
   Workstation 17.5.1). That is hardening change number 8. If it does not work, drop it and
   substitute another change from the catalogue. Low damage, but test it early. Item 2 in
   OPEN-QUESTIONS.md.
3. **Indexer heap and archive growth under `logall_json` are estimated, not measured.** The
   16 GB and 200 GB figures are judgment. If archives grow faster than expected, F: fills up
   mid-experiment. Item 3 in OPEN-QUESTIONS.md.
4. **The same source is dated differently in two proposals.** The Tyagi sigmalint paper appears
   as "(2026)" with "SSRN Working Paper 2025" in the T2 proposal, and as written 24 May 2026 and
   posted 5 June 2026 in the T3 proposal. Make the two entries agree before submission. A panel
   member who reads both will notice.
5. **Two proposals carry mojibake in an author name.** "Hackländer" appears as "Hackl?nder" and
   "João" as "Jo?o" in the proposal text files, and "Mapúa" as "Map?a". Fix the encoding before
   printing.
6. **No code exists yet.** Say it plainly if asked. The runbook, the decision log, and the
   open-questions list are the work product so far, and Phase 0 is verified complete.
7. **T3's Objective 5 is not executable as written.** Section 5.6. Disclose it first, always.

---

## 9. Current build status, in one honest paragraph

Phase 0 of the runbook is complete and verified on 2026-08-19: F: has 732 GB free, AMD SVM
virtualization is enabled in firmware, Python 3.13.14 is installed, VMware Workstation 17.5.1
build 23298084 matches the pinned version in the blueprint, `vmrun` works, and both ISOs are
staged (Ubuntu 24.04.4 LTS server and Windows 11 Enterprise Evaluation). The Windows hypervisor
was disabled with `bcdedit /set hypervisorlaunchtype off` and the host rebooted, so VMware now
runs directly on the hardware. That must stay off for the whole experiment, because changing it
mid-experiment changes timing and invalidates earlier runs. Phases 1 through 8 are not started.
No code has been written. Source: [docs/WORKLOG.md](WORKLOG.md) and [docs/DECISIONS.md](DECISIONS.md).

---

## 10. Which title to push for

**Critique.** The strongest objection to pushing T1 is that both of its hard requirements are
still unverified at the point of the defense. The variance floor is unmeasured, so you do not
know whether the headline result exists. The per-run wall clock is unmeasured, so you do not
know whether 101 runs fit in the calendar. On top of that, the fallback plan is weaker than the
documents say: T3 lost its reference standard on 19 August, and the second choice is officially
undecided. If the panel approves T1 and the spike fails in September, you are switching topics
with the data-collection deadline already passed.

**Steelman for the other side.** Argue for T2 instead. T2 is offline static analysis, needs no
lab, runs on a laptop, has no data-collection window, and cannot fail on wall clock. Its known
weakness, self-created ground truth, is fixable with a second annotator and a reported agreement
statistic. Choosing T2 would remove every schedule risk from the project in one step. The
evidence against this is that T2 produces the least new knowledge of the three: it audits one
vendor's ruleset for one property, and its result may be a small number of defects or none. T1
produces measurements that do not currently exist anywhere, and it is the only one of the three
that generates new data rather than analyzing files other people wrote. For a thesis judged on
contribution, that difference is real.

**Recommendation.** Push for T1, and say the gate out loud. Tell the panel that T1 is your
choice, that a two-week feasibility test measures the variance floor and the real wall clock,
and that you will switch if the numbers fail. Naming your own kill condition in the room is the
strongest position available to you, because it is the objection they were going to raise
anyway. If a panelist pushes back hard on feasibility, do not fight. Say that T2 is deliverable
with certainty and that you will take their direction. Do not present T3 as the safe fallback,
because as of 19 August it is not.

**Summary.** T1 first, with the gate disclosed. T2 as the honest deliverable-for-certain answer
if they push on schedule. T3 only with the Objective 5 problem stated first.

---

## 11. Checklist for the week before

- [ ] Rebuild the 16-change catalogue: control ID and class (B or C) on every row. Drop the four
      anti-hardening items. This is the highest-value item on the list. See Section 3.14.
- [ ] Print the one-page addendum from that table and bring copies.
- [ ] Tell the research professor about the correction before the defense, not during it.
- [ ] Rehearse the four-condition blind-spot definition in Section 3.8 until it is automatic.
- [ ] Make the Tyagi citation consistent between the T2 and T3 proposals.
- [ ] Fix the mojibake in author names in all three proposal files.
- [ ] Read every proposal out loud once. You will catch what your eye skips.
- [ ] Rehearse the three one-sentence answers (problem, method, measure) for all three titles.
- [ ] Rehearse the T3 disclosure in Section 5.6 word for word. It must sound calm, not defensive.
- [ ] Rehearse the T1 falsifiable claim in Section 3.10. Same reason.
- [ ] Memorize Section 6.
- [ ] Bring the one-slide deck: `thesis/topic-proposal-titles.pptx`. Descriptions are in the
      speaker notes.
- [ ] Bring the Topic Proposal Document, which is what you actually present.
- [ ] Know your own repository URL and what is in it, in case they ask to see the work.

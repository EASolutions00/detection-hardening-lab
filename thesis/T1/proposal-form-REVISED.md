# T1 Proposal (Research Topic Proposal Form)

**Revised version.** Incorporates the panel's comments and the changes listed in
`T1-REVISION-DRAFT.md`. The submitted version is preserved as `proposal-form.md`.

---

| Name of Student | Elijah Amorsolo |  |  |
|---|---|---|---|
| Student ID | OED20-0012616 | Program | BS Computer Science |

## Proposed Title

Identifying Hardening-Induced Detection Blind Spots Through Differential Analysis of
Pre- and Post-Hardening Security Event Telemetry

---

## Area of Investigation

### Field and Background of the Study

This study falls under cybersecurity, in the areas of security operations, detection
engineering, and security event telemetry analysis.

Organizations watch their systems for attack using a Security Information and Event
Management (SIEM) platform. The platform collects events from endpoints, servers, and
network devices, then tests each event against a library of detection rules. When a rule
matches, the platform raises an alert for an analyst. Open-source platforms such as Wazuh
have brought this capability within reach of small and medium enterprises.

Writing and maintaining those rules is now its own discipline, called detection
engineering. It treats a rule like code. Engineers derive a rule from attacker behavior,
put it in version control, test it, deploy it, monitor it, and retire it. They describe
attacker behavior using MITRE ATT&CK, a public catalogue of the tactics and techniques
observed in real intrusions. ATT&CK gives them a shared vocabulary for stating what they
can and cannot see, which they measure as detection coverage.

A separate and equally established practice is system hardening. Hardening reduces the
attack surface by changing configuration, guided by published baselines such as the Center
for Internet Security (CIS) Benchmarks and the Defense Information Systems Agency (DISA)
Security Technical Implementation Guides (STIGs). Typical measures disable legacy
protocols, restrict scripting interpreters, and remove unused services. Regulators
increasingly require a documented hardening program, so configuration change is routine
work.

The two practices are coupled, and that coupling is the subject of this study. A detection
rule never observes an attacker directly. It observes the events a system emits, and
configuration decides which events a system emits. Hardening changes configuration. A
change made to reduce exposure therefore also changes the evidence that detection depends
on. Practitioners recognise this in principle. They cannot reason about it in practice,
because a single enterprise endpoint can emit thousands of events an hour across hundreds
of distinct event types.

To test whether detections still work, the field uses adversary emulation: it reproduces
known attacker behavior safely and observes what the defenders detect. Open libraries such
as Atomic Red Team and MITRE Caldera supply scripted tests mapped to ATT&CK techniques.
Separately, computer science provides formal methods for deciding whether two streams of
observations differ meaningfully, including hypothesis testing for count data and
correction for multiple comparisons. This study sits where those two bodies of work meet.

### Algorithms to be Used

The system applies the following algorithms. Each is stated with the scope at which it
operates, because two of them are commonly applied at a scope that does not suit them. The
naive event-count differencing method is the experimental baseline against which the
combined approach is measured.

| Algorithm / Technique | Scope | Purpose in the System |
|---|---|---|
| Differential profile alignment over the union of event-type keys | Once per validation run | Aligns the pre-change and post-change frequency profiles across every event type seen in either one, inserting explicit zeros where a type occurs in only one profile. Produces the table on which all later tests operate. |
| Coefficient of variation and dispersion estimation from control runs | Once per monitored environment | Measures, for each event type, the mean rate, the coefficient of variation, and the dispersion parameter across repeated control runs in which nothing is changed. This is the empirical noise floor. |
| Chi-square test of homogeneity | Once per validation run, on the whole profile | Tests whether the distribution of events across all event types differs between the two phases. Acts as a single global gate before any per-event-type test runs. |
| Dispersion-aware rate ratio with confidence bounds | Once per event type | Estimates how much the rate of each event type changed, and whether that change is significant, using the dispersion measured from the control runs instead of assuming none. |
| Benjamini-Hochberg false discovery rate correction | Once per validation run, across all event types tested | Holds down the share of false findings that arises from testing several hundred event types at once. |
| Weighted graph traversal over the event-rule-technique dependency index | Once per event type classified as lost or reduced | Maps lost telemetry to the detection rules that read it and the ATT&CK techniques those rules cover, and computes the impact score used for ranking. |

Two of these assignments differ from common practice, and the reasons are stated here
rather than left implicit.

The chi-square test runs once on the whole profile, not separately on each event type.
Applied per event type it fails twice. The expected counts for rare security event types
often fall below the value at which the chi-square approximation stays valid, and the
resulting p value duplicates the one the rate ratio already gives for the same event type.
Applied once to the whole profile it answers a question nothing else answers: did the
emitted profile change at all.

The rate ratio uses a dispersion-aware model, not the Poisson model. Poisson assumes that
the variance of a count equals its mean. This study measures the variance of each event
type directly from the control runs, and it would be inconsistent to measure that quantity
and then use a test that assumes it away. Where the control runs show dispersion close to
one, the system falls back to the Poisson rate test, and the study reports that the
assumption was tested rather than presumed.

---

## Reasons for Choice of Project

### The Current Process

Today an engineer validates a hardening change in a way that looks only at configuration.

The engineer takes a required change from a compliance benchmark, a vulnerability finding,
or an internal directive. They apply it to a test group and promote it to production
through change management. Two checks follow. The first is a compliance check: a
configuration scanner or a manual registry and policy review confirms the setting is now in
force. The second is a functional regression test: the business applications are exercised
to confirm nothing broke.

Neither check looks at detection coverage. Where a detection-side check happens at all, it
is ad hoc. An engineer who happens to remember that a rule relates to the changed component
may re-run one or two adversary simulation tests against it. That depends entirely on
personal recall, and no organization applies it across the whole rule set.

In many organizations the only standing safeguard is a rule health report listing rules
that have not fired within a defined period. Teams consult these reports periodically
rather than in connection with a specific change, and they often ignore them. A rule that
has not fired looks identical whether no attack occurred or its data source disappeared.

The result is that no step in the existing process surfaces a loss of detection capability.
The change produces no error, no failed test, and no alert. The affected rule stays in the
rule set, stays enabled, and keeps appearing in coverage reports as an active control.
Teams usually discover the deficiency during an incident investigation, an annual detection
audit, or a red team engagement, long after the coverage was lost.

A preliminary trial early in the development phase will show that this is a property of
real systems rather than a theoretical concern. One hardening change will be applied to one
instrumented host, and the telemetry will be compared before and after under identical
scripted stimulus. An event type present before the change and absent after it will be
exhibited as direct evidence that the loss happens and produces no failure indication. This
gap in the current process is the condition the study addresses.

### Research Design

The study uses a developmental and experimental design.

It is developmental because its main output is working software, produced through
requirements definition, design, implementation, and evaluation.

It is experimental because the finished system is compared against a named baseline under
controlled conditions, using outcome measures declared before the evaluation begins. The
baseline is naive event-count differencing: an event type is reported as lost whenever its
post-change count falls below its pre-change count, with no model of variance and no test
of significance.

Control is established two ways. Every host is returned to a known state by virtual machine
snapshot restoration before every capture window, and an identical scripted adversary
simulation suite runs in each window. The applied configuration change is therefore the
only variable that differs between the pre-change and post-change phases. That condition is
not asserted but enforced. Every run is defined by an immutable manifest recording the
snapshot, the adversary emulation tests and their versions, the window duration, the number
of repetitions, the rule set version, and the statistical thresholds. Two runs are admitted
to comparison only when the hashes of their manifests match.

The declared outcome measures are precision, recall, F1 score, and false positive rate,
computed for the proposed algorithm and for the baseline against the same ground-truth set
of deliberately induced telemetry losses, together with the share of the event-type space
successfully analyzed.

### Statement of the Problems

1. Security hardening changes silently alter or remove the security event telemetry that
  existing detection rules depend on. This creates detection blind spots that produce no
  error, alert, or failure indication, so the security team never learns of them.

2. The prevailing verification procedure for a hardening change checks only configuration
  compliance and application function. No stage of the existing change process can
  determine whether detection coverage survived.

3. Manual before-and-after comparison of telemetry does not work at operational scale. The
  volume of events and the number of distinct event types exceed what an analyst can
  inspect and compare reliably.

4. Comparing raw event counts before and after a change produces too many false alarms.
  Normal operational variance from user activity, scheduled tasks, and patch cycles moves
  event volumes independently of any configuration change, which makes naive differencing
  unusable as a decision tool.

5. Even where a change in telemetry is identified, no quantitative measure links the
  affected event type to the detection rules and adversary techniques that depend on it.
  The security impact of the loss therefore cannot be assessed or prioritized for
  remediation.

### Objectives of the Study

**General Objective.** The study aims to design, develop, and evaluate a system that
automatically detects hardening-induced detection blind spots. The system compares
pre-change and post-change security event streams using differential analysis and
statistical significance testing, and quantifies the detection coverage lost to each
change.

### Specific Objectives

1. To design and implement a differential analysis algorithm that represents pre-change and
  post-change telemetry as normalized frequency profiles, and identifies event types that
  are absent or significantly reduced after a hardening change, exposing losses that
  currently produce no failure indication. (addresses Problem 1).

2. To build the algorithm into an automated validation workflow that captures baseline and
  post-change telemetry under controlled, repeatable conditions using scripted adversary
  simulation, so that coverage verification becomes an explicit and reproducible stage of
  the hardening change process. (addresses Problem 2).

3. To automate the comparison across the complete event-type space of the monitored
  environment, so that event volumes and event-type counts beyond the reach of manual
  inspection can be analyzed. (addresses Problem 3).

4. To distinguish genuine hardening-induced telemetry loss from normal operational variance,
  by (a) applying a chi-square test of homogeneity once to the complete event profile as a
  global gate, (b) applying a dispersion-aware rate-ratio test to each event type using the
  variance measured from 5 control runs, and (c) correcting for multiple comparisons with
  the Benjamini-Hochberg procedure; and to measure the resulting reduction in false
  positives against a naive event-count differencing baseline across 16 hardening changes
  drawn from the CIS Benchmarks and the DISA STIGs, with each capture phase repeated 3
  times. (addresses Problem 4).

5. To develop a blind-spot impact scoring and remediation component that maps each lost
  event type to its dependent detection rules and their ATT&CK techniques, ranks findings
  by the coverage each change costs, proposes the surviving sources and compensating
  controls that could restore that coverage, and closes a finding only after a
  re-validation run shows the remediation worked. (addresses Problem 5).

---

## Project Context

### Concept of the Proposed System

The system validates detection coverage by running a controlled experiment around a
hardening change. It does not inspect configuration state. It observes what the monitored
environment actually emits. It captures a profile of security event telemetry before the
change, captures a second profile after the change under identical stimulus, then
determines by statistical comparison which event types were lost or materially reduced.
Identical stimulus comes from running the same scripted adversary simulation suite in both
windows, so any difference between the profiles is attributable to the configuration change
rather than to different activity.

The core contribution is algorithmic. The system does not simply subtract one set of counts
from another. It aligns the two profiles, models the expected variance of each event type
from repeated control runs, and applies hypothesis testing with multiple-comparison
correction to decide which differences are real. It then traverses the dependency
relationship between event types, detection rules, and adversary techniques to turn a
statistical finding into a ranked statement of security impact.

The system is a server-side web application. It is not a desktop program and not a
standalone script. It installs once on a single server placed alongside the SIEM platform,
distributed as a set of containers. The analytical core is a Python package that also runs
from the command line without the web interface, and that headless mode executes the
experimental runs reported in this study, so every measurement comes from the same code a
deploying organization would run. The web interface is the operator's point of contact: the
operator defines a validation run through one form, watches its progress, and reads the
report in a browser.

**No software agent is installed on the monitored endpoints.** The endpoints of a monitored
environment already run the agent of the SIEM platform, which is how their events reach the
platform, and the system drives the experiment from the server side through that existing
channel. This choice is deliberate. Organizations resist a second endpoint agent, and
building one would consume development effort without adding to the contribution of the
study.

### Inputs, Preconditions and Outputs

The inputs fall into three classes, distinguished here because different parties supply
them at different times.

**A. Preconditions of the monitored environment.** These are established once, before any
validation run. The system cannot operate without them, and they are stated so the cost of
deployment is not understated.

| Precondition | Concrete form | Provided by |
|---|---|---|
| A SIEM platform with a programmatic interface | A Wazuh manager and indexer, agents enrolled on the target hosts, and credentials for the indexer API | The organization, as existing infrastructure. This system does not install a SIEM. |
| The ability to return a host to a known state | Target hosts as virtual machines under a hypervisor whose interface allows snapshot restoration | The organization's infrastructure team |
| The detection rule set in machine-readable form | Sigma rules in YAML, or Wazuh rules in XML. A Sigma rule declares its ATT&CK techniques inside the rule file, so the dependency index is built automatically. | The detection engineer, as a one-time export, refreshed when rules change |
| A library of adversary emulation tests | Atomic Red Team (Red Canary, MIT licence), executed through the Invoke-AtomicRedTeam framework | Distributed with the system |
| A measured noise baseline | The 5 control runs from which the dispersion model is derived. The system performs these itself, but they must finish before the first comparison. | The system, in Phase 0 |
| Written authorization to run adversary emulation | A change record or engagement authorization. The tests reproduce real attacker behavior. | The organization. Not optional. |

**B. Inputs entered for each validation run.** The security or systems engineer supplies
these through the interface, and every field comes from the change record they are already
working from: the identifier of the hardening change, given as a CIS Benchmark control
number or a DISA STIG rule identifier, together with the script, group policy backup, or
configuration management task that applies it; the target host or host group and the
snapshot each capture starts from; the adversary emulation test identifiers that form the
stimulus, which may instead be given as the ATT&CK techniques to exercise; the observation
window duration and the number of repetitions per phase; and the statistical thresholds
declared under Scale of the Experiment.

**C. Outputs.** Each validation run produces one report in seven sections, plus
machine-readable exports.

| Section | Contents |
|---|---|
| Verdict | No significant change, blind spots found with their count and highest impact score, or inconclusive. Stated with the change identifier and target host. |
| Telemetry comparison | One row per event type: pre-change rate, post-change rate, rate ratio with confidence interval, corrected q value, the measured noise band, and the classification. |
| Ranked blind spots | For each lost or reduced event type: the detection rules that read it and their severity, the ATT&CK techniques those rules cover, and the impact score with its component terms shown. |
| Coverage change | Techniques covered before and after, and the specific techniques that moved from covered to uncovered. |
| Remediation candidates | For each finding, the ranked candidates described under Module 5. |
| Reproducibility record | The run manifest and its hash, the snapshot identifier, the test identifiers and versions, the rule set version, the analyser version, and the raw counts of every run. |
| Evaluation | Precision, recall, F1 score, and false positive rate for the proposed algorithm and the naive baseline against the injected ground truth. Produced for the study, not part of the operational report. |

Exports are produced in four forms: a report for reading, a CSV of the telemetry
comparison, a JSON file of findings for a ticketing system, and a MITRE ATT&CK Navigator
coverage layer.

### Scale of the Experiment

The evaluation covers 16 hardening changes, each drawn from a published baseline, the CIS
Benchmarks or the DISA STIGs. Each change is applied in isolation, so any telemetry effect
observed belongs to that change alone rather than to a combination. The dispersion model
for each event type is built from 5 control runs in which the same stimulus is applied and
nothing is changed. Each of the pre-change and post-change phases is repeated 3 times, so
within-phase variation appears in the comparison rather than being assumed absent. Every
run begins from the same restored snapshot, is driven by the same scripted suite, and is
recorded with its run identifier, phase label, and configuration state, so the full
experiment can be reconstructed and audited.

The statistical thresholds are declared before the evaluation begins and held constant
across all 16 changes. The false discovery rate is controlled at 0.05. An event type is
reported as reduced only when its rate ratio falls at or below 0.5, so that reductions that
are detectable but operationally immaterial are not reported as findings. An event type
must be observed at least 30 times in the pre-change phase before it is admitted to
testing, and is otherwise classified as inconclusive. These are configurable parameters of
the system, not constants of the method, and the sensitivity of precision and recall to
each of them is examined during evaluation.

### The Variance Floor and the External Validity of the Measurements

A reasonable objection to this design is that the two capture windows are made nearly
identical by construction, since the host is restored from the same snapshot and driven by
the same stimulus, so simple subtraction should be enough. The study answers this by
measurement rather than assertion.

Before any hardening change is evaluated, a control-versus-control experiment runs. The
identical suite is executed repeatedly against the same restored snapshot, across the same
5 control runs from which the dispersion model is built, with no configuration change of
any kind. The residual variation in each event type's count is recorded as a coefficient of
variation. That quantity is the run-to-run variance floor of the laboratory, and it is
reported with the results.

The consequence is stated in advance and is falsifiable in either direction. If the
variance floor is non-trivial, then counts differ between two runs in which nothing
changed, the statistical layer is necessary even under snapshot restoration, and the naive
baseline will report those residual differences as telemetry losses. The reduction in false
positives achieved over that baseline is then the direct experimental result of the study,
obtained under the most favourable conditions the baseline can be given. If the variance
floor is negligible, the statistical layer gains nothing inside the laboratory, and the
study reports that plainly. The testing and correction would then be justified only for
production, where snapshot restoration does not control the variance floor. The study
records that as a limitation of its own contribution rather than claiming a benefit it did
not observe.

This has a further consequence for how the results are read, and it is asymmetric. A
production environment has concurrent user activity, scheduled tasks, backup and patch
cycles, software updates, and ordinary variation in workload. The laboratory design
excludes every one of them. The naive baseline is sensitive to exactly the variance the
laboratory suppresses, so the false positive rate attributed to it here is the lowest rate
it can attain under any conditions. The reduction measured for the proposed method is
therefore a lower bound on the benefit obtainable in production, not an estimate of it.
Establishing that magnitude requires a deployment where the variance floor is not
controlled, which is outside the scope of this study.

### Features and Capabilities

The system will provide the following capabilities:

- Automated, repeatable capture of security event telemetry across defined pre-change and
  post-change observation windows
- Orchestrated execution of a scripted adversary simulation suite, so that stimulus is
  identical across capture windows
- Definition of every run by an immutable, hashed manifest, so two runs are compared only
  when their parameters are demonstrably identical
- Normalization of heterogeneous event formats from endpoint and operating system sources
  into a unified profile, keyed on the fields that detection rules discriminate upon
- Variance and dispersion modeling of each event type from repeated control runs in which
  nothing is changed
- Differential alignment of the two profiles, with a global test of profile change,
  per-event-type significance testing, and false discovery rate correction
- Classification of each event type as lost, significantly reduced, unchanged, newly
  introduced, or inconclusive
- Dependency mapping from lost event types to the detection rules and ATT&CK techniques
  that consume them
- Computation of a weighted blind-spot impact score and a ranked findings list
- Generation of ranked remediation candidates for each finding, comprising surviving
  telemetry sources, matched compensating controls, and the event fields that still
  discriminate attack activity from normal activity
- An enforced finding lifecycle, in which a finding cannot be closed as fixed without a
  re-validation run that passed
- Re-validation in two distinct modes, according to whether the remediation applied was a
  detection rule or a restoration of telemetry
- Exportable reports and a coverage layer for the MITRE ATT&CK Navigator
- Retention of experiment metadata, so any validation run can be reproduced and audited

### System Modules

The features above are organized into five modules.

- **Module 1. Telemetry Acquisition and Experiment Control.** This module governs the
  experimental procedure and is the only module that talks to the monitored environment. It
  manages the definition of a validation run: the hardening change under test, the target
  hosts, the observation window duration, and the number of repetitions per phase. Before
  any capture starts, it writes those parameters into an immutable run manifest, together
  with the snapshot identifier, the adversary emulation test identifiers and versions, the
  rule set version, and the statistical thresholds, and records the manifest's hash. Two
  runs are comparable only when their hashes match; where they differ, the system declines
  the comparison and names the parameter responsible. The module restores the virtual
  machine snapshot before every individual capture window rather than once per phase,
  triggers the adversary emulation suite through the Invoke-AtomicRedTeam framework against
  tests from the Atomic Red Team library, and retrieves the resulting events from the Wazuh
  platform through its indexer API. Every retrieved event is tagged with a run identifier, a
  repetition number, and a phase label distinguishing pre-change, post-change, and control
  captures.

- **Module 2. Event Normalization and Profiling.** This module turns raw, heterogeneous
  event records into the representation the system analyses. It parses Windows Security
  Event Log records and Sysmon records, and reduces each record to an event-type key. The key is the triple of telemetry source, numeric event
  identifier, and the discriminating field values that detection rules match upon. Including
  the field values is deliberate and material. A hardening change often degrades an event
  without removing it, as when a protection measure changes an access mask recorded inside
  an event while the event itself keeps being emitted at the same rate. A key built from the
  event identifier alone would call such an event type unchanged and would miss the blind
  spot entirely. The discriminating fields are not chosen by the researcher. They are read
  from the detection rule set, because a Sigma rule states in its detection block the exact
  fields it matches on, which ties the key space directly to what the detection logic
  depends on. From these keys the module builds a normalized frequency profile giving the
  rate of each key per unit of observation time, and computes per-key statistics from the
  control runs: the mean rate, the coefficient of variation, and the dispersion parameter.

- **Module 3. Differential Alignment and Statistical Analysis.** This module holds the core
  algorithm and works in three ordered stages. First it aligns the pre-change and
  post-change profiles across the union of their keys, inserting explicit zeros for keys
  present in only one profile. Second it applies a single chi-square test of homogeneity to
  the complete two-by-K table formed by the two phases across all K aligned keys. This
  answers whether the emitted profile changed at all and gates everything that follows;
  where the gate does not pass, the run is recorded as showing no significant change and is
  archived. Third, it computes for each key a rate ratio with confidence bounds and a p
  value, using the dispersion parameter measured in Module 2 in place of the equal variance
  and mean that Poisson assumes, then applies a Benjamini-Hochberg false discovery rate
  correction across the full set of per-key tests. Each key receives one of five
  classifications. **Lost**: seen before the change, absent after it. **Reduced**: the
  corrected q value, the effect size, and the measured noise floor are all satisfied
  together, all three required rather than any one. **New**: appears only after the change.
  **Inconclusive**: the pre-change count falls below the minimum at which the test has
  power. Everything else is **unchanged**. Inconclusive is reported rather than folded into
  unchanged, because a rare event type that cannot be tested is not evidence that coverage
  survived, and treating it as such would inflate the reported recall. The module also
  implements the naive event-count differencing baseline.

- **Module 4. Blind-Spot Impact Scoring and Coverage Mapping.** This module turns
  statistical findings into security findings. It maintains a dependency index linking each
  event-type key to the detection rules that reference it, and those rules to their ATT&CK
  techniques. The index is built automatically from the rule set in its authored form,
  Sigma YAML or Wazuh XML, from which the referenced fields and declared technique
  identifiers are read directly. Where a rule set carries no technique annotation, the
  mapping is supplied manually and maintained thereafter as an artifact of the system. For
  every key classified as lost or reduced, the module traverses the index to list the
  affected rules and techniques, then computes a weighted impact score. The score combines
  the severity of the affected rules, the number of rules affected, the tactic-level
  significance of the techniques, and the surviving coverage, expressed as the number of
  other event types still observed after the change that also support detection of the same
  technique. The last term is material: a technique that keeps three working detections has
  not become a blind spot, while a technique whose only detection has gone silent has.
  Findings are ranked by score.

- **Module 5. Reporting, Remediation and Experiment Validation.** This module presents
  results, proposes remediation, and supports the evaluation. It generates the ranked
  blind-spot report, side-by-side profile comparison views, and an exportable ATT&CK
  Navigator layer. For each finding it produces ranked remediation candidates at three
  levels of confidence: surviving event types that remain observable after the change and
  also support the affected technique, found by querying the dependency index; a matched
  entry from a curated knowledge base of hardening changes and their known compensating
  controls, built across the 16 changes examined here; and a ranked list of the event fields
  that still separate simulated adversary activity from control activity after the change,
  which the detection engineer uses as the starting point for a new rule. The system reports
  discriminating fields. It does not author rules. All candidates are advisory. The system deploys no detection content, and no
  candidate takes effect without the detection engineer's approval. Where no surviving
  source and no compensating control can be found, the module says so and directs the
  finding to documented risk acceptance. The module maintains each finding through an
  enforced lifecycle of open, remediation proposed, remediation applied, revalidating, and
  closed, and will not let a finding reach closed-as-fixed without a re-validation run that
  passed. Two re-validation modes are distinguished, because the two kinds of remediation
  need different evidence. A compensating detection rule does not change what the host
  emits, so the re-validation replays the identical manifest and confirms the rule fires. A
  restoration of telemetry does change what is emitted, so the re-validation takes a fresh
  capture and compares it against the stored pre-change profile. For evaluation, the module
  provides a ground-truth injection facility that deliberately disables known detections,
  and computes precision, recall, F1 score, and false positive rate for both the proposed
  algorithm and the naive baseline across the resulting labeled cases.

### Activity Diagram of the Proposed System

The activity diagram is presented on two sheets. It uses four partitions: the Security or
Systems Engineer, the proposed system, the monitored environment comprising the SIEM
platform with its endpoints and hypervisor, and the Security Detection Engineer. The flow
is organized into six phases.

**Phase 0** runs once per monitored environment, not once per change. The system executes 5
control captures in which the stimulus is applied and nothing is configured differently,
fits the noise model of each event type from them, and reads the detection rule set once to
build the event-type to rule to ATT&CK technique dependency index.

**Phase 1** captures the pre-change profile. The engineer defines the hardening change and
its scope. The system freezes and hashes the run manifest, then repeats the capture 3
times, each beginning from a restored snapshot.

**Phase 2** is the application of the hardening change and the recording of its metadata.

**Phase 3** re-runs the identical manifest 3 times from the changed host to build the
post-change profile.

**Phase 4** aligns the two profiles, applies the global test of profile change, localizes
the change to individual event types, classifies each of them, maps those classified as
lost or reduced to their dependent rules and techniques, computes the impact score, and
generates remediation candidates.

**Phase 5** is the detection engineer's review. It ends either in documented acceptance of
residual visibility risk or in remediation. Where remediation is required, the flow
separates according to the kind of fix, because the two kinds need different evidence of
success. A compensating detection rule does not change the telemetry the host emits, so a
further capture would reproduce the same counts and establish nothing; the re-validation
therefore replays the identical manifest and confirms the rule fires on the stimulus. A
restoration of telemetry, such as re-enabling an audit subcategory or changing the Sysmon
configuration, does change what is emitted, so the re-validation takes a fresh capture and
compares it against the stored pre-change profile. In both cases the finding is closed as
fixed only when the re-validation passes, and otherwise returns to review.

> **[IMAGE: T1_Activity_Diagram_Revised_Sheet1.png, phases 0 to 3]**

> **[IMAGE: T1_Activity_Diagram_Revised_Sheet2.png, phases 4 and 5]**

---

## Scope and Limitations

The boundaries of the study are stated here so its claims are not read more broadly than
the evidence supports.

The study covers Windows endpoints and two classes of host telemetry: Windows Security
Event Log records and Sysmon records. Network intrusion detection telemetry, Linux and
macOS endpoints, cloud control-plane audit logs, identity provider telemetry, and
application-layer logging are outside its scope. Network telemetry was considered and
excluded deliberately: it would require a separate sensor in the laboratory and a separate
rule source for the dependency index, and the schedule does not support building both.
Extending to these sources is identified as later work.

The evaluation examines 16 hardening changes, each applied in isolation so the telemetry
effect observed belongs to that change alone. The study does not examine what happens when
several changes are applied together, and makes no claim that their effects combine
additively.

All measurements come from a controlled laboratory. The consequences are set out under The
Variance Floor and the External Validity of the Measurements, and in short: the reduction
in false positives measured against the naive baseline is a lower bound on the benefit
obtainable in production, not an estimate of it.

The adversary emulation tests that provide the stimulus are open, published, and well
signatured. They reproduce known attacker behavior. They do not try to evade detection. It
follows that a rule firing against such a test does not establish that the rule would catch
an adversary actively trying to slip past it. **The study measures whether the evidence a
detection depends on still exists after a hardening change. It does not measure how robust
the detection logic is against evasion**, which is the separate problem addressed by Uetz
and colleagues in the work reviewed below.

The system proposes remediation and does not apply it. It deploys no detection content, and
every candidate needs the detection engineer's approval before it takes effect.

The accuracy of the impact score is bounded by how complete the dependency index is. Where
a rule set carries no ATT&CK annotation, the mapping is supplied manually, and the score
inherits whatever gaps that manual mapping has. The index is therefore treated as a
maintained artifact of the system, not a fixed input.

Finally, the study evaluates whether telemetry is present and whether techniques are
covered. It makes no assessment of the quality of the detection rules themselves. A
technique reported as covered is covered in the sense that a rule exists which reads live
telemetry for it, not in the sense that the rule has been shown to work.

---

## Importance of the Study

**To society.** Banks, government agencies, healthcare providers, and utilities hold
personal and financial data, and regulation requires them to harden their systems. This
study addresses a hazard arising directly from that compliance: a control implemented to
reduce risk may at the same time, and invisibly, reduce the ability to detect an intrusion.
Making such losses visible when they happen lets an organization improve its posture
without unknowingly degrading its ability to detect a breach. Faster detection limits how
long citizens' data is exposed and reduces disruption to essential services.

**To the security industry.** The study contributes a reproducible method and a working
system for change-aware detection validation, an activity currently performed manually,
selectively, or not at all. Commercial breach and attack simulation platforms measure
coverage continuously but do not attribute a loss of coverage to a specific configuration
change. Detection-as-code pipelines monitor rule health but cannot tell a rule that is
silent because no attack occurred from one that is silent because its telemetry
disappeared. Because the system is built on open-source components, the method is
affordable for small and medium enterprises and managed security service providers,
including those in the Philippines, for whom commercial validation platforms are often out
of reach.

**To computer science.** The study frames detection coverage regression as a measurable
computational problem, and applies hypothesis testing, effect-size estimation, and
multiple-comparison correction to security telemetry. It extends the literature on change
detection in data streams into a setting where the phenomenon of interest is the
disappearance of observations rather than the appearance of anomalous ones, which is
comparatively underexplored. It also produces a labeled dataset of hardening changes and
their telemetry effects, with a reproducible test harness.

**To security operations practitioners.** The study gives detection engineers and SOC
analysts a way to measure visibility that does not depend on remembering which rules read
which event sources. It turns an undocumented dependency, currently held informally by
experienced staff, into an explicit and queryable artifact. That reduces the operational
risk of staff turnover and makes coverage reporting more reliable.

---

## Target Users

| User | Function / Role | Benefit |
|---|---|---|
| Security Detection Engineer | Primary operator. Defines the detection scope of a run, reviews the ranked report and the remediation candidates after each change, decides whether remediation is required, and authors compensating rules where coverage was lost. Maintains the dependency index. | Gets an automated, evidence-based way to confirm that coverage survived a change, instead of relying on personal recall of rule-to-telemetry dependencies. Receives a prioritized remediation list rather than an undifferentiated set of differences, so engineering effort goes to the highest-impact losses first. |
| Security / Systems Engineer | Starts a validation run by registering the change and its scope, applies the configuration change between the two capture phases, and records the change metadata. | Can show that a hardening measure was implemented without unknowingly degrading detection capability, so security improvements ship with documented assurance rather than untested assumption. |
| SOC Analyst (Tier 1 and Tier 2) | Uses the coverage reports and ATT&CK Navigator layers as a reference on current visibility. Checks the record of known blind spots when triaging alerts and running investigations. | Gets an accurate, current picture of which techniques the environment can and cannot see. Avoids the incorrect assumption that no alerts means no attacker activity, and makes better escalation decisions. |
| SOC Manager / Security Operations Lead | Reviews impact scores and ranked findings to set priorities and make risk decisions, allocates engineering effort to remediation, and formally accepts and documents residual visibility risk where remediation is not pursued. | Gets a quantified measure of coverage lost per change, which supports defensible risk acceptance, evidence-based resource allocation, and accurate reporting of posture to management and auditors. |

---

## Similarities with any Previous Studies/Projects

**You Cannot Escape Me: Detecting Evasions of SIEM Rules in Enterprise Networks.**
Uetz, Rafael; Herzog, Marco; Hackländer, Louis; Schwarz, Simon; Henze, Martin (2024).
Proceedings of the 33rd USENIX Security Symposium, Philadelphia, pp. 5179-5196,
ISBN 978-1-939133-44-1, Distinguished Artifact Award. Preprint arXiv:2311.10197.
https://www.usenix.org/conference/usenixsecurity24/presentation/uetz

The authors address the problem that expert-written SIEM rules can be trivially evaded,
producing detection blind spots in which malicious actions trigger no alert. Of 292 Windows
process-creation Sigma rules they examined, 110 were fully evadable and 19 partially. They
built AMIDES, an open-source tool that compares incoming events against both rule
signatures and known-benign events to surface likely evasions. It caught 358 of 512
hand-crafted evasions, 70 percent, with zero false alerts, on four weeks of events from an
enterprise network of more than 50,000 users in which benign events outnumbered malicious
ones by roughly 145,000 to one. The authors describe the gaps they found as critical
detection blind spots.
This is the closest published work: both centre on detection blind spots, both use
controlled ground-truth injection, and both report precision and false alert measures. The
difference is cause and timing. AMIDES detects evasions produced by an active attacker in
live streams. This study detects blind spots produced by the defender's own hardening
changes, found proactively before an intrusion rather than during one.

**Rule-ATT&CK Mapper (RAM): Mapping SIEM Rules to TTPs Using LLMs.**
Wudali, Prasanna N.; Kravchik, Moshe; Malul, Ehud; Gandhi, Parth A.; Elovici, Yuval;
Shabtai, Asaf (2025). arXiv preprint arXiv:2502.02337, Ben-Gurion University of the Negev
and Rafael Advanced Defense Systems. https://arxiv.org/abs/2502.02337

SIEM rules must be mapped accurately to ATT&CK techniques, but manual annotation is slow
and error-prone, and earlier machine-learning approaches target unstructured text rather
than structured rule logic. The authors propose RAM, a multi-stage prompt-chaining pipeline
that uses large language models to map structured rules to techniques without pretraining
or fine-tuning. Evaluated on the Splunk Security Content dataset, the multi-stage design
improved accuracy over baseline prompting, with GPT-4-Turbo performing best. This is
directly relevant because the present study depends on an event-type to rule to technique
index, which is exactly the mapping RAM automates. The difference is what happens next. RAM
stops at annotating rules. This study traverses that mapping as a weighted dependency
graph, to rank remediation and to quantify how a telemetry loss cascades into lost
technique coverage.

**Improving Threat Detection in Wazuh Using Machine Learning Techniques.**
Gherabi, Noreddine (2025). Journal of Cybersecurity and Privacy, vol. 5, no. 2, article 34,
DOI 10.3390/jcp5020034, MDPI. https://www.mdpi.com/2624-800X/5/2/34

The author addresses the high false-positive rate of rule-based detection in Wazuh, an
open-source SIEM widely used in SOCs, by integrating Random Forest and DBSCAN into the
detection pipeline. Random Forest reached 97.2 percent accuracy; DBSCAN reached 91.06
percent with a false-positive rate of 0.0821, and both met real-time latency requirements.
This study shares the platform, the SOC audience, and the vocabulary of accuracy and
false-positive rate, and both apply quantitative methods on top of Wazuh telemetry rather
than relying on rule matching alone. The gap is orientation. That work improves the quality
of alerts that fire. This study detects the absence of telemetry that should have fired, a
failure mode that produces no alert and no false positive to measure.

**Cybersecurity Program for Philippine Higher Education Institutions: A Multiple-Case
Study.** De Ramos, Noly M.; Esponilla, Francisco Dente II (2022). International Journal of
Evaluation and Research in Education (IJERE), vol. 11, no. 3, pp. 1198-1209,
DOI 10.11591/ijere.v11i3.22863, IAES, Scopus-indexed.
https://ijere.iaescore.com/index.php/IJERE/article/view/22863

This qualitative multiple-case study examines the cybersecurity readiness of Philippine
State Universities and Colleges through structured interviews with IT experts in the
National Capital Region. The principal challenges identified were user education, cloud
security, information security strategy, and unsecured personal devices. Both authors are
affiliated with Philippine institutions. The connection is the setting rather than the
method: the work establishes that Philippine SUCs apply security measures under strategy
and expertise constraints, which is precisely the condition in which a hardening change is
applied and its detection consequences never checked. De Ramos and Esponilla assess
readiness qualitatively at governance level, with no telemetry analysis. This study
measures coverage loss empirically. The work establishes need and beneficiary context, not
technical precedent.

**Design of the Network Security Architecture for Smart Campus in the Philippines.**
Yuhong, Yang; Zhuo, Song; Monreal, Richard N. (2023). Journal of Knowledge Learning and
Science Technology, vol. 2, no. 1, pp. 26-34, DOI 10.60087/mrb0hh55. The venue is an
open-access journal of uncertain indexing status and is not a Philippine journal
(unverified indexing). https://jklst.org/index.php/home/article/view/14

The authors analyze the network security posture of Philippine smart campuses, identify
prevailing vulnerabilities, and design a multi-layered framework integrating access
control, authentication, intrusion detection, and incident response. Co-author Richard N.
Monreal is affiliated with Mapúa University. The relevance is that this is Philippine work
treating intrusion detection and incident response as core components of institutional
defense, matching this study's local beneficiaries and its concern with monitoring under
resource constraints. The gap is specificity: the work proposes an architecture at design
level and does not examine whether configuration changes degrade the telemetry that
intrusion detection depends on, which is the exact failure mode this study measures.

---

## Project Time Table (Gantt Chart)

### Gantt Chart of the system documentation and development

In the original document the schedule is drawn as shaded cells rather than text. The
shading is reproduced below as `X`.

| Activity | Aug 2026 | Sep 2026 | Oct 2026 | Nov 2026 | Dec 2026 (Wk 1 to 2) | Dec 2026 (Wk 3 to 4) |
|---|---|---|---|---|---|---|
| Data Gathering: Laboratory Build and Telemetry Acquisition | X | X |  |  |  |  |
| Construction of Chapter 1-2 | X | X |  |  |  |  |
| System Analysis and Construction of Chapter 3 |  | X |  |  |  |  |
| Preliminary Trial: single change, single host |  | X |  |  |  |  |
| Development: Analysis Engine and Command-Line Interface |  |  | X |  |  |  |
| Development: Impact Scoring and Remediation Candidates |  |  | X |  |  |  |
| Development: Reporting, Exports and Web Interface |  |  |  | X |  |  |
| Testing and Evaluation, 16 hardening changes |  |  |  | X |  |  |
| Results, Conclusion and Recommendations |  |  |  |  | X |  |
| Paper Presentation / Final Defense |  |  |  |  |  | X |

The analysis engine and the command-line interface are the deliverable of the study and
must be complete by the end of October, because the evaluation in November depends on them.
The web interface is built after them and is the component that would be reduced first if
the schedule slips.

| Recommending Approval | Name | Signature |
|---|---|---|
| Research Professor |  |  |
| Panel Member |  |  |
| Panel Member |  |  |
| Dean | Prof. Mary A. Soriano |  |
|  |  |  |

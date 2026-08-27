# T1 Proposal (Research Topic Proposal Form)

Extracted from `T1_Detection of Hardening-Induced Blind Spots.docx`.
This is the **submitted version, before the panel's revisions.**
The revisions are drafted separately in [docs/T1-PROPOSAL-REVISION.md](../../docs/T1-PROPOSAL-REVISION.md).

---

| Name of Student | Elijah Amorsolo |  |  |
|---|---|---|---|
| Student ID | OED20-0012616 | Program | BS Computer Science |

## Proposed Title

Detection of Hardening-Induced Blind Spots via Differential Sequence Alignment of Pre- and Post-Change Security Event Streams

---

## Area of Investigation


### Field and Background of the Study


The study falls under the field of cybersecurity, specifically within the sub-disciplines of security operations, detection engineering, and security event telemetry analysis. Security operations refers to the continuous practice of monitoring, detecting, investigating, and responding to malicious activity across an organization's computing infrastructure. This practice is typically institutionalized in a Security Operations Center (SOC), a function staffed by security analysts and engineers who rely on centralized log collection platforms to gain visibility into the behavior of endpoints, servers, and network devices.

The technological foundation of modern security operations is the Security Information and Event Management (SIEM) platform, which aggregates security event data from distributed sources, normalizes that data into a common schema, and evaluates it against a library of detection rules. When the conditions of a detection rule are satisfied, the platform generates an alert for analyst review. Contemporary platforms have expanded this model into Extended Detection and Response (XDR), which correlates telemetry across endpoint, network, and identity layers. Open-source platforms such as Wazuh, alongside commercial offerings, have made this capability accessible to organizations of varying size and budget, including small and medium enterprises in developing economies.

The authorship and maintenance of the detection rules that operate on this telemetry has matured into a distinct discipline known as detection engineering. Detection engineering treats detection logic as a software artifact subject to a lifecycle: requirements are derived from adversary behavior, logic is authored and version-controlled, and the resulting rules are tested, deployed, monitored, and periodically retired. Adversary behavior in this discipline is commonly described using the MITRE ATT&CK framework, a curated knowledge base that catalogs the tactics and techniques observed in real-world intrusions and provides a shared vocabulary for expressing what an organization can and cannot detect. Practitioners measure their posture in terms of detection coverage, which expresses the proportion of relevant adversary techniques for which a functioning detection exists.

A parallel and equally established discipline within information security is system hardening, which refers to the deliberate reduction of a system's attack surface through configuration change. Hardening is guided by published configuration baselines such as the Center for Internet Security (CIS) Benchmarks, the Defense Information Systems Agency (DISA) Security Technical Implementation Guides (STIGs), and vendor-issued security baselines. Typical hardening measures include disabling legacy cryptographic algorithms and deprecated network protocols, restricting the execution of scripting interpreters, tightening group policy settings, removing unnecessary services, and enforcing least-privilege access models. Regulatory and supervisory frameworks increasingly require documented hardening programs, making configuration change a routine and recurring activity in enterprise environments.

A structural relationship exists between these two disciplines that is central to the field. Detection rules do not observe adversary behavior directly; they observe the security events that a system emits as a byproduct of its configuration. The volume, type, and content of these events are therefore determined by configuration state. Because hardening is precisely the act of changing configuration state, hardening and detection are coupled: a change intended to reduce exposure simultaneously alters the evidentiary record on which detection depends. This coupling is well recognized in principle but is difficult to reason about in practice, because a single enterprise endpoint may emit thousands of events per hour distributed across hundreds of distinct event types.

To measure whether detections function as intended, the field has developed the practice of adversary emulation, in which known attacker behaviors are safely reproduced in a controlled environment so that the resulting detections can be observed. Open frameworks such as Atomic Red Team and MITRE Caldera provide libraries of scripted tests mapped to ATT&CK techniques, and the broader category of Breach and Attack Simulation (BAS) tooling automates this validation on a continuous basis. Complementing these operational practices, the computer science literature on data stream analysis provides formal methods for determining whether two streams of observations differ in a statistically meaningful way. Techniques including sequence alignment, distributional comparison, hypothesis testing for count data, and concept drift detection have been developed to distinguish genuine change from the random variation inherent in any observed process. The convergence of security telemetry analysis with these established statistical and algorithmic methods forms the general area within which this study is situated.


### Algorithms to be Used


The proposed system applies the following algorithms and techniques. The naive event-count differencing method serves as the experimental baseline against which the combined approach is measured.

| Algorithm / Technique | Purpose in the System |
|---|---|
| Differential sequence alignment over frequency profiles | Aligns pre-change and post-change event-type profiles and isolates absent or reduced event types |
| Chi-square test of homogeneity | Tests whether the observed distribution of an event type differs significantly between capture phases |
| Poisson rate ratio with confidence bounds | Quantifies the magnitude of change in event rate and provides an interpretable effect size for count data |
| Benjamini-Hochberg false discovery rate correction | Controls false findings arising from simultaneous hypothesis testing across hundreds of event types |
| Coefficient-of-variation baseline modeling | Establishes the normal operational variance of each event type from repeated control runs |
| Weighted graph traversal over the event-rule-technique dependency index | Maps lost telemetry to dependent detection rules and adversary techniques and computes the impact score |

---

## Reasons for Choice of Project


### The Current Process


In current practice, the validation of a security hardening change follows a largely manual and configuration-centric procedure. A security or systems engineer first identifies a required change, typically sourced from a compliance benchmark, a vulnerability assessment finding, or an internal security directive. The change is applied to a test group and then promoted to production through a change management process. Verification of the change consists of two activities. The first is a compliance check, in which a configuration scanner or a manual registry and policy review confirms that the intended setting is now in effect. The second is a functional regression test, in which business applications are exercised to confirm that no operational disruption has occurred.

Neither verification activity examines detection coverage. Where any detection-side verification occurs at all, it is performed on an ad hoc basis: a detection engineer may recall that a particular rule is related to the changed component and manually re-run one or two adversary simulation tests against it. This ad hoc review depends entirely on the engineer's memory of which rules consume which event sources, and it is not applied systematically across the rule set. In many organizations the only ongoing safeguard is a rule health report that flags detection rules which have not fired within a defined period. Such reports are consulted periodically rather than in connection with any specific change, and they are frequently ignored because a rule that has not fired is indistinguishable, on the evidence available, from a rule guarding against an attack that simply has not occurred.

The consequence is that the loss of detection capability produced by a hardening change is not surfaced by any step in the existing process. The change generates no error, no failed test, and no alert. The affected detection rule remains present in the rule set, remains enabled, and continues to appear in coverage reports as an active control. The deficiency is typically discovered only during a subsequent incident investigation, during an annual detection audit, or during a red team engagement in each case long after the coverage was lost. That the phenomenon is a demonstrable property of real systems rather than a theoretical concern will be established by a preliminary trial early in the development phase, in which a single hardening change is applied to a single instrumented host and the security event telemetry is compared before and after under identical scripted stimulus, so that a named event type present before the change and absent after it is exhibited as direct evidence that the loss occurs and produces no failure indication. This gap in the current process is the condition the study addresses.


### Research Design


The study adopts a developmental and experimental research design. It is developmental in that its primary output is a working software system, produced through the successive stages of requirements definition, design, implementation, and evaluation. It is experimental in that the completed system is compared against a named baseline under controlled conditions, using outcome measures declared before the evaluation begins. The baseline is naive event-count differencing, in which an event type is reported as lost whenever its post-change count falls below its pre-change count, with no modelling of variance and no test of statistical significance. The controlled conditions are established by returning each host to a known state through virtual machine snapshot restoration before every capture window and by executing an identical scripted adversary simulation suite in each of them, so that the applied configuration change is the only variable that differs between the pre-change and post-change phases. The pre-declared outcome measures are precision, recall, F1 score, and false positive rate, computed for the proposed algorithm and for the baseline against the same ground-truth set of deliberately induced telemetry losses, together with the proportion of the event-type space successfully analyzed. The problems that give rise to this design are stated below.


### Statement of the Problems


- Security hardening changes silently alter or eliminate the security event telemetry on which existing detection rules depend, creating detection blind spots that produce no error, alert, or failure indication and therefore remain unknown to the security team.

- The prevailing verification procedure for hardening changes evaluates only configuration compliance and application functionality, so no stage of the existing change process is capable of determining whether detection coverage survived the change.

- Manual before-and-after comparison of security event telemetry is not practical at operational scale, because the volume of events and the number of distinct event types generated by a monitored environment exceed what an analyst can reliably inspect and compare by inspection.

- A direct comparison of raw event counts before and after a change produces an unacceptable rate of false alarms, because normal operational variance arising from user activity, scheduled tasks, and patch cycles causes event volumes to fluctuate independently of any configuration change, rendering naive differencing unusable as a decision tool.

- Even where a change in telemetry is identified, there is no quantitative measure that links the affected event type to the specific detection rules and adversary techniques that depend on it, so the security impact of the loss cannot be assessed or prioritized for remediation.


### Objectives of the Study


General Objective. The study aims to design, develop, and evaluate a system that automatically detects hardening-induced detection blind spots by applying differential sequence alignment and statistical significance testing to pre-change and post-change security event streams, and that quantifies the detection coverage lost as a result of each change.


### Specific Objectives


- To design and implement a differential sequence alignment algorithm that represents pre-change and post-change security event telemetry as normalized frequency profiles and identifies event types that are absent or significantly reduced following a hardening change, thereby exposing telemetry losses that currently generate no failure indication. (addresses Problem 1).

- To integrate the algorithm into an automated validation workflow that captures baseline and post-change telemetry under controlled and repeatable conditions using scripted adversary simulation, so that detection coverage verification becomes an explicit and reproducible stage of the hardening change process. (addresses Problem 2).

- To automate the profile comparison across the complete event-type space of the monitored environment, enabling the analysis of event volumes and event-type counts that exceed the capacity of manual inspection. (addresses Problem 3).

- To incorporate statistical significance testing, comprising the chi-square test of homogeneity and Poisson rate-ratio estimation with confidence bounds, together with a Benjamini-Hochberg false discovery rate correction, in order to distinguish genuine hardening-induced telemetry loss from normal operational variance, and to measure the resulting reduction in false positives against a naive event-count differencing baseline across 16 distinct hardening changes drawn from the Center for Internet Security Benchmarks and the Defense Information Systems Agency Security Technical Implementation Guides, with the variance model for each event type constructed from 5 control runs and each capture phase repeated 3 times. (addresses Problem 4).

- To develop a blind-spot impact scoring component that maps each lost event type to its dependent detection rules and their associated MITRE ATT&CK techniques, producing a ranked report that quantifies the detection coverage lost by each hardening change. (addresses Problem 5).

---

## Project Context


### Concept of the Proposed System


The proposed system is a detection-coverage validation tool that operates as a controlled experiment around a hardening change. Rather than inspecting configuration state, the system observes what the monitored environment actually emits. It captures a baseline profile of security event telemetry before a hardening change is applied, captures a second profile after the change under identical stimulus conditions, and then determines by statistical comparison which event types were lost or materially reduced. Identical stimulus is achieved by executing the same scripted adversary simulation suite in both capture windows, so that any difference between the two profiles is attributable to the configuration change rather than to differences in activity.

The core contribution is algorithmic. The system does not merely subtract one set of event counts from another; it aligns the two frequency profiles, models the expected variance of each event type from repeated control runs, and applies hypothesis testing with multiple-comparison correction to determine which differences are statistically significant. It then traverses the dependency relationship between event types, detection rules, and adversary techniques to convert a statistical finding into a prioritized statement of security impact.


### Scale of the Experiment


The evaluation is conducted over 16 distinct hardening changes, each drawn from a published configuration baseline, specifically the Center for Internet Security Benchmarks and the Defense Information Systems Agency Security Technical Implementation Guides, and each applied in isolation so that any telemetry effect observed is attributable to that change alone rather than to a combination of changes. The variance model for each event type is constructed from 5 control runs in which the environment is exercised by the same stimulus with no configuration change applied. Each of the pre-change and post-change capture phases is repeated 3 times, so that within-phase variation is represented in the comparison rather than assumed to be absent. Every run begins from the same restored snapshot and is driven by the same scripted adversary simulation suite, and every run is recorded with its run identifier, phase label, and configuration state so that the full experiment can be reconstructed and audited.


### Justification of the Statistical Layer


A reasonable objection to this design is that the two capture windows are made near-identical by construction, since the host is restored from the same virtual machine snapshot and driven by the same scripted stimulus in both phases, and that simple subtraction of event counts would therefore be sufficient. The study answers this objection by measurement rather than by assertion. Before any hardening change is evaluated, a control-versus-control experiment is executed: the identical adversary simulation suite is executed repeatedly against the same restored snapshot, across the same control runs from which the per-event-type variance model is built, with no configuration change of any kind applied between the runs, and the residual variation in the observed count of each event type is recorded as a coefficient of variation. This quantity is the run-to-run variance floor of the laboratory, and it is the empirical basis on which the statistical layer either is or is not warranted. It is established by the control-versus-control experiment as the coefficient of variation of each event type across the control runs, and it is reported with the results of the study.

The consequence of that measurement is stated in advance and is falsifiable in either direction. If the measured variance floor is non-trivial, then event counts differ between two runs in which nothing was changed, the statistical layer is necessary even under snapshot restoration, and the naive event-count differencing baseline will report those residual differences as telemetry losses; the reduction in false positives achieved by the proposed method over that baseline is then the direct experimental result of the study, and it is obtained under the most favourable conditions the baseline can be given. If instead the measured variance floor is negligible, the statistical layer confers no advantage inside the laboratory, and the study reports that finding without qualification: in that case the significance testing, effect-size estimation, and false discovery rate correction are justified only for deployment in a production environment, where the variance floor is not controlled by snapshot restoration and cannot be assumed negligible, and the study records that restriction as a stated limitation of its own contribution rather than claiming a benefit it did not observe.


### External Validity of the Measurements


All measurements reported by this study are obtained in a controlled laboratory in which each host is returned to a known state by snapshot restoration before every capture window and is driven by a fixed scripted stimulus. A production environment does not have these properties. Concurrent user activity, scheduled tasks, backup and patch cycles, software updates, and ordinary variation in workload all contribute additional variance to event counts, and the laboratory design deliberately excludes every one of them. The consequence for the interpretation of the results is asymmetric, and it is stated here rather than left for the reader to infer. The naive event-count differencing baseline is sensitive to precisely the variance that the laboratory suppresses, so the false positive rate attributed to that baseline in this study is the lowest rate it can attain under any conditions. The reduction in false positives measured for the proposed method is therefore a lower bound on the benefit obtainable in production rather than a direct estimate of it. Establishing the magnitude of that benefit under production conditions requires a deployment in which the variance floor is not controlled, which is outside the scope of this study and is identified as work for subsequent research.


### Features and Capabilities


The proposed system will provide the following capabilities:

- Automated, repeatable capture of security event telemetry across defined pre-change and post-change observation windows

- Orchestrated execution of a scripted adversary simulation suite to guarantee identical stimulus across capture windows

- Normalization of heterogeneous event formats from endpoint, operating system, and network sources into a unified event-type profile

- Variance modeling of each event type derived from repeated control runs in which no configuration change is applied

- Differential alignment of pre-change and post-change profiles with statistical significance testing and false discovery rate correction

- Classification of each event type as lost, significantly reduced, unchanged, or newly introduced

- Dependency mapping from lost event types to the detection rules and MITRE ATT&CK techniques that consume them

- Computation of a weighted blind-spot impact score and generation of a ranked remediation list

- Exportable reports and a coverage layer suitable for visualization in the MITRE ATT&CK Navigator

- Retention of experiment metadata enabling any validation run to be reproduced and audited


### System Modules


The features above are organized into five modules.

- Module 1 Telemetry Acquisition and Experiment Control Module. This module governs the experimental procedure. It manages the definition of a validation run, including the hardening change under test, the target hosts, and the observation window duration. It orchestrates virtual machine snapshot restoration to guarantee a consistent starting state, triggers the adversary simulation suite, and retrieves the resulting security events from the SIEM platform through its application programming interface (API). All retrieved events are tagged with run identifiers and phase labels distinguishing pre-change, post-change, and control captures.

- Module 2 Event Normalization and Profiling Module. This module converts raw, heterogeneous event records into the analytical representation used by the system. It parses Windows Security Event Log records, Sysmon records, and network intrusion detection alerts, extracts the fields that define an event type, and constructs a normalized frequency profile expressing the rate of occurrence of each event type per unit of observation time. It also computes per-event-type variance statistics from repeated control runs, which form the reference distribution used in later significance testing.

- Module 3 Differential Alignment and Statistical Analysis Module. This module contains the core algorithm of the study. It aligns the pre-change and post-change profiles across their union of event types, handling event types present in only one profile. For each aligned event type it computes a chi-square test of homogeneity and a Poisson rate ratio with confidence bounds, then applies a Benjamini-Hochberg false discovery rate correction across the full set of comparisons to control the proportion of false findings arising from simultaneous testing of many event types. Each event type is assigned a classification and an effect size. The module also implements the naive event-count differencing baseline against which the proposed algorithm is evaluated.

- Module 4 Blind-Spot Impact Scoring and Coverage Mapping Module. This module converts statistical findings into security findings. It maintains a dependency index linking each event type to the detection rules that reference it and links those rules to their associated MITRE ATT&CK techniques. For every event type classified as lost or significantly reduced, the module traverses this index to enumerate the affected rules and techniques, then computes a weighted impact score reflecting the severity of the affected rules, the number of rules affected, and the tactic-level significance of the associated techniques. Findings are ranked by score.

- Module 5 Reporting, Visualization, and Experiment Validation Module. This module presents results and supports the experimental evaluation of the study. It generates a ranked blind-spot report, side-by-side profile comparison views, and an exportable ATT&CK Navigator coverage layer. For evaluation purposes it provides a ground-truth injection facility that deliberately disables known detections through controlled hardening changes, and it computes precision, recall, F1 score, and false positive rate for both the proposed algorithm and the naive baseline across the resulting labeled test cases.


### Activity Diagram of the Proposed System


The activity diagram below uses four partitions representing the Security or Systems Engineer, the proposed system, the monitored environment comprising the SIEM platform and its endpoints, and the Security Detection Engineer. The flow proceeds from the definition of a hardening change through baseline capture, change application, post-change capture, differential analysis, and impact scoring, terminating either in a recorded finding of no blind spot or in a reviewed and ranked blind-spot report. Where remediation is required, a compensating detection rule is implemented and the validation cycle is repeated.


> **[IMAGE IN ORIGINAL DOCUMENT: activity diagram]**


---

## Importance of the Study

To society. Organizations that hold personal and financial data, including banks, government agencies, healthcare providers, and utilities, are required by regulation and supervisory guidance to harden their systems against attack. The findings of this study address a hazard that arises directly from compliance with those requirements: the possibility that a control implemented to reduce risk simultaneously and invisibly reduces the organization's ability to detect an intrusion. By making such losses visible at the moment they occur, the study supports the objective of an organization improving its security posture without unknowingly degrading its capacity to detect a breach. Faster detection of intrusions limits the exposure of the personal data of ordinary citizens, and reduces the disruption to essential services on which the public depends.

To the computer science and information technology security industry. The study contributes a reproducible method and an implemented system for change-aware detection validation, an activity that is currently performed manually, selectively, or not at all. Existing commercial breach and attack simulation platforms measure detection coverage on a continuous basis but do not attribute a loss of coverage to a specific configuration change, and detection-as-code pipelines monitor rule health without distinguishing a rule that is silent because no attack occurred from a rule that is silent because its underlying telemetry has disappeared. The proposed approach addresses this specific gap. Because it is built on open-source components, the resulting method is accessible to small and medium enterprises and to managed security service providers operating under budget constraints, including those in the Philippines, for whom commercial validation platforms are frequently not economically viable.

To computer science as a discipline. The study formalizes detection coverage regression as a measurable computational problem and demonstrates the application of statistical hypothesis testing, effect-size estimation, and multiple-comparison correction to the domain of security telemetry analysis. It extends the established literature on change detection in data streams into an application area where the phenomenon of interest is the disappearance of observations rather than the appearance of anomalous ones, a comparatively underexplored framing. The study additionally produces a labeled experimental dataset of hardening changes and their corresponding telemetry effects, together with a reproducible test harness, both of which can support further research in detection engineering and security analytics.

To security operations practitioners. For detection engineers and SOC analysts, the study provides a means of quantifying visibility that does not depend on institutional memory of which detection rules consume which event sources. It converts an undocumented dependency, presently held informally by experienced staff, into an explicit and queryable artifact, thereby reducing the operational risk associated with staff turnover and improving the reliability of coverage reporting.

To future researchers. The system, its evaluation methodology, and the accompanying labeled dataset provide a foundation on which subsequent studies can build, including extension to additional operating systems and telemetry sources, application to cloud-based control planes, and investigation of predictive models that estimate the detection impact of a proposed change before it is applied.

---

## Target Users

| User | Function/Role | Benefit |
|---|---|---|
| Security Detection Engineer | Primary operator of the system. Defines the detection scope of a validation run, reviews the ranked blind-spot report produced after each hardening change, decides whether remediation is required, and authors compensating detection rules where coverage has been lost. Maintains the event-type to detection-rule dependency index used by the impact scoring module. | Gains an automated and evidence-based means of confirming that detection coverage survived a configuration change, eliminating reliance on personal recall of rule-to-telemetry dependencies. Receives a prioritized remediation list rather than an undifferentiated set of differences, allowing engineering effort to be directed at the highest-impact losses first. |
| Security / Systems Engineer | Initiates a validation run by registering the hardening change to be tested and its target scope, applies the configuration change between the two capture phases, and records the associated change metadata within the system. | Is able to demonstrate that a hardening measure was implemented without unknowingly degrading the organization's detection capability, allowing security improvements to be deployed with documented assurance rather than untested assumption. |
| SOC Analyst (Tier 1 and Tier 2) | Consumes the coverage reports and ATT&CK Navigator layers generated by the system as a reference on the current state of detection visibility. Reviews the record of known blind spots when triaging alerts and conducting investigations. | Obtains an accurate and current picture of which adversary techniques the environment can and cannot observe, preventing the incorrect assumption that the absence of alerts constitutes evidence of the absence of attacker activity, and enabling better-informed escalation decisions. |
| SOC Manager / Security Operations Lead | Reviews the blind-spot impact scores and ranked findings to make prioritization and risk decisions, allocates engineering effort toward remediation, and formally accepts and documents residual visibility risk where remediation is not pursued. | Receives a quantified measure of detection coverage lost per configuration change, supporting defensible risk-acceptance decisions, evidence-based resource allocation, and accurate reporting of security posture to management and auditors. |

---

## Similarities with any Previous Studies/Projects

YOU CANNOT ESCAPE ME: DETECTING EVASIONS OF SIEM RULES IN ENTERPRISE NETWORKS

Uetz, Rafael; Herzog, Marco; Hackländer, Louis; Schwarz, Simon; Henze, Martin (2024)

August 2024, Proceedings of the 33rd USENIX Security Symposium, Philadelphia, PA, pp. 5179-5196, ISBN 978-1-939133-44-1 (Distinguished Artifact Award). Preprint: arXiv:2311.10197.

https://www.usenix.org/conference/usenixsecurity24/presentation/uetz

This study addresses the problem that expert-written SIEM detection rules can be trivially evaded by adversaries, producing "detection blind spots" in which malicious actions occur without triggering alerts. The authors first analyzed a set of widespread Sigma detection rules and found that 38 percent were fully evadable and 7 percent partially evadable (110 fully plus 19 partially of 292 Windows process-creation Sigma rules), which the authors summarize as "major detection blind spots." To remedy this, they propose adaptive misuse detection and build AMIDES, an open-source proof-of-concept that uses machine learning to compare incoming events both against SIEM rule signatures and against known-benign events to surface likely evasions. They evaluated AMIDES on four weeks of SIEM events from a large enterprise network together with more than 500 hand-crafted evasions. AMIDES detected 70 percent of the evasions (358 true positives and 154 false negatives of 512) with zero false alerts against roughly 74.4 million benign events, and it attributed the evaded rule in the top-ranked position for 63 percent of evasions and within the top 10 for 95 percent. Its computational efficiency was found suitable for real-world operation, and the authors conclude that organizations can significantly reduce detection blind spots with moderate effort.

This is the closest published work to the proposal because both center on the concept of detection blind spots in SIEM rule coverage and both quantify how many detections silently fail. Both use controlled ground-truth injection (hand-crafted evasions in AMIDES; deliberately disabled detections in the proposal) and evaluate with precision, recall, and false alert measures. The key difference the proposal addresses is causation and timing: AMIDES detects evasions produced by an active attacker in live event streams, whereas the proposal detects blind spots produced by the defender's own hardening changes, caught proactively through a before/after controlled experiment rather than during an intrusion.

RULE-ATT&CK MAPPER (RAM): MAPPING SIEM RULES TO TTPS USING LLMS

Wudali, Prasanna N.; Kravchik, Moshe; Malul, Ehud; Gandhi, Parth A.; Elovici, Yuval; Shabtai, Asaf (2025)

February 2025, arXiv preprint arXiv:2502.02337 (Ben-Gurion University of the Negev and Rafael Advanced Defense Systems).

https://arxiv.org/abs/2502.02337

This study tackles the problem that SIEM rules must be accurately mapped to MITRE ATT&CK techniques for threat analysis, but manual annotation is slow and error-prone and prior machine-learning approaches target unstructured text rather than structured rule logic. Inaccurate mapping causes attacks to be misinterpreted and threats to be overlooked. The authors propose RAM, a multi-stage pipeline inspired by prompt chaining that leverages large language models to automate mapping of structured SIEM rules to ATT&CK techniques without pretraining or fine-tuning. Using the Splunk Security Content dataset, they evaluated RAM across several LLMs including GPT-4-Turbo, Qwen, IBM Granite, and Mistral. GPT-4-Turbo delivered the strongest performance, and the study reports that the multi-stage design improved mapping accuracy over baseline prompting. The authors conclude that LLM-driven mapping can reduce analyst workload and improve the consistency of rule-to-technique annotation.

This work is directly relevant because the proposal depends on an event-type to detection-rule to MITRE ATT&CK technique dependency index to compute its blind-spot impact score, which is exactly the rule-to-technique mapping RAM automates. Both treat the linkage between detection content and ATT&CK techniques as the backbone for coverage reasoning. The difference the proposal addresses is that RAM stops at annotating existing rules, while the proposal traverses that mapping as a weighted dependency graph to rank remediation and to quantify how a hardening-induced telemetry loss cascades into lost technique coverage.

IMPROVING THREAT DETECTION IN WAZUH USING MACHINE LEARNING TECHNIQUES

Gherabi, Noreddine (2025)

June 14, 2025, Journal of Cybersecurity and Privacy, vol. 5, no. 2, article 34, DOI: 10.3390/jcp5020034 (MDPI).

https://www.mdpi.com/2624-800X/5/2/34

This study addresses the high false-positive rate of rule-based detection in Wazuh, an open-source SIEM widely used in Security Operations Centers. The author proposes a hybrid approach that integrates Random Forest and DBSCAN machine-learning techniques into the Wazuh detection pipeline to improve accuracy and operational efficiency. The models were evaluated for both detection quality and real-time deployment feasibility in a SOC-representative setting. Random Forest achieved 97.2 percent accuracy while DBSCAN achieved 91.06 percent accuracy with a false-positive rate of 0.0821. All models maintained end-to-end processing latency below 100 milliseconds, with 95 percent of events processed within 500 milliseconds, and scalability testing confirmed roughly linear performance up to 500 events per second. The author concludes that the integration offers a practical, resource-efficient way to strengthen real-time detection in modern environments.

This study shares the proposal's platform (Wazuh SIEM/XDR), its SOC target users, and its evaluation vocabulary of accuracy and false-positive rate, and both aim to make open-source SIEM more reliable for resource-constrained teams. Both apply quantitative statistical or machine-learning methods on top of Wazuh telemetry rather than relying on raw rule matching alone. The gap the proposal addresses is orientation: this work improves the quality of alerts that fire, whereas the proposal detects the absence of telemetry that should have fired, a failure mode that produces no alert and no false positive to measure.

CYBERSECURITY PROGRAM FOR PHILIPPINE HIGHER EDUCATION INSTITUTIONS: A MULTIPLE-CASE STUDY

De Ramos, Noly M.; Esponilla, Francisco Dente II (2022)

September 2022, International Journal of Evaluation and Research in Education (IJERE), vol. 11, no. 3, pp. 1198-1209, DOI: 10.11591/ijere.v11i3.22863 (IAES, Scopus-indexed)

https://ijere.iaescore.com/index.php/IJERE/article/view/22863

This study examines the cybersecurity readiness of Philippine State Universities and Colleges, whose management information systems face rising threats to student data and institutional assets. It uses a qualitative multiple-case design with structured interviews of purposively selected IT experts from SUCs in the National Capital Region, analyzed through thematic coding. The principal challenges identified were user education, cloud security, information security strategy, and unsecured personal devices. The authors propose a program logic model to guide cybersecurity planning, implementation, and assessment for national bodies including CHED, DICT, and PASUC. Both authors are affiliated with Philippine institutions (Philippine Normal University and the Technological University of the Philippines). The study documents an environment in which security controls are applied without a supporting verification capability.

The connection to the proposed study is the setting rather than the method: this work establishes that Philippine SUCs implement security measures under strategy and expertise constraints, which is precisely the condition under which a hardening change would be applied and its detection consequences never checked. Both works are concerned with whether an organization's stated security posture matches its actual defensive capability. The key difference is that De Ramos and Esponilla assess readiness qualitatively at the governance level with no telemetry or detection analysis, whereas the proposed study delivers an instrumented, statistically validated system that measures detection coverage loss empirically; this local study establishes need and beneficiary context, not technical precedent.

DESIGN OF THE NETWORK SECURITY ARCHITECTURE FOR SMART CAMPUS IN THE PHILIPPINES

Yuhong, Yang; Zhuo, Song; Monreal, Richard N. (2023)

April 30, 2023, Journal of Knowledge Learning and Science Technology, vol. 2, no. 1, pp. 26-34, DOI: 10.60087/mrb0hh55. Venue is an open-access journal of uncertain indexing status and is not itself a Philippine journal (unverified indexing).

https://jklst.org/index.php/home/article/view/14

This study examines the network security posture of smart campuses in the Philippines and proposes a more robust architecture as institutions adopt smart technologies. The authors analyze the current state of Philippine smart-campus construction, identify prevailing vulnerabilities, and design a multi-layered security framework integrating access control, authentication, intrusion detection systems, and incident response, drawing on domestic and international research. The framework incorporates situational-awareness and zero-trust concepts. The authors report that the proposed framework enhances security for Philippine smart campuses and state that effectiveness was verified through implementation. Co-author Richard N. Monreal is affiliated with Mapúa University. The work is a framework-design study rather than a hands-on tool deployment.

The relevance is that this is a Philippine work treating intrusion detection and incident response as core components of institutional defense, matching the proposed study's local beneficiaries and its concern with layered monitoring under resource constraints. Both assume that detection capability is a defensible asset that must be maintained rather than assumed. The gap the proposal addresses is rigor and specificity: this study proposes an architecture at the design level and does not examine whether configuration changes degrade the telemetry that intrusion detection depends on, which is the exact failure mode the proposed system measures with controlled before-and-after experiments and significance testing.

---

## Project Time Table (Gantt Chart)

---


### Gantt Chart of the system documentation and development


In the original document the schedule is drawn as shaded cells rather than text. The shading is
reproduced below as `X`.

| Activity | Aug 2026 | Sep 2026 | Oct 2026 | Nov 2026 | Dec 2026 (Wk 1–2) | Dec 2026 (Wk 3–4) |
|---|---|---|---|---|---|---|
| Data Gathering: Laboratory Build and Telemetry Acquisition | X |  |  |  |  |  |
| Construction of Chapter 1-2 | X | X |  |  |  |  |
| System Analysis and Construction of Chapter 3 |  | X |  |  |  |  |
| System Development |  |  | X | X |  |  |
| Testing and Evaluation |  |  |  | X |  |  |
| Results, Conclusion and Recommendations |  |  |  |  | X |  |
| Paper Presentation / Final Defense |  |  |  |  |  | X |

| Recommending Approval | Name | Signature |
|---|---|---|
| Research Professor |  |  |
| Panel Member |  |  |
| Panel Member |  |  |
| Dean | Prof. Mary A. Soriano |  |
|  |  |  |

# TeLoS

**Te**lemetry **Lo**ss. A tool that finds the detection blind spots created by security hardening.

Undergraduate BS Computer Science thesis, plus the purple team lab built to run it.

> **Detecting Security Blind Spots Through Pre- and Post-Hardening Events Using Differential
> Analysis Algorithm**
>
> Elijah Amorsolo, OED20-0012616

---

## The problem

A detection rule never watches an attacker directly. It watches the events a system emits, and
configuration decides which events a system emits.

Security hardening is the act of changing configuration. So a change made to reduce risk can
also delete the evidence a detection rule depends on. The rule stays enabled. It stays green on
the coverage report. It detects nothing.

Nothing errors. Nothing alerts. Teams usually find out during an incident, months later.

---

## It works

This is real output from `src/demo.py`. I simulated one hardening change: one event type
removed outright, one genuinely cut to 30 percent, and one noisy type that drifted down 1.4
percent on its own.

```
  method                       TP   FP   FN  precision   recall      F1
  -------------------------- ---- ---- ---- ---------- -------- -------
  naive differencing            2    8    0     20.0%  100.0%   0.333
  proposed system               2    0    0    100.0%  100.0%   1.000
```

Both methods found both real losses. The difference is the eight false alarms.

Each false alarm is an event type that moved on its own, by less than the amount it was already
measured to move. An engineer comparing raw counts would investigate every one of them. TeLoS
measures each event type's natural variation first, then only reports a drop that exceeds it.

**These numbers are synthetic.** They demonstrate that the code is correct. They are not
measurements, and they are not a result of the study. Full output:
[docs/demo-output.txt](docs/demo-output.txt)

---

## Run it

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

```bash
.venv/Scripts/python.exe src/demo.py
```

```bash
.venv/Scripts/python.exe -m pytest tests -q
```

The demo needs no lab, no SIEM, and no virtual machines. The analyser consumes event counts and
does not care where they came from.

---

## Status

Honest state of the work, not a plan.

| Component | Status |
|---|---|
| Analysis core (variance model, differential analysis, classification) | **Built.** 20 tests passing. |
| Naive baseline, for comparison | **Built** |
| Reporting | Text output only |
| Acquisition from live VMs | Not built. Needs the lab. |
| Impact scoring (lost event to affected rules to ATT&CK techniques) | Not built |
| Web interface | Not built |
| Lab Phase 0, host readiness | **Done** |
| Lab Phase 1, virtual networks | **Done** |
| Lab Phase 2, SIEM build | In progress |
| Lab Phases 3 to 7 | Not started |

---

## How the analysis works

1. **Measure the noise floor.** Run the identical stimulus 5 times against the same restored
   snapshot with nothing changed. Whatever varies is the laboratory's own noise. Recorded per
   event type as a coefficient of variation and a dispersion parameter.
2. **Global gate.** One chi-square test of homogeneity across the whole profile. Did anything
   change at all? Applied once, not once per event type.
3. **Per-type rate ratio.** Dispersion-aware, using the variance measured in step 1 rather than
   assuming Poisson equidispersion.
4. **Correction.** Benjamini-Hochberg across every event type tested, because testing several
   hundred at once will otherwise produce findings by chance alone.
5. **Classification.** LOST, REDUCED, UNCHANGED, NEW, or INCONCLUSIVE.

An event type is only reported as REDUCED when three conditions hold together: the corrected q
value, the effect size, and the measured noise floor. Any one alone is not enough.

---

## Repository layout

```
docs/     runbook, decision log, work log, open questions, command reference
src/      TeLoS analyser (Python)
tests/    20 tests for the analysis core
thesis/   the proposal, and the two alternatives that were not chosen
lab/      homelab blueprint, pinned configs, hardening scripts
data/     runs/ is local only, summaries/ is committed
```

Start with [CLAUDE.md](CLAUDE.md). It is the index to everything.

---

## Build the lab yourself

[docs/RUNBOOK-homelab.md](docs/RUNBOOK-homelab.md) rebuilds the whole thing from a bare host,
in 8 phases, with a check at the end of each one.

Host: Ryzen 9 7950X, 64 GB RAM, VMware Workstation 17.5.1. Wazuh SIEM on Ubuntu, Sysmon and
Atomic Red Team on a Windows endpoint, orchestrated over `vmrun` from Python on the Windows
host. Every command run on the host is recorded in [docs/COMMANDS.md](docs/COMMANDS.md), with
what a correct result looks like.

---

## Methodology notes

Two things here are deliberate.

**A pre-declared falsifiable outcome.** Before collecting any data, I state the result that
would prove my own central claim unnecessary, and commit to reporting it without softening. The
statistical layer is only justified if the laboratory's run-to-run variance is non-zero. If it
turns out to be negligible, I report that plainly and restrict the claim to production
deployment, where the variance floor is not controlled by snapshot restoration.

**Untestable is reported, not assumed safe.** An event type seen too few times before a change
cannot be tested with any power. TeLoS reports these as INCONCLUSIVE rather than folding them
into UNCHANGED. Calling them unchanged would claim they survived, which the data does not
support, and would inflate the reported recall.

Claims that are engineering judgment rather than sourced fact are labeled `(unverified)`
inline throughout.

---

## Alternatives considered

I wrote up two other topics as full proposals before choosing T1. Both remain in
[thesis/](thesis/README.md).

**T2, severity inversion in the Wazuh ruleset.** Rules form a dependency graph, and a serious
alert can sit at a severity level no analyst ever sees. Not chosen, but it remains the fallback
if the primary approach fails its feasibility gate.

**T3, analytic robustness scoring.** Score how hard each detection rule is to evade, and
validate against the manually annotated subset of the Sigma corpus. **I killed it after
checking the assumption it rested on.** Counting the corpus at pinned commit `da9bb07` turned
up only **6 rules out of 3,783** carrying a Summiting the Pyramid annotation, which is 0.16
percent. Far too few for the agreement statistic the evaluation depended on. Method and
evidence in [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md).

---

## License

Code and documentation are released under the [MIT License](LICENSE). You may use, copy,
modify, and redistribute the work, including for commercial use, as long as the copyright
notice is kept. This keeps the tool usable by small companies, which is a stated goal of the
thesis.

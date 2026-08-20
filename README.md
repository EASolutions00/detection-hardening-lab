# Detection Engineering Thesis and Homelab

BS Computer Science thesis, plus the purple team lab built to run it.

**Elijah Amorsolo** - OED20-0012616

---

## The question

A detection rule can be present, enabled, and green on the coverage report, and still detect
nothing at all. Three ways that happens, one thesis each:

| | Topic | What makes the detection useless | Needs a lab |
|---|---|---|---|
| **T1** | Hardening-induced blind spots | Hardening deleted the events the rule reads | Yes |
| **T2** | Severity inversion | The alert fires at a level no human ever sees | No |
| **T3** | Analytic robustness | The rule is real but trivially evaded | No |

These are alternatives, not parts. One gets built. T1 is the primary choice and it is gated
behind a two week feasibility spike.

---

## Repository layout

```
docs/     runbook, decision log, work log, open questions
thesis/   the three proposals, one folder each
lab/      homelab blueprint, pinned configs, hardening scripts
src/      Python harness and analysis code
data/     runs/ is local only, summaries/ is committed
```

Start with [CLAUDE.md](CLAUDE.md). It is the index to everything.

---

## Build the lab yourself

[docs/RUNBOOK-homelab.md](docs/RUNBOOK-homelab.md) rebuilds the whole thing from a bare host,
step by step, with a check at the end of every phase.

Host used: Ryzen 7950X, 64 GB RAM, VMware Workstation 17.5.1 Pro. Wazuh SIEM, Sysmon,
Atomic Red Team, orchestrated over `vmrun` from a Python harness on the Windows host.

---

## Methodology notes

Two things in here are deliberate and worth calling out.

**Pre-declared falsifiable outcomes.** T1 and T3 both state, before any data is collected,
the result that would prove them wrong, and commit to reporting it without softening. T1's
statistics layer is justified only if the lab's run to run variance is non-zero. If it turns
out to be zero, the study says so plainly and restricts its claim to production deployment.

**Honest coverage reporting.** Rules that cannot be parsed are counted and reported as
unscorable rather than quietly dropped. Corpora are pinned to a named commit so the numbers
can be reproduced.

Claims that are engineering judgment rather than sourced fact are labeled `(unverified)`
inline throughout.

---

## License

Code and documentation are released under the [MIT License](LICENSE). You may use, copy,
modify, and redistribute the work, including for commercial use, as long as the copyright
notice is kept. This keeps the tool usable by small companies, which is a stated goal of the
thesis.

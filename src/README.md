# src - Python code

Empty for now. No code has been written yet.

## Stack (from `lab/blueprint.md` section 9)

Python 3.11+ in a venv on C:. Packages: `lxml`, `pyyaml`, `networkx`, `scikit-learn`, `pandas`.

## Planned layout

```
src/
  harness/     capture orchestration. Runs on the Windows HOST, not in a VM,
               because vmrun.exe is local and the Wazuh API is on vmnet2.
  analysis/    profile building, statistics, impact scoring
```

## Where the harness logic is specified

`docs/RUNBOOK-homelab.md` Phase 6 lists the 11 steps of one capture window in order.
Build to that. The two easy things to get wrong:

1. **Settle 180 s after boot, drain 120 s after the test suite.** Boot makes an event storm.
   Agent buffering means the tail arrives late. Cutting the window early loses real events.
2. **Mark the window with in-telemetry fences**, not host clock time. Run a uniquely named
   binary that emits one distinctive Sysmon EventID 1 at the start and end.

## Guard rail

Check free space on F: before every run and abort cleanly if low. Filling the disk 40 hours
into a 67 hour batch is the most expensive failure available.

"""The feasibility spike: its run plan and the batch runner (runbook Phase 7).

The plan is the smallest set of runs that answers the six spike questions, plus
one real C3 comparison so the whole method runs once on real data:

    S-ctl    5 control runs, Config S      Q1, Q2, Q3, Q4, Q5
    N-ctl    5 control runs, Config N      Q1 under Config N
    reboot   3 control runs, Config S,     Q6: does a post-change run's extra reboot
             with one extra reboot             leave a trace?
    C3-pre   3 runs before C3, Config S    the first real comparison (src/run.py)
    C3-post  3 runs after C3, Config S

The batch runner runs them in order. A run whose folder already holds a manifest is
skipped, so an interrupted batch can be started again. A voided run does not stop the
batch (it is recorded). A failed check before a run stops the batch, because it is a
lab problem (for example the host's lab address is missing) that every later run
would hit too.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .harness import HarnessError


@dataclass(frozen=True)
class PlannedRun:
    run_id: str
    group: str
    phase: str
    config: str                 # "S" Defender off after every boot, "N" as is
    change: str | None = None
    extra_reboot: bool = False


def spike_plan() -> list[PlannedRun]:
    plan = [PlannedRun(f"spike-S-ctl-{i}", "S-ctl", "control", "S") for i in range(1, 6)]
    plan += [PlannedRun(f"spike-N-ctl-{i}", "N-ctl", "control", "N") for i in range(1, 6)]
    plan += [PlannedRun(f"spike-S-reboot-{i}", "reboot", "control", "S", extra_reboot=True) for i in range(1, 4)]
    plan += [PlannedRun(f"spike-S-C3-pre-{i}", "C3-pre", "pre", "S") for i in range(1, 4)]
    plan += [PlannedRun(f"spike-S-C3-post-{i}", "C3-post", "post", "S", change="C3") for i in range(1, 4)]
    return plan


def _valid_dirs(runs_dir: Path, group: str) -> tuple[list[Path], int]:
    """The valid run folders of one plan group, and how many the plan has."""
    from .pipeline import load_run
    planned = [r for r in spike_plan() if r.group == group]
    good = []
    for r in planned:
        d = runs_dir / r.run_id
        if (d / "run_manifest.json").exists() and (d / "counts.json").exists() and load_run(d).valid:
            good.append(d)
    return good, len(planned)


def _not_enough(have: int, of: int) -> str:
    return f"not enough valid runs ({have} of {of})"


def analyse_spike(runs_dir: str | Path, out_dir: str | Path, rules_dir: str | Path | None,
                  analyser_version: str = "unknown") -> dict:
    """Answer the spike's Q1 to Q6 from the run folders, and run the C3 comparison.

    `analyser_version` is the git commit, written into the C3 reproducibility record.

    Writes, into out_dir: cov_control_runs.csv (Q1), run_timings.csv (Q2) and
    spike_answers.txt (all answers), plus the C3 report in out_dir/C3 when its runs exist.
    Each answer uses valid runs only and says so when there are too few.
    """
    import csv
    import itertools
    import statistics

    from .differential import MIN_PRE_COUNT, analyse
    from .model import Classification
    from .pipeline import PipelineError, compare, load_phase, load_run
    from .variance import VarianceModel

    runs_dir, out = Path(runs_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    groups = {g: _valid_dirs(runs_dir, g) for g in ["S-ctl", "N-ctl", "reboot", "C3-pre", "C3-post"]}
    answers: dict = {}

    # Q1: noise per key under Config S and Config N.
    answers["Q1"] = {}
    with (out / "cov_control_runs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["config", "key", "mean", "std", "cov", "dispersion", "n_runs"])
        for config, group in (("S", "S-ctl"), ("N", "N-ctl")):
            dirs, planned = groups[group]
            if len(dirs) < 3:
                answers["Q1"][config] = _not_enough(len(dirs), planned)
                continue
            phase, _, _ = load_phase(f"control-{config}", dirs)
            vm = VarianceModel.from_control(phase)
            for key in sorted(phase.counts):
                kv = vm.get(key)
                w.writerow([config, key, f"{kv.mean:.3f}", f"{kv.std:.3f}", f"{kv.cov:.4f}",
                            f"{kv.dispersion:.3f}", kv.n_runs])
            answers["Q1"][config] = {k: round(v, 4) for k, v in vm.summary().items()}

    # Q2: real time per run.
    timed = [(load_run(d).run_id, g, load_run(d).manifest["record"].get("run_seconds"))
             for g in ("S-ctl", "N-ctl", "reboot", "C3-pre", "C3-post") for d in groups[g][0]]
    timed = [t for t in timed if t[2] is not None]
    with (out / "run_timings.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["run_id", "group", "run_seconds"])
        w.writerows(timed)
    if timed:
        mean_min = statistics.mean(t[2] for t in timed) / 60
        answers["Q2"] = {"runs": len(timed), "mean_minutes": round(mean_min, 2),
                         "hours_for_101_runs": round(mean_min * 101 / 60, 1)}
    else:
        answers["Q2"] = "no timed runs"

    s_dirs, s_planned = groups["S-ctl"]
    if len(s_dirs) >= 3:
        s_phase, _, _ = load_phase("control-S", s_dirs)
        vm_s = VarianceModel.from_control(s_phase)
        keys = sorted(s_phase.counts)

        # Q3: every pair of control runs, one run on each side; any LOST or REDUCED is false.
        per_pair = []
        for a, b in itertools.combinations(s_dirs, 2):
            pa, _, _ = load_phase("a", [a], keys)
            pb, _, _ = load_phase("b", [b], keys)
            res = analyse(pa, pb, vm_s)
            bad = [f.key for f in res.findings if f.classification in (Classification.LOST, Classification.REDUCED)]
            per_pair.append({"pair": f"{a.name} vs {b.name}", "false_findings": bad})
        answers["Q3"] = {"pairs": len(per_pair), "false_findings": sum(len(p["false_findings"]) for p in per_pair),
                         "per_pair": per_pair}

        # Q4: keys with at least MIN_PRE_COUNT events over 3 runs.
        testable = [k for k in keys if s_phase.mean(k) * 3 >= MIN_PRE_COUNT]
        answers["Q4"] = {"keys": len(keys), "testable": len(testable),
                         "share": round(len(testable) / len(keys), 3) if keys else 0.0}

        # Q5: the stimulus fingerprint, process starts (Sysmon 1) per control run.
        fp = [sum(n for k, n in load_run(d).counts.items() if k.startswith("Sysmon-1[")) for d in s_dirs]
        mean_fp = statistics.mean(fp)
        answers["Q5"] = {"per_run": fp, "min": min(fp), "max": max(fp), "mean": round(mean_fp, 2),
                         "cov": round(statistics.stdev(fp) / mean_fp, 4) if len(fp) > 1 and mean_fp else 0.0}

        # Q6: control runs with one extra reboot, against the first three control runs.
        r_dirs, r_planned = groups["reboot"]
        if len(r_dirs) >= 3:
            keys6 = sorted(set(keys) | {k for d in r_dirs for k in load_run(d).counts})
            pre, _, _ = load_phase("control", s_dirs[:len(r_dirs)], keys6)
            post, _, _ = load_phase("reboot", r_dirs, keys6)
            res = analyse(pre, post, vm_s)
            moved = {c.value: [f.key for f in res.by_class(c)]
                     for c in (Classification.LOST, Classification.REDUCED, Classification.NEW)}
            answers["Q6"] = {"runs": len(r_dirs), "lost_or_reduced": len(moved["LOST"]) + len(moved["REDUCED"]),
                             "new": len(moved["NEW"]), "keys": moved}
        else:
            answers["Q6"] = _not_enough(len(r_dirs), r_planned)
    else:
        for q in ("Q3", "Q4", "Q5"):
            answers[q] = _not_enough(len(s_dirs), s_planned)
        answers["Q6"] = _not_enough(len(groups["reboot"][0]), groups["reboot"][1])

    # The C3 comparison through the whole pipeline.
    (pre_d, pre_n), (post_d, post_n) = groups["C3-pre"], groups["C3-post"]
    if len(pre_d) < 3 or len(post_d) < 3 or len(s_dirs) < 3:
        answers["C3"] = f"not enough valid runs (C3-pre {len(pre_d)} of {pre_n}, C3-post {len(post_d)} of {post_n})"
    elif rules_dir is None:
        answers["C3"] = "no rule export given"
    else:
        try:
            res = compare(s_dirs, pre_d, post_d, rules_dir, out / "C3", analyser_version=analyser_version)
            answers["C3"] = {"report": str(res.files["report"]), "ranked": [h.key for h in res.ranked],
                             "coverage_lost": res.coverage_lost}
        except PipelineError as exc:
            answers["C3"] = f"cannot compare: {exc}"

    lines = ["TeLoS feasibility spike: answers (runbook Phase 7)", ""]
    for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "C3"):
        a = answers[q]
        if q == "Q3" and isinstance(a, dict):
            a = {k: v for k, v in a.items() if k != "per_pair"}
        lines.append(f"{q}: {a}")
    (out / "spike_answers.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return answers


def run_batch(plan: list[PlannedRun], runs_dir: str | Path, capture_one: Callable[[PlannedRun], dict],
              log: Callable[..., None] = print) -> list[dict]:
    """Run each planned run in order; returns one summary line per run reached."""
    runs_dir = Path(runs_dir)
    summary: list[dict] = []
    for i, run in enumerate(plan, 1):
        if (runs_dir / run.run_id / "run_manifest.json").exists():
            summary.append({"run_id": run.run_id, "status": "skipped (exists)"})
            log(f"[{i}/{len(plan)}] {run.run_id}: skipped, already exists")
            continue
        log(f"[{i}/{len(plan)}] {run.run_id}: {run.group}, phase {run.phase}, config {run.config}"
            + (f", change {run.change}" if run.change else "") + (", extra reboot" if run.extra_reboot else ""))
        try:
            m = capture_one(run)
        except HarnessError as exc:
            summary.append({"run_id": run.run_id, "status": f"STOPPED: {exc}"})
            log(f"    STOPPED, before producing data: {exc}")
            break
        r = m["record"]
        status = "valid" if r["valid"] else "VOID"
        summary.append({"run_id": run.run_id, "status": status, "void_reasons": r.get("void_reasons", []),
                        "run_seconds": r.get("run_seconds")})
        log(f"    {status}" + (f": {r['void_reasons']}" if not r["valid"] else "")
            + (f"   ({r.get('run_seconds', 0) / 60:.1f} min)" if r.get("run_seconds") else ""))
    return summary

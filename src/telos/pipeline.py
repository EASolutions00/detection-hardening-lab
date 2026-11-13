"""The pipeline: run folders in, report and exports out.

The harness writes one folder per capture window (`counts.json`, `run_manifest.json`).
This module reads the folders of one comparison (the control runs, the runs before
the change, the runs after it), checks that they belong together, runs the whole
method, and writes three files:

    report.txt       verdict, noise floor, telemetry comparison, ranked blind spots,
                     coverage change
    findings.json    the ranked findings, for a ticketing system
    comparison.csv   one row per event key
    navigator_layer.json   the coverage change as an ATT&CK Navigator layer (format 4.5)

Checks, each a reason the comparison would otherwise be wrong:
- **Voided runs are left out** and named (the harness voids a run whose tests ran
  past the window, whose change was not confirmed, or whose window could not be read).
- **Each phase needs at least `min_runs` valid runs** (3 by design; blueprint).
- **Every run must have the same `parameters` hash.** Runs with different settings
  (window, snapshot, attack list, rule set) are not comparable (runbook step 11).
- **All "after" runs must be of one change.**
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .differential import analyse
from .impact import ImpactFinding, rank_impact
from .index import build_index, load_rules
from .model import AnalysisResult, Phase
from .report import (comparison_csv, coverage_change, findings_json, load_controls, navigator_layer,
                     remediation_level2, render_analysis, render_coverage, render_impact, render_remediation2,
                     render_reproducibility, render_variance, render_verdict)
from .variance import VarianceModel


class PipelineError(RuntimeError):
    """The run folders cannot be compared as given."""


@dataclass
class RunData:
    run_id: str
    path: Path
    manifest: dict
    counts: dict[str, int]
    fired: dict[str, int]

    @property
    def valid(self) -> bool:
        return bool(self.manifest.get("record", {}).get("valid", False))

    @property
    def params_hash(self) -> str:
        return self.manifest.get("parameters_sha256", "")

    @property
    def change_id(self) -> str | None:
        return self.manifest.get("record", {}).get("change_id")


def load_run(run_dir: str | Path) -> RunData:
    d = Path(run_dir)
    counts = json.loads((d / "counts.json").read_text(encoding="utf-8"))
    manifest = json.loads((d / "run_manifest.json").read_text(encoding="utf-8"))
    return RunData(run_id=counts.get("run_id", d.name), path=d, manifest=manifest,
                   counts=counts.get("counts", {}), fired=counts.get("fired", {}))


def load_phase(name: str, run_dirs: list, keys: list[str] | None = None,
               window_minutes: float = 15.0) -> tuple[Phase, dict[str, int], list[RunData]]:
    """One phase from run folders: counts per key (0 where a run lacks the key), and
    the fired rules summed over the runs."""
    runs = [load_run(d) for d in run_dirs]
    keys = keys if keys is not None else sorted({k for r in runs for k in r.counts})
    phase = Phase(name=name, counts={k: [r.counts.get(k, 0) for r in runs] for k in keys},
                  window_minutes=window_minutes)
    fired: dict[str, int] = {}
    for r in runs:
        for rid, n in r.fired.items():
            fired[rid] = fired.get(rid, 0) + int(n)
    return phase, fired, runs


@dataclass
class ComparisonOutput:
    result: AnalysisResult
    ranked: list[ImpactFinding]
    coverage_lost: list[str]
    files: dict[str, Path]
    left_out: list[str]


def _valid(name: str, runs: list[RunData], min_runs: int) -> list[RunData]:
    good = [r for r in runs if r.valid]
    if len(good) < min_runs:
        bad = ", ".join(r.run_id for r in runs if not r.valid) or "none"
        raise PipelineError(f"{name} has {len(good)} valid runs, needs {min_runs}; left out: {bad}")
    return good


def compare(control_dirs: list, pre_dirs: list, post_dirs: list, rules_dir: str | Path,
            out_dir: str | Path, min_runs: int = 3, analyser_version: str = "unknown",
            controls_path: str | Path | None = None) -> ComparisonOutput:
    """Run the whole method on one comparison and write the report and exports.

    `analyser_version` is the git commit of the repository (src/run.py reads it).
    `controls_path` is the curated list for remediation level 2
    (lab/knowledge/compensating-controls.json); without it the level is left out."""
    groups = {"control": [load_run(d) for d in control_dirs],
              "pre": [load_run(d) for d in pre_dirs],
              "post": [load_run(d) for d in post_dirs]}
    left_out = [r.run_id for runs in groups.values() for r in runs if not r.valid]
    valid = {name: _valid(name, runs, min_runs) for name, runs in groups.items()}

    hashes = {r.params_hash for runs in valid.values() for r in runs}
    if len(hashes) != 1:
        raise PipelineError(f"runs are not comparable: {len(hashes)} different parameters hashes")
    changes = {r.change_id for r in valid["post"]}
    if len(changes) != 1:
        raise PipelineError(f"the after runs belong to more than one change: {sorted(map(str, changes))}")

    params = valid["pre"][0].manifest.get("parameters", {})
    window_minutes = float(params.get("window_s", 900)) / 60.0
    keys = sorted({k for runs in valid.values() for r in runs for k in r.counts})
    control, _, _ = load_phase("control", [r.path for r in valid["control"]], keys, window_minutes)
    pre, fired_pre, _ = load_phase("pre", [r.path for r in valid["pre"]], keys, window_minutes)
    post, fired_post, _ = load_phase("post", [r.path for r in valid["post"]], keys, window_minutes)

    vm = VarianceModel.from_control(control, min_runs=min_runs)
    result = analyse(pre, post, vm)
    index = build_index(load_rules(rules_dir))
    ranked = rank_impact(result, post, index, fired_after=fired_post)
    before, after, lost = coverage_change(fired_pre, fired_post, index)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    header = [f"Change: {next(iter(changes))}   parameters sha256: {next(iter(hashes))}",
              f"Runs: control {len(valid['control'])}, before {len(valid['pre'])}, after {len(valid['post'])}"
              + (f"   left out (voided): {', '.join(left_out)}" if left_out else ""), ""]
    repro = {"parameters": params, "parameters_sha256": next(iter(hashes)),
             "analyser_version": analyser_version,
             "runs": [{"phase": name, "run_id": r.run_id, "valid": r.valid, "change_id": r.change_id,
                       "folder": str(r.path)} for name, runs in groups.items() for r in runs]}
    sections = [render_verdict(result, ranked), render_variance(vm), render_analysis(result),
                render_impact(ranked), render_coverage(before, after, lost)]
    level2: list[dict] = []
    if controls_path is not None:
        blind = {t for h in ranked for t in h.blind_techniques} | set(lost)
        level2 = remediation_level2(load_controls(controls_path), next(iter(changes)), blind)
        sections.append(render_remediation2(next(iter(changes)), level2))
        repro["controls_file"] = str(controls_path)
    sections.append(render_reproducibility(repro))
    report = "\n".join(header + sections)
    files = {"report": out / "report.txt", "findings": out / "findings.json", "csv": out / "comparison.csv",
             "navigator": out / "navigator_layer.json"}
    files["report"].write_text(report, encoding="utf-8")
    data = json.loads(findings_json(result, ranked, lost, repro))
    if controls_path is not None:
        data["remediation_level_2"] = level2
    files["findings"].write_text(json.dumps(data, indent=2), encoding="utf-8")
    files["csv"].write_text(comparison_csv(result), encoding="utf-8")
    files["navigator"].write_text(navigator_layer(f"TeLoS {next(iter(changes))}", before, after, ranked),
                                  encoding="utf-8")
    return ComparisonOutput(result=result, ranked=ranked, coverage_lost=lost, files=files, left_out=left_out)

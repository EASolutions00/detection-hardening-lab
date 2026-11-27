"""The pipeline: run folders in, report and exports out.

The harness writes one folder per capture window (`counts.json`, `run_manifest.json`).
This module reads the folders of one comparison (the control runs, the runs before
the change, the runs after it), checks that they belong together, runs the whole
method, and writes three files:

    report.txt       verdict, Myers comparison (step 3), noise floor, telemetry
                     comparison, ranked blind spots, coverage change
    findings.json    the ranked findings, for a ticketing system
    comparison.csv   one row per event key
    navigator_layer.json   the coverage change as an ATT&CK Navigator layer (format 4.5)

Checks, each a reason the comparison would otherwise be wrong:
- **Voided runs are left out** and named (the harness voids a run whose tests ran
  past the window, whose change was not confirmed, or whose window could not be read,
  and, since 2026-11-27, a run outside item 22's void rule; `harness.RunChecks`).
- **Each phase needs at least `min_runs` valid runs** (3 by design; blueprint).
- **Every run's stored parameters hash must equal the hash of its own parameters**, recomputed here
  (since 2026-11-28; outside review, point 12), so an edited manifest is refused.
- **Every run must have the same `parameters` hash.** Runs with different settings
  (window, snapshot, attack list, rule set) are not comparable (runbook step 11). The error
  names the parameters that differ.
- **The rule export must be the one the runs were captured with:** its SHA256 is computed from the
  folder given (`rulehash.rule_folder_sha256`) and compared with `rule_folder_sha256` in the runs'
  parameters, when they have one (since 2026-11-28).
- **All "after" runs must be of one change.**

The hash covers the parameters only. Each run's code version, its run checks and the analysis settings are
recorded beside it, in the reproducibility record (DECISIONS 2026-11-28).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .differential import ALPHA, MAX_RATIO, MIN_PRE_COUNT, NOISE_SIGMAS, analyse
from .harness import parameters_hash
from .impact import ImpactFinding, rank_impact
from .index import build_index, load_rules
from .model import AnalysisResult, Phase
from .myers import MyersComparison, compare_phases, render_myers
from .report import (comparison_csv, coverage_change, findings_json, load_controls, navigator_layer,
                     remediation_level2, render_analysis, render_coverage, render_impact, render_remediation2,
                     render_reproducibility, render_variance, render_verdict)
from .rulehash import rule_folder_sha256
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
    myers: MyersComparison | None = None


def _differing_fields(runs: list[RunData]) -> str:
    """The parameters whose values differ between runs, for the "not comparable" error."""
    names = sorted({k for r in runs for k in r.manifest.get("parameters", {})})
    out = []
    for k in names:
        values = {json.dumps(r.manifest.get("parameters", {}).get(k, "<missing>"), sort_keys=True) for r in runs}
        if len(values) > 1:
            out.append(f"{k} ({len(values)} values)")
    return ", ".join(out)


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

    used = [r for runs in valid.values() for r in runs]
    for r in used:                      # the stored hash must be the hash of the run's own parameters
        recomputed = parameters_hash(r.manifest.get("parameters", {}))
        if recomputed != r.params_hash:
            raise PipelineError(f"{r.run_id}: its parameters do not match its stored hash "
                                f"({r.params_hash[:8] or 'none'} stored, {recomputed[:8]} recomputed): "
                                "the manifest was changed or damaged")
    hashes = {r.params_hash for r in used}
    if len(hashes) != 1:
        raise PipelineError(f"runs are not comparable: {len(hashes)} different parameters hashes; "
                            f"parameters that differ: {_differing_fields(used) or 'none found'}")
    changes = {r.change_id for r in valid["post"]}
    if len(changes) != 1:
        raise PipelineError(f"the after runs belong to more than one change: {sorted(map(str, changes))}")

    params = valid["pre"][0].manifest.get("parameters", {})
    # The rule export read below must be the one the runs were captured with: computed from the files, not typed.
    try:
        rules_sha = rule_folder_sha256(rules_dir)
    except ValueError as exc:                       # a missing folder: say so, no traceback
        raise PipelineError(f"cannot read the rule export: {exc}") from exc
    pinned = params.get("rule_folder_sha256")
    if pinned is not None and str(pinned) != rules_sha:
        raise PipelineError(f"the rule export in {rules_dir} (SHA256 {rules_sha[:8]}...) is not the one the runs were "
                            f"captured with ({str(pinned)[:8]}...): the index and the ranking would read other rules")
    rule_export = {"folder": str(rules_dir), "sha256": rules_sha, "pinned_in_runs": pinned,
                   "matches_runs": None if pinned is None else True}
    window_minutes = float(params.get("window_s", 900)) / 60.0
    keys = sorted({k for runs in valid.values() for r in runs for k in r.counts})
    control, _, _ = load_phase("control", [r.path for r in valid["control"]], keys, window_minutes)
    pre, fired_pre, _ = load_phase("pre", [r.path for r in valid["pre"]], keys, window_minutes)
    post, fired_post, _ = load_phase("post", [r.path for r in valid["post"]], keys, window_minutes)

    # Step 3: Myers on the sorted event lists, each phase's runs joined (DECISIONS 2026-11-26).
    myers = compare_phases([r.counts for r in valid["control"]], [r.counts for r in valid["pre"]],
                           [r.counts for r in valid["post"]])
    # Step 4: which differences are larger than the noise floor.
    vm = VarianceModel.from_control(control, min_runs=min_runs)
    result = analyse(pre, post, vm)
    index = build_index(load_rules(rules_dir))
    ranked = rank_impact(result, post, index, fired_after=fired_post, fired_before=fired_pre)
    before, after, lost = coverage_change(fired_pre, fired_post, index)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    header = [f"Change: {next(iter(changes))}   parameters sha256: {next(iter(hashes))}",
              f"Runs: control {len(valid['control'])}, before {len(valid['pre'])}, after {len(valid['post'])}"
              + (f"   left out (voided): {', '.join(left_out)}" if left_out else ""), ""]
    repro = {"parameters": params, "parameters_sha256": next(iter(hashes)),
             "analyser_version": analyser_version,
             "rule_export": rule_export,
             "analysis_settings": {"alpha": ALPHA, "max_ratio": MAX_RATIO, "min_pre_count": MIN_PRE_COUNT,
                                   "noise_sigmas": NOISE_SIGMAS, "min_control_runs": min_runs},
             "runs": [{"phase": name, "run_id": r.run_id, "valid": r.valid, "change_id": r.change_id,
                       "code_commit": r.manifest.get("record", {}).get("code_commit"),
                       "code_dirty": r.manifest.get("record", {}).get("code_dirty"),
                       "folder": str(r.path)} for name, runs in groups.items() for r in runs]}
    sections = [render_verdict(result, ranked), render_myers(myers), render_variance(vm), render_analysis(result),
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
    data["myers"] = myers.to_dict()
    if controls_path is not None:
        data["remediation_level_2"] = level2
    files["findings"].write_text(json.dumps(data, indent=2), encoding="utf-8")
    files["csv"].write_text(comparison_csv(result), encoding="utf-8")
    files["navigator"].write_text(navigator_layer(f"TeLoS {next(iter(changes))}", before, after, ranked),
                                  encoding="utf-8")
    return ComparisonOutput(result=result, ranked=ranked, coverage_lost=lost, files=files, left_out=left_out,
                            myers=myers)

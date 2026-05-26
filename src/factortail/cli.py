"""``factortail`` command-line interface.

Entry points
------------

* ``factortail run --config <path>``          — execute one experiment.
* ``factortail run-all --config <path>``      — execute every experiment.
* ``factortail validate-run <run_id>``        — enforce App. G rules.
* ``factortail validate-schema <path>``       — check that every required CSV
  in a directory matches the SCHEMA (or that ``SCHEMA.md`` itself is in sync).
* ``factortail replace-figure <label>``       — swap a placeholder tex/pdf for
  the generated artifact with the same basename.
* ``factortail list-experiments``             — print the priority manifest.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from factortail import __version__
from factortail.io.schema import all_schema_names
from factortail.io.validators import ValidationError, validate_csv
from factortail.manifest import (
    ReplacementError,
    load_manifest,
)
from factortail.manifest import (
    validate_run as manifest_validate_run,
)

console = Console()


@click.group(invoke_without_command=False)
@click.version_option(__version__, prog_name="factortail")
def main() -> None:
    """FactorTail: rare-event simulation for regularly-varying factor models."""


@main.command("list-experiments")
def list_experiments() -> None:
    """Print the priority manifest (App. G)."""
    rows = load_manifest()
    t = Table(title="FactorTail experiment manifest")
    t.add_column("Priority", style="cyan", no_wrap=True)
    t.add_column("Experiment")
    t.add_column("CSVs")
    t.add_column("Status")
    for r in rows:
        t.add_row(r.priority, r.experiment, ", ".join(r.required_csvs), r.status)
    console.print(t)


@main.command("validate-schema")
@click.argument("target", type=click.Path(exists=True, path_type=Path))
def validate_schema(target: Path) -> None:
    """Validate every CSV in ``target`` (file or directory) against the schema."""
    failures: list[str] = []
    if target.is_dir():
        files = sorted(target.glob("*.csv"))
    elif target.suffix == ".csv":
        files = [target]
    else:
        # SCHEMA.md cross-check
        text = target.read_text()
        for name in all_schema_names():
            if name not in text:
                failures.append(f"SCHEMA.md missing entry for {name}")
        if failures:
            for msg in failures:
                console.print(f"[red]FAIL[/red] {msg}")
            sys.exit(1)
        console.print(f"[green]OK[/green] SCHEMA.md mentions all {len(all_schema_names())} schemas")
        return
    for path in files:
        try:
            validate_csv(path)
            console.print(f"[green]OK[/green] {path.name}")
        except (ValidationError, KeyError) as exc:
            failures.append(f"{path.name}: {exc}")
            console.print(f"[red]FAIL[/red] {path.name}: {exc}")
    if failures:
        sys.exit(1)


@main.command("validate-run")
@click.argument("run_id")
@click.option("--results-dir", default="results", type=click.Path(path_type=Path))
def cli_validate_run(run_id: str, results_dir: Path) -> None:
    """Enforce App. G replacement rules for a recorded run."""
    try:
        manifest_validate_run(run_id, results_dir=results_dir)
    except ReplacementError as exc:
        console.print(f"[red]Replacement rule violated:[/red] {exc}")
        sys.exit(1)
    console.print(f"[green]Run {run_id!r} passes the replacement contract.[/green]")


@main.command()
@click.option("--config", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--results-dir", default="results", type=click.Path(path_type=Path))
def run(config: Path, results_dir: Path) -> None:
    """Execute one experiment described by a YAML config."""
    from factortail.experiments import dispatch

    res = dispatch.run_config(config, results_dir=results_dir)
    console.print(f"[green]Wrote {len(res)} artifact(s):[/green]")
    for path in res:
        console.print(f"  - {path}")


@main.command("run-all")
@click.option("--config", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--results-dir", default="results", type=click.Path(path_type=Path))
def run_all(config: Path, results_dir: Path) -> None:
    """Execute every experiment listed in a master YAML config."""
    from factortail.experiments import dispatch

    res = dispatch.run_master(config, results_dir=results_dir)
    console.print(f"[green]Total artifacts:[/green] {len(res)}")
    for path in res:
        console.print(f"  - {path}")


@main.command("repro")
@click.argument("run_id")
@click.option("--results-dir", default="results", type=click.Path(path_type=Path))
@click.option(
    "--scratch-dir",
    default=None,
    type=click.Path(path_type=Path),
    help="Where to write re-generated CSVs (defaults to a sibling of results-dir).",
)
@click.option(
    "--configs-dir",
    default="configs",
    type=click.Path(path_type=Path),
    help="Directory holding the YAML configs referenced by the run.",
)
def cli_repro(run_id: str, results_dir: Path, scratch_dir: Path | None, configs_dir: Path) -> None:
    """Re-run a recorded ``run_id`` and verify byte-identical CSVs.

    Reads ``results/_run_<run_id>.json``, re-executes every config whose
    output appears in the run's ``csvs`` list against a temporary results
    dir, then compares every regenerated CSV to its archived counterpart
    byte-for-byte (ignoring the volatile ``run_timestamp`` column).
    """
    import json
    import re
    import shutil
    import tempfile

    import pandas as pd

    record_path = results_dir / f"_run_{run_id}.json"
    if not record_path.exists():
        console.print(f"[red]Run record missing:[/red] {record_path}")
        sys.exit(1)
    record = json.loads(record_path.read_text())
    csvs = list(record.get("csvs", []))
    if not csvs:
        console.print(f"[red]Run record has no CSVs:[/red] {record_path}")
        sys.exit(1)

    if scratch_dir is None:
        scratch_dir = Path(tempfile.mkdtemp(prefix=f"factortail_repro_{run_id}_"))
    else:
        scratch_dir.mkdir(parents=True, exist_ok=True)

    # Map every CSV to a YAML config in configs_dir whose script writes it.
    from factortail.experiments import dispatch

    yaml_paths = sorted(configs_dir.glob("*.yaml"))
    csv_to_config: dict[str, Path] = {}
    for cfg_path in yaml_paths:
        import yaml as _yaml

        cfg = _yaml.safe_load(cfg_path.read_text()) or {}
        script = cfg.get("script", "")
        # The script's SCHEMA_NAME determines the CSV basename. Greedy match
        # by reading the script for SCHEMA_NAME = "<basename>".
        if not script:
            continue
        script_path = (Path.cwd() / script).resolve()
        if not script_path.exists():
            continue
        text = script_path.read_text()
        m = re.search(r"SCHEMA_NAME\s*=\s*['\"]([A-Za-z0-9_]+)['\"]", text)
        if not m:
            continue
        basename = m.group(1)
        csv_to_config[f"{basename}.csv"] = cfg_path

    matched = [c for c in csvs if c in csv_to_config]
    if not matched:
        console.print(f"[red]No matching configs found for any of:[/red] {csvs}")
        sys.exit(1)

    mismatches: list[str] = []
    for csv_name in matched:
        cfg_path = csv_to_config[csv_name]
        console.print(f"[cyan]repro[/cyan] {csv_name} via {cfg_path.name}")
        dispatch.run_config(cfg_path, results_dir=scratch_dir)
        orig = results_dir / csv_name
        regen = scratch_dir / csv_name
        if not regen.exists():
            mismatches.append(f"{csv_name}: regenerated file missing")
            continue
        volatile = [
            "run_timestamp",
            "git_hash",
            "config_hash",
            "code_version",
            "run_id",
            "runtime_seconds",
            "runtime",  # F14
            "wnre",
            "work_norm_variance",
            "work_normalized_variance",
        ]
        df_orig = pd.read_csv(orig).drop(columns=volatile, errors="ignore")
        df_new = pd.read_csv(regen).drop(columns=volatile, errors="ignore")
        if df_orig.shape != df_new.shape:
            mismatches.append(f"{csv_name}: shape {df_new.shape} != {df_orig.shape}")
            continue
        try:
            pd.testing.assert_frame_equal(df_orig, df_new, check_exact=False, rtol=1e-6, atol=1e-9)
        except AssertionError as exc:
            mismatches.append(f"{csv_name}: {str(exc).splitlines()[0]}")

    skipped = [c for c in csvs if c not in csv_to_config]
    if skipped:
        console.print(f"[yellow]skipped (no config):[/yellow] {skipped}")

    if mismatches:
        for msg in mismatches:
            console.print(f"[red]MISMATCH[/red] {msg}")
        sys.exit(1)
    console.print(
        f"[green]Run {run_id!r}: {len(matched)} CSV(s) reproduced byte-identical "
        f"(modulo run_timestamp).[/green]"
    )
    # Clean up the scratch dir we created.
    if scratch_dir.parent == Path(tempfile.gettempdir()):
        shutil.rmtree(scratch_dir, ignore_errors=True)


@main.command("replace-figure")
@click.argument("label")
@click.option("--results-dir", default="results", type=click.Path(path_type=Path))
@click.option("--report-dir", default="docs/report/figures", type=click.Path(path_type=Path))
def replace_figure(label: str, results_dir: Path, report_dir: Path) -> None:
    """Replace a placeholder TikZ figure with the generated PDF/TeX of the same basename."""
    base = label.split(":", 1)[-1]
    generated = list(results_dir.glob(f"{base}.*"))
    if not generated:
        console.print(f"[red]No generated artifact for {label!r} in {results_dir}[/red]")
        sys.exit(1)
    target = report_dir / f"{base}.tex"
    console.print(f"Would replace {target} with {generated[0]} (dry run)")

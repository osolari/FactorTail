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

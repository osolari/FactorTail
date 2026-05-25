"""Implementation of the App. G replacement contract."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from factortail.io.validators import validate_csv

__all__ = [
    "PriorityRow",
    "ReplacementError",
    "load_manifest",
    "record_run",
    "validate_run",
]


class ReplacementError(RuntimeError):
    """Raised when the manuscript replacement contract is violated."""


@dataclass
class PriorityRow:
    """A row of the seven-row priority manifest (App. G)."""

    priority: str
    experiment: str
    required_csvs: tuple[str, ...]
    placeholder_labels: tuple[str, ...]
    status: str = "planned"

    def to_dict(self) -> dict:
        return asdict(self)


_DEFAULT_MANIFEST: list[PriorityRow] = [
    PriorityRow(
        priority="P1",
        experiment="Independent replication",
        required_csvs=(
            "F1_tail_equivalence.csv",
            "F8_second_order.csv",
            "T_sim_results_independent.csv",
        ),
        placeholder_labels=(
            "fig:ind-tail-equivalence",
            "fig:second-order-placeholder",
            "tab:sim-results-independent",
        ),
    ),
    PriorityRow(
        priority="P2",
        experiment="Common-shock simulation",
        required_csvs=("F11_common_shock_geometry.csv", "T_sim_results_dependent.csv"),
        placeholder_labels=("fig:common-shock-geometry", "tab:sim-results-dependent"),
    ),
    PriorityRow(
        priority="P3",
        experiment="Copula-kernel test",
        required_csvs=("T_sim_results_dependent.csv",),
        placeholder_labels=("tab:sim-results-dependent",),
    ),
    PriorityRow(
        priority="P4",
        experiment="MRV spectral test",
        required_csvs=("F12_spectral_simplex.csv", "T_sim_results_dependent.csv"),
        placeholder_labels=("fig:spectral-simplex-placeholder", "tab:sim-results-dependent"),
    ),
    PriorityRow(
        priority="P5",
        experiment="Hidden-cone test",
        required_csvs=("F13_hidden_cones.csv", "T_sim_results_dependent.csv"),
        placeholder_labels=("fig:hidden-cones-placeholder", "tab:sim-results-dependent"),
    ),
    PriorityRow(
        priority="P6",
        experiment="Public Fama-French data",
        required_csvs=(
            "F15_tail_dependence_heatmap.csv",
            "F16_var_es_dashboard.csv",
            "F17_spectral_by_period.csv",
            "F18_hill_plots.csv",
            "T_data_panels.csv",
            "T_tail_index_placeholder.csv",
            "T_dependence_diagnostic_placeholder.csv",
            "T_var_es_backtest_placeholder.csv",
            "T_crisis_attribution_placeholder.csv",
        ),
        placeholder_labels=(
            "tab:data-panels",
            "tab:tail-index-placeholder",
            "tab:tail-dep-placeholder",
            "tab:var-es-backtest-placeholder",
            "tab:crisis-attribution-placeholder",
            "fig:tail-dep-heatmap-placeholder",
            "fig:var-es-dashboard-placeholder",
            "fig:spectral-by-period-placeholder",
            "fig:hill-plots-placeholder",
        ),
    ),
    PriorityRow(
        priority="P7",
        experiment="CRSP licensed extension",
        required_csvs=("F15_tail_dependence_heatmap.csv", "F16_var_es_dashboard.csv"),
        placeholder_labels=("fig:tail-dep-heatmap-placeholder", "fig:var-es-dashboard-placeholder"),
        status="optional/planned",
    ),
]


def load_manifest(path: str | Path | None = None) -> list[PriorityRow]:
    """Load the priority manifest from YAML, or return the default seven rows."""
    if path is None:
        return list(_DEFAULT_MANIFEST)
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    data = yaml.safe_load(p.read_text())
    rows: list[PriorityRow] = []
    for row in data["rows"]:
        rows.append(
            PriorityRow(
                priority=row["priority"],
                experiment=row["experiment"],
                required_csvs=tuple(row["required_csvs"]),
                placeholder_labels=tuple(row["placeholder_labels"]),
                status=row.get("status", "planned"),
            )
        )
    return rows


@dataclass
class RunRecord:
    run_id: str
    priority: str
    config_hash: str
    git_hash: str
    seed: int
    csvs: tuple[str, ...]
    timestamp: str = ""
    notes: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2)


def record_run(
    run_id: str,
    *,
    priority: str,
    config_hash: str,
    git_hash: str,
    seed: int,
    csvs: Iterable[str],
    results_dir: str | Path = "results",
    notes: str = "",
) -> Path:
    """Write a ``RunRecord`` JSON next to the generated CSVs."""
    from datetime import datetime, timezone

    rec = RunRecord(
        run_id=run_id,
        priority=priority,
        config_hash=config_hash,
        git_hash=git_hash,
        seed=seed,
        csvs=tuple(csvs),
        timestamp=datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        notes=notes,
    )
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    out = results_dir / f"_run_{run_id}.json"
    out.write_text(rec.to_json())
    return out


def validate_run(run_id: str, *, results_dir: str | Path = "results") -> None:
    """Enforce App. G replacement rules for ``run_id``."""
    results_dir = Path(results_dir)
    record_path = results_dir / f"_run_{run_id}.json"
    if not record_path.exists():
        raise ReplacementError(f"Run record missing: {record_path}")
    record = json.loads(record_path.read_text())
    for required in ("run_id", "priority", "config_hash", "git_hash", "seed"):
        if required not in record or record[required] in (None, ""):
            raise ReplacementError(f"Run record {run_id!r} missing field {required!r}")
    for csv_name in record["csvs"]:
        csv_path = results_dir / csv_name
        if not csv_path.exists():
            raise ReplacementError(f"CSV missing for {run_id}: {csv_path}")
        validate_csv(csv_path)

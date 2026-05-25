"""Dispatch YAML configs to ``scripts/generate_*.py`` entry points."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import yaml

__all__ = ["run_config", "run_master"]


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def _import_script(script_path: Path):
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_config(config_path: Path, *, results_dir: Path) -> list[Path]:
    """Execute the single experiment described by ``config_path``."""
    cfg = _load_yaml(config_path)
    script = Path(cfg["script"])
    if not script.is_absolute():
        script = Path.cwd() / script
    module = _import_script(script)
    if not hasattr(module, "run"):
        raise AttributeError(f"{script}: expected a ``run(config, results_dir)`` entry point")
    out = module.run(config=cfg, results_dir=results_dir)
    return list(out) if isinstance(out, (list, tuple)) else [out]


def run_master(master_path: Path, *, results_dir: Path) -> list[Path]:
    """Execute every experiment listed in a master YAML."""
    master = _load_yaml(master_path)
    artifacts: list[Path] = []
    for sub_cfg in master.get("experiments", []):
        sub_path = Path(sub_cfg) if isinstance(sub_cfg, str) else None
        if sub_path is not None:
            if not sub_path.is_absolute():
                sub_path = Path.cwd() / sub_path
            artifacts.extend(run_config(sub_path, results_dir=results_dir))
        else:
            # Inline config dict.
            script = Path(sub_cfg["script"])
            if not script.is_absolute():
                script = Path.cwd() / script
            module = _import_script(script)
            out = module.run(config=sub_cfg, results_dir=results_dir)
            artifacts.extend(list(out) if isinstance(out, (list, tuple)) else [out])
    return artifacts

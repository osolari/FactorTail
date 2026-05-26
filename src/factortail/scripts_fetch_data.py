"""Wheel-installable entry point for the data-fetch script.

The real implementation is :mod:`scripts.fetch_data` so it can be run
directly from a source checkout via ``python scripts/fetch_data.py``.
This module re-exports a ``main()`` so the entry point declared in
``pyproject.toml`` (``factortail-fetch-data = factortail.scripts_fetch_data:main``)
works after ``pip install``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from factortail.real_data.fama_french import load_fama_french

FF_PANELS = {
    "FF3_daily": (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "F-F_Research_Data_Factors_daily_CSV.zip"
    ),
    "FF5_daily": (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
    ),
    "Momentum_daily": (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "F-F_Momentum_Factor_daily_CSV.zip"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and cache the Fama-French daily panels.")
    parser.add_argument(
        "--panels",
        nargs="+",
        default=list(FF_PANELS.keys()),
        choices=list(FF_PANELS.keys()),
    )
    parser.add_argument("--cache-dir", default="data/raw")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip the live download; emit synthetic panels instead.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the local CSV exists.",
    )
    args = parser.parse_args()

    cache = Path(args.cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    print(f"[factortail-fetch] target cache: {cache.resolve()}")
    n_ok = 0
    n_fail = 0
    for name in args.panels:
        url = FF_PANELS[name]
        if args.force:
            stale = cache / f"{name}.csv"
            if stale.exists():
                stale.unlink()
        try:
            panel = load_fama_french(
                name=name,
                cache_dir=cache,
                url=url,
                offline=args.offline,
                n_synthetic=5000,
                rng_seed=0,
            )
            print(
                f"  OK   {name:18s}  n={panel.n_obs:>6d}"
                f"  {panel.start_date.date()}..{panel.end_date.date()}"
                f"  sha256={panel.checksum[:12]}"
            )
            n_ok += 1
        except Exception as exc:  # - tolerant
            print(f"  FAIL {name:18s}  {type(exc).__name__}: {str(exc)[:80]}")
            n_fail += 1

    print(f"[factortail-fetch] done — {n_ok} ok, {n_fail} failed")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

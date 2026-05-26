"""Download and cache every external dataset FactorTail needs.

This is the one-shot data fetch:

- Kenneth French Data Library: FF3 / FF5 / Momentum daily panels.

The script is **idempotent**: it skips files that already exist with
matching SHA-256, so re-running is cheap.

It is wired to run automatically after `pip install`-time hooks via:

- the `factortail-fetch-data` console-script entry point (so the user
  can rerun manually),
- a `post_install` hint in the dev workflow (running ``make dev`` invokes
  this script after the editable install), and
- a CI step in `.github/workflows/ci.yml`.

Usage:

    python scripts/fetch_data.py            # default: all FF panels, offline-fallback if no net
    python scripts/fetch_data.py --offline  # skip the live downloads (synthesize only)
    python scripts/fetch_data.py --panels FF3_daily FF5_daily
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

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
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--panels",
        nargs="+",
        default=list(FF_PANELS.keys()),
        choices=list(FF_PANELS.keys()),
        help="Subset of panels to fetch.",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(REPO_ROOT / "data" / "raw"),
        help="Local cache directory.",
    )
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
    print(f"[factortail-fetch] target cache: {cache}")
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
        except Exception as exc:  # - one-shot fetch tolerates any failure
            print(f"  FAIL {name:18s}  {type(exc).__name__}: {str(exc)[:80]}")
            n_fail += 1

    print(f"[factortail-fetch] done — {n_ok} ok, {n_fail} failed")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

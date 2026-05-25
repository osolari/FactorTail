"""Loaders and synthesizers for Kenneth-French data-library panels.

The pipeline supports two modes:

* **Online**: download a panel by URL and cache it on disk with the source
  vintage, SHA-256 hash, and access timestamp.
* **Offline / CI**: synthesize a deterministic surrogate panel whose
  marginal tails are heavy-tailed Student-t innovations with a single
  market common shock. The surrogate has the same shape and column names as
  the public panels and is used by the test suite and reproducible-CI runs
  where the actual public files are not downloaded.

The CSV pull format follows the standard "Fama/French 3 Factors", "5
Factors", etc., zipped layout. The pipeline records:

* source URL,
* download timestamp,
* SHA-256 file hash,
* row count, first date, last date,
* parsing log.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from factortail.utils.hashing import file_sha256

__all__ = ["FFPanel", "load_fama_french", "synthesize_panel"]


_DEFAULT_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_Factors_daily_CSV.zip"
)


@dataclass
class FFPanel:
    name: str
    data: pd.DataFrame
    source: str
    vintage: str
    checksum: str
    access_timestamp: str
    parse_log: list[str] = field(default_factory=list)

    @property
    def n_obs(self) -> int:
        return len(self.data)

    @property
    def start_date(self) -> pd.Timestamp:
        return self.data.index.min()

    @property
    def end_date(self) -> pd.Timestamp:
        return self.data.index.max()

    @property
    def missing_rate(self) -> float:
        return float(self.data.isna().mean().mean())


def load_fama_french(
    *,
    name: str = "FF3_daily",
    cache_dir: str | Path = "data/raw",
    url: str | None = None,
    offline: bool = False,
    n_synthetic: int = 5000,
    rng_seed: int = 42,
) -> FFPanel:
    """Load a Fama-French panel.

    Parameters
    ----------
    offline:
        If True (default for CI), return :func:`synthesize_panel` instead of
        downloading. This is what the test suite uses to avoid network
        dependence while still exercising the entire downstream pipeline.
    """
    if offline:
        return synthesize_panel(name=name, n=n_synthetic, seed=rng_seed)

    import io
    import zipfile

    import requests

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / f"{name}.csv"
    src = url or _DEFAULT_URL
    if not target.exists():
        resp = requests.get(src, timeout=60)
        resp.raise_for_status()
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        zip_name = zf.namelist()[0]
        with zf.open(zip_name) as f:
            raw = f.read().decode("utf-8")
        target.write_text(raw)
    df = _parse_ff_csv(target)
    return FFPanel(
        name=name,
        data=df,
        source=src,
        vintage=_dt.datetime.utcnow().strftime("%Y-%m-%d"),
        checksum=file_sha256(target),
        access_timestamp=_dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        parse_log=[f"parsed {len(df)} daily rows from {target.name}"],
    )


def _parse_ff_csv(path: Path) -> pd.DataFrame:
    """Parse the standard Fama-French CSV layout."""
    raw = path.read_text().splitlines()
    # Find the first row that begins with an integer date.
    start = None
    for i, line in enumerate(raw):
        token = line.strip().split(",")[0]
        if token.isdigit() and len(token) >= 6:
            start = i
            break
    if start is None:
        raise ValueError(f"Could not locate data section in {path}")
    end = start
    while end < len(raw) and raw[end].strip() and raw[end].split(",")[0].strip().isdigit():
        end += 1
    rows = raw[start:end]
    header_line = raw[start - 1] if start > 0 else "Date,Mkt-RF,SMB,HML,RF"
    cols = [c.strip() for c in header_line.split(",") if c.strip()]
    if cols[0] != "Date":
        cols = ["Date"] + cols
    df = pd.read_csv(
        Path(path),
        skiprows=start,
        nrows=len(rows),
        header=None,
        names=cols,
    )
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
    df = df.set_index("Date")
    df = df.apply(pd.to_numeric, errors="coerce") / 100.0  # FF reports in percent
    return df


def synthesize_panel(*, name: str = "FF3_daily", n: int = 5000, seed: int = 42) -> FFPanel:
    """Produce a heavy-tailed synthetic FF panel for tests and offline runs."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp("2024-12-31"), periods=n, freq="B")
    market_shock = rng.standard_t(df=4.0, size=n) * 0.012
    smb = 0.45 * market_shock + 0.5 * rng.standard_t(df=6.0, size=n) * 0.008
    hml = 0.30 * market_shock + 0.5 * rng.standard_t(df=6.0, size=n) * 0.008
    rf = np.full(n, 0.00003)
    df = pd.DataFrame(
        {"Mkt-RF": market_shock, "SMB": smb, "HML": hml, "RF": rf},
        index=pd.Index(dates, name="Date"),
    )
    return FFPanel(
        name=name,
        data=df,
        source="synthetic",
        vintage="synthetic-v1",
        checksum="synthetic",
        access_timestamp=_dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        parse_log=["synthetic panel"],
    )

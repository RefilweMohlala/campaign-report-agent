"""
Step 1 - LOAD.

Reads each raw export exactly as it arrives. Everything is loaded as TEXT (dtype=str)
on purpose: we don't trust the files yet. Converting to real numbers and dates is the
cleaning step's job (clean.py), where we can check and log every problem.
"""
from pathlib import Path

import pandas as pd

from campaign_report.config import RAW_DIR

SOURCES = {
    "google_ads": "google_ads.csv",
    "meta_ads": "meta_ads.csv",
    "app_installs": "app_installs.csv",
}


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input file: {path}. Run `python scripts/generate_mock_data.py` first."
        )
    # keep_default_na=False keeps blanks as "" so we can see them, instead of hiding them as NaN
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_all(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Return {source_name: raw DataFrame} for every source."""
    return {name: load_csv(raw_dir / filename) for name, filename in SOURCES.items()}


def profile(name: str, df: pd.DataFrame) -> str:
    """A quick human-readable look at a raw file: shape, columns, blanks, sample row."""
    blanks = {col: int((df[col].str.strip() == "").sum()) for col in df.columns}
    blanks = {c: n for c, n in blanks.items() if n}
    lines = [
        f"=== {name} ===",
        f"rows: {len(df)}   columns: {len(df.columns)}",
        f"columns: {list(df.columns)}",
        f"blank cells: {blanks or 'none'}",
        f"duplicate rows: {int(df.duplicated().sum())}",
        f"first row: {df.iloc[0].to_dict()}",
    ]
    return "\n".join(lines)
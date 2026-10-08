"""Stage 1 - Ingest: read the raw CSV and check it has the expected schema."""
import logging
from pathlib import Path

import pandas as pd

from ipl import config

log = logging.getLogger(__name__)


def load_raw(path: Path = config.RAW_MATCHES) -> pd.DataFrame:
    """Load the raw matches file without altering any values."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Raw data not found: {path}")

    df = pd.read_csv(path)

    missing = set(config.REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Raw file is missing columns: {sorted(missing)}")

    log.info("Loaded %s rows x %s cols from %s", *df.shape, path)
    return df

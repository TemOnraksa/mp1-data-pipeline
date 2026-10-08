# src/data_output.py
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def save_data(df, filepath):
    """Save a DataFrame as a CSV file."""
    path = Path(filepath)

    # Create the output folder if it does not exist yet
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)
    logger.debug(f"Saved {len(df)} rows to {path}")

    return path

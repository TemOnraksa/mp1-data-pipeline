# src/data_validator.py
import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    # Work on a copy so the original data is not changed
    df = df.copy()
    rows_before = len(df)

    # 1. Every required column must exist
    for col in required_columns:
        if col not in df.columns:
            logger.error(f"Missing required column: {col}")
            raise ValueError(f"Missing required column: {col}")

    # 2. Numeric columns must only contain numbers (or be empty)
    for col in numeric_columns:
        if col not in df.columns:
            logger.error(f"Missing numeric column: {col}")
            raise ValueError(f"Missing numeric column: {col}")

        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    logger.warning(f"Invalid numeric value in {col}: {value} (row {i})")
                    invalid_rows.append(i)

        # Remove the invalid rows
        if len(invalid_rows) > 0:
            df = df.drop(invalid_rows)
            logger.warning(f"Removed {len(invalid_rows)} rows with invalid numeric values in {col}")

        # convert to a numeric data type
        df[col] = pd.to_numeric(df[col])

    rows_after = len(df)
    rows_removed = rows_before - rows_after
    logger.debug(f"Validation: {rows_before} → {rows_after} rows (valid {rows_after}, removed {rows_removed})")

    return df

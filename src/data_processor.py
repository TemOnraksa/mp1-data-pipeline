# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    df = df.drop_duplicates()
    rows_after = len(df)
    rows_removed = rows_before - rows_after

    logger.debug(f"remove_duplicates: {rows_before} → {rows_after} rows (removed {rows_removed})")
    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        rows_before = len(df)
        df = df.dropna(axis=0)
        rows_after = len(df)
        rows_removed = rows_before - rows_after
        logger.debug(f"handle_missing: {rows_before} → {rows_after} rows (removed {rows_removed})")

    elif axis == "columns":
        columns_before = len(df.columns)
        df = df.dropna(axis=1)
        columns_after = len(df.columns)
        columns_removed = columns_before - columns_after
        logger.debug(f"handle_missing: {columns_before} → {columns_after} columns (removed {columns_removed})")

    else:
        logger.error(f"Unsupported axis: {axis}")
        raise ValueError(f"Unsupported axis: {axis}")

    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method != "iqr" and method != "zscore":
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    for column in columns:
        # Skip columns we cannot work with
        if column not in df.columns:
            logger.warning(f"Column not found: {column}")
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            logger.warning(f"Column is not numeric: {column}")
            continue

        # Both methods give us a lowest and a highest allowed value
        if method == "iqr":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
        else:
            mean = df[column].mean()
            std = df[column].std()
            lower = mean - threshold * std
            upper = mean + threshold * std

        # Keep rows inside the allowed range.
        # Missing values are not outliers, so we keep those rows too.
        rows_before = len(df)
        in_range = (df[column] >= lower) & (df[column] <= upper)
        is_missing = df[column].isna()
        df = df[in_range | is_missing]
        rows_removed = rows_before - len(df)

        logger.debug(f"{column}: lower={lower}, upper={upper}, removed={rows_removed}")
        logger.debug(f"remove_outliers: method={method}, threshold={threshold}, removed={rows_removed}")

    return df


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    settings = config["processing"]

    # 1. Remove duplicates
    if settings["remove_duplicates"]:
        df = remove_duplicates(df)

    # 2. Handle missing values
    if settings["missing"]["enabled"]:
        axis = settings["missing"]["axis"]
        df = handle_missing(df, axis)

    # 3. Remove outliers
    if settings["outliers"]["enabled"]:
        columns = settings["outliers"]["columns"]
        method = settings["outliers"]["method"]
        threshold = settings["outliers"]["threshold"]
        df = remove_outliers(df, columns, method, threshold)

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before = len(df_before)
    rows_after = len(df_after)
    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)

    report = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }
    return report

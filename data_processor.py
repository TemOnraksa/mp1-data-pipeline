# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    df = df.drop_duplicates()
    rows_after = len(df)

    logger.debug(
        f"remove_duplicates: {rows_before} → {rows_after} rows "
        f"(removed={rows_before - rows_after})"
    )
    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        rows_before = len(df)
        df = df.dropna(axis=0)
        rows_after = len(df)
        logger.debug(
            f"handle_missing: {rows_before} → {rows_after} rows "
            f"(removed={rows_before - rows_after})"
        )
    elif axis == "columns":
        cols_before = len(df.columns)
        df = df.dropna(axis=1)
        cols_after = len(df.columns)
        logger.debug(
            f"handle_missing: {cols_before} → {cols_after} columns "
            f"(removed={cols_before - cols_after})"
        )
    else:
        logger.error(f"Unsupported axis: {axis}")
        raise ValueError(f"Unsupported axis: {axis}")

    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    rows_start = len(df)

    for column in columns:
        if column not in df.columns:
            logger.warning(f"Column not found: {column}")
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            logger.warning(f"Column is not numeric: {column}")
            continue

        rows_before = len(df)
        values = df[column]

        if method == "iqr":
            # Keep values inside [Q1 - threshold*IQR, Q3 + threshold*IQR]
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            keep = values.between(lower, upper)
            details = f"lower={lower}, upper={upper}"
        else:
            # Keep values within `threshold` standard deviations of the mean
            mean = values.mean()
            std = values.std()
            if std == 0 or pd.isna(std):
                # Every value is the same (or there is only one), so no outliers
                keep = pd.Series(True, index=df.index)
            else:
                z_scores = (values - mean) / std
                keep = z_scores.abs() <= threshold
            details = f"mean={mean:.2f}, std={std:.2f}"

        # Missing values are not outliers; handle_missing() deals with those
        df = df[keep | values.isna()]

        logger.debug(f"{column}: {details}, removed={rows_before - len(df)}")

    logger.debug(
        f"remove_outliers: method={method}, threshold={threshold}, "
        f"{rows_start} → {len(df)} rows (removed={rows_start - len(df)})"
    )
    return df


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config["processing"]

    # 1. Remove duplicates
    if processing["remove_duplicates"]:
        df = remove_duplicates(df)

    # 2. Handle missing values
    missing = processing["missing"]
    if missing["enabled"]:
        df = handle_missing(df, axis=missing["axis"])

    # 3. Remove outliers
    outliers = processing["outliers"]
    if outliers["enabled"]:
        df = remove_outliers(
            df,
            columns=outliers["columns"],
            method=outliers["method"],
            threshold=outliers["threshold"],
        )

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before = len(df_before)
    rows_after = len(df_after)
    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)

    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }

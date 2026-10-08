"""
Data Processing Pipeline

DS 3500 - MP1

Usage:
    python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml
    python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
"""

import argparse
import logging
import sys

from src import (
    create_cleaning_report,
    load_data,
    process_data,
    save_data,
    setup_logging,
    validate_dataframe,
    validate_input,
)


logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Load, validate, clean, and save data.")

    parser.add_argument("--input", "-i", required=True, help="Path to the input file")
    parser.add_argument("--config", required=True, help="Path to the YAML config file")
    parser.add_argument("--output", "-o", required=True, help="Path to the output file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()
    return args


def main():
    """Main pipeline function."""
    # Step 1: read the command-line arguments and turn on logging
    args = parse_arguments()
    setup_logging(args.verbose)
    logger.debug(f"Arguments parsed: input={args.input}, config={args.config}, output={args.output}")

    # Step 2: make sure both files exist before loading anything
    if not validate_input(args.input):
        sys.exit(1)
    if not validate_input(args.config):
        sys.exit(1)

    # Step 3: load the data and the configuration
    try:
        data = load_data(args.input)
        config = load_data(args.config)
    except ValueError:
        sys.exit(1)

    # Step 4: validate the data using the settings in the config file
    required_columns = config["validation"]["required_columns"]
    numeric_columns = config["validation"]["numeric_columns"]
    rows_before_validation = len(data)

    try:
        df = validate_dataframe(data, required_columns, numeric_columns)
    except ValueError:
        sys.exit(1)

    logger.info(f"Validation complete: {rows_before_validation} → {len(df)} rows")

    # Step 5: keep a copy of the validated data, then clean it
    df_before = df.copy()

    try:
        df_after = process_data(df, config)
    except ValueError:
        sys.exit(1)

    report = create_cleaning_report(df_before, df_after)
    logger.info(f"Processing complete: {report['rows_before']} → {report['rows_after']} rows")

    # Step 6: save the cleaned data
    output_path = save_data(df_after, args.output)
    logger.info(f"Saved cleaned data to {output_path}")

    # Step 7: print the cleaning report
    print()
    print("Cleaning report:")
    print(report)


if __name__ == "__main__":
    main()

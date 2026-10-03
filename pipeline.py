"""
Data Processing Pipeline

DS 3500 - MP1

Usage:
    python pipeline.py --input fixtures/sample.csv --config config.yaml --output cleaned_data.csv
    python pipeline.py --input fixtures/sample.csv --config config.yaml --output cleaned_data.csv --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

from data_loaders import load_data
from data_processor import process_data, create_cleaning_report


logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Load, clean, and save data.")

    parser.add_argument("--input", "-i", required=True, help="Path to the input file")
    parser.add_argument("--config", required=True, help="Path to the YAML config file")
    parser.add_argument("--output", "-o", required=True, help="Path to the output file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()
    return args


def validate_input(filepath):
    """Check whether the input path exists and is a file."""
    path = Path(filepath)

    if path.is_file():
        logger.info(f"Input file validated: {filepath}")
        return True
    else:
        logger.error(f"Input file not found: {filepath}")
        return False


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

    # Step 4: keep a copy of the original data, then clean it
    df_before = data.copy()

    try:
        df_after = process_data(data, config)
    except ValueError:
        sys.exit(1)

    # Step 5: report what changed
    report = create_cleaning_report(df_before, df_after)
    print(report)
    logger.info(f"Processing complete: {report['rows_before']} → {report['rows_after']} rows")

    # Step 6: save the cleaned data
    df_after.to_csv(args.output, index=False)
    logger.info(f"Saved cleaned data to {args.output}")


if __name__ == "__main__":
    main()

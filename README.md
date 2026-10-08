# MP1 Data Pipeline

This project is a command-line data pipeline that loads a data file, validates it, cleans it, and saves the cleaned result as a CSV file. Data moves through the pipeline in order: `pipeline.py` reads the command-line arguments, checks that the input and config files exist, loads both files, validates the data, cleans it, saves it, and prints a cleaning report. All the reusable code lives in the `src/` package, and `pipeline.py` only coordinates the steps. `src/data_loaders.py` loads CSV, JSON, and YAML files based on the file extension. `src/data_validator.py` checks that the required columns exist and removes rows whose numeric columns contain values that are not numbers. `src/data_processor.py` removes duplicate rows, rows with missing values, and outliers, and builds the cleaning report. `src/data_output.py` saves the cleaned data and creates the output folder if needed, while `src/utils.py` sets up logging and checks that input files exist. Which columns are validated and which cleaning steps run are controlled by `config/config.yaml`, so the same code can clean a different dataset by changing only the config.

## Example

```bash
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
```

Output:

```text
13:17:24 DEBUG    __main__ — Arguments parsed: input=fixtures/sample_data.csv, config=config/config.yaml, output=output/clean.csv
13:17:24 INFO     src.utils — Input file validated: fixtures/sample_data.csv
13:17:24 INFO     src.utils — Input file validated: config/config.yaml
13:17:24 INFO     src.data_loaders — Loaded CSV file: fixtures/sample_data.csv (100 rows)
13:17:24 INFO     src.data_loaders — Loaded YAML file: config/config.yaml
13:17:24 WARNING  src.data_validator — Invalid numeric value in rating: not_available (row 94)
13:17:24 WARNING  src.data_validator — Invalid numeric value in rating: error (row 95)
13:17:24 WARNING  src.data_validator — Removed 2 rows with invalid numeric values in rating
13:17:24 DEBUG    src.data_validator — Validation: 100 → 98 rows (valid 98, removed 2)
13:17:24 INFO     __main__ — Validation complete: 100 → 98 rows
13:17:24 DEBUG    src.data_processor — remove_duplicates: 98 → 96 rows (removed 2)
13:17:24 DEBUG    src.data_processor — handle_missing: 96 → 94 rows (removed 2)
13:17:24 DEBUG    src.data_processor — rating: lower=43.625, upper=106.625, removed=2
13:17:24 DEBUG    src.data_processor — remove_outliers: method=iqr, threshold=1.5, removed=2
13:17:24 INFO     __main__ — Processing complete: 98 → 92 rows
13:17:24 DEBUG    src.data_output — Saved 92 rows to output/clean.csv
13:17:24 INFO     __main__ — Saved cleaned data to output/clean.csv

Cleaning report:
{'rows_before': 98, 'rows_after': 92, 'rows_removed': 6, 'columns_before': 5, 'columns_after': 5, 'columns_removed': 0}
```

from pathlib import Path
import pandas as pd

# Locate the project and raw data folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

# Check whether the raw data folder exists
if not RAW_DIR.exists():
    raise FileNotFoundError(
        f"Raw data folder not found: {RAW_DIR}"
    )

# List the CSV files available
csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        "No CSV files found. Check data/raw/."
    )

print("CSV FILES FOUND")
print("=" * 50)

for file in csv_files:
    print(file.name)

# Load the orders dataset
orders_path = RAW_DIR / "olist_orders_dataset.csv"

if not orders_path.exists():
    raise FileNotFoundError(
        "olist_orders_dataset.csv is missing."
    )

orders = pd.read_csv(orders_path)

print("\nORDERS DATASET OVERVIEW")
print("=" * 50)

print("Shape:", orders.shape)

print("\nFirst 5 rows:")
print(orders.head())

print("\nColumn names:")
print(orders.columns.tolist())

print("\nData types and non-null counts:")
orders.info()

print("\nMissing values per column:")
print(orders.isnull().sum())

print("\nDuplicate rows:", orders.duplicated().sum())

print("\nUnique order IDs:", orders["order_id"].nunique())

print("\nOrder status counts:")
print(orders["order_status"].value_counts(dropna=False))

from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "raw"
    / "olist_customers_dataset.csv"
)

df = pd.read_csv(file_path)

print("=" * 50)
print("CUSTOMERS DATA INSPECTION")
print("=" * 50)

print("\nShape:", df.shape)
print("\nColumns:", df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:", df.duplicated().sum())

print("\nDuplicate customer IDs:",
      df["customer_id"].duplicated().sum())

print("\nUnique customer IDs:",
      df["customer_id"].nunique())

print("\nUnique customer unique IDs:",
      df["customer_unique_id"].nunique())

print("\nCustomer state counts:")
print(df["customer_state"].value_counts().head(15))

print("\nCustomer city examples:")
print(df["customer_city"].value_counts().head(10))

print("\nSample records:")
print(df.head())

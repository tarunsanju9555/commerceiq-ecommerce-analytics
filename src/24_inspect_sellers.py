
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "raw"
    / "olist_sellers_dataset.csv"
)

df = pd.read_csv(file_path)

print("=" * 50)
print("SELLERS DATA INSPECTION")
print("=" * 50)

print("\nShape:", df.shape)
print("\nColumns:", df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:", df.duplicated().sum())

print("\nDuplicate seller IDs:",
      df["seller_id"].duplicated().sum())

print("\nUnique seller IDs:",
      df["seller_id"].nunique())

print("\nSeller state counts:")
print(df["seller_state"].value_counts().head(15))

print("\nSeller city examples:")
print(df["seller_city"].value_counts().head(10))

print("\nSample records:")
print(df.head())


from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "raw"
    / "olist_order_items_dataset.csv"
)

df = pd.read_csv(file_path)

print("=" * 50)
print("ORDER ITEMS DATA INSPECTION")
print("=" * 50)

print("\nShape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:", df.duplicated().sum())

print("\nDuplicate order-item keys:")
print(
    df.duplicated(
        subset=["order_id", "order_item_id"]
    ).sum()
)

print("\nSample records:")
print(df.head())

print("\nNumeric summary:")
print(df.select_dtypes(include="number").describe())

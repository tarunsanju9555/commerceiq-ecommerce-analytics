
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "raw"
    / "olist_products_dataset.csv"
)

df = pd.read_csv(file_path)

print("=" * 50)
print("PRODUCTS DATA INSPECTION")
print("=" * 50)

print("\nShape:", df.shape)
print("\nColumns:", df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:", df.duplicated().sum())

print("\nDuplicate product IDs:", df["product_id"].duplicated().sum())

print("\nUnique product IDs:", df["product_id"].nunique())

print("\nProduct category counts:")
print(df["product_category_name"].value_counts(dropna=False).head(15))

print("\nProduct dimensions summary:")
dimension_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]

print(df[dimension_columns].describe())

print("\nSample records:")
print(df.head())

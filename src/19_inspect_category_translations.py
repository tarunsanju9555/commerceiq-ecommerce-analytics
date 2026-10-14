
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "raw"
    / "product_category_name_translation.csv"
)

df = pd.read_csv(file_path)

print("=" * 50)
print("CATEGORY TRANSLATION INSPECTION")
print("=" * 50)

print("\nShape:", df.shape)
print("\nColumns:", df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:", df.duplicated().sum())

print(
    "\nDuplicate Portuguese category names:",
    df["product_category_name"].duplicated().sum()
)

print("\nUnique Portuguese categories:",
      df["product_category_name"].nunique())

print("\nUnique English categories:",
      df["product_category_name_english"].nunique())

print("\nTranslation records:")
print(df.to_string(index=False))

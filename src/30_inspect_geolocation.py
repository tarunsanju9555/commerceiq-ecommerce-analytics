
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent
file = root / "data" / "raw" / "olist_geolocation_dataset.csv"

df = pd.read_csv(file)

print("Rows:", len(df))
print("Columns:", df.columns.tolist())
print("Missing values:\n", df.isnull().sum())
print("Unique ZIP prefixes:", df["geolocation_zip_code_prefix"].nunique())
print("Unique states:", df["geolocation_state"].nunique())
print("Exact duplicate rows:", df.duplicated().sum())


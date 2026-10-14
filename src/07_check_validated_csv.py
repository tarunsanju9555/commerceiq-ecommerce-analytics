
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

file_path = (
    project_root
    / "data"
    / "processed"
    / "orders_validated.csv"
)

df = pd.read_csv(file_path, nrows=5)

print("=" * 50)
print("VALIDATED CSV CHECK")
print("=" * 50)

print("\nColumns:")
for column in df.columns:
    print(column)

print("\nNumber of columns:", len(df.columns))
print("\nSample records:")
print(df.head())

print("\nData types:")
print(df.dtypes)

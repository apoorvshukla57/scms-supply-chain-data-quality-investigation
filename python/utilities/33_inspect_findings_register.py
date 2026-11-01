
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Project_03")
OUTPUT_DIR = BASE_DIR / "publication" / "execution" / "outputs"

files = [
    OUTPUT_DIR / "initial_findings_register.csv",
    OUTPUT_DIR / "prioritized_findings_register.csv",
]

for file_path in files:
    print("\n" + "=" * 75)
    print(f"FILE: {file_path.name}")
    print("=" * 75)

    if not file_path.exists():
        print("FILE NOT FOUND")
        continue

    df = pd.read_csv(file_path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFindings:")
    print(df.to_string(index=False, max_cols=None))


from pathlib import Path
import pandas as pd

OUT = Path(r"C:\Project_03\publication\evidence")

files = [
    "register_evidence_verification.csv",
    "initial_findings_register.csv",
    "prioritized_findings_register.csv",
]

for filename in files:
    path = OUT / filename
    print(f"\n{'=' * 72}")
    print(filename)
    print("=" * 72)

    if not path.exists():
        print("FILE NOT FOUND")
        continue

    df = pd.read_csv(path, encoding="utf-8-sig")
    print(f"Rows: {len(df):,}")
    print("Columns:", df.columns.tolist())

    if filename == "register_evidence_verification.csv":
        print(df.to_string(index=False))
    elif "finding_id" in df.columns:
        columns = [
            c for c in [
                "finding_id",
                "finding",
                "evidence",
                "classification",
                "validation_status",
                "next_validation",
                "investigation_priority",
                "priority_status",
            ]
            if c in df.columns
        ]
        print(df[columns].to_string(index=False, max_colwidth=180))

print("\nInspection complete. No files were modified.")

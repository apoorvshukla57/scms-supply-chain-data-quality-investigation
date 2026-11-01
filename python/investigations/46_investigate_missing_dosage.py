
from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Project_03")
SOURCE = BASE / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT = BASE / "publication" / "execution" / "outputs"

DOSAGE_COL = "dosage"

GROUP_COLUMNS = [
    "product group",
    "sub classification",
    "item description",
    "molecule/test type",
    "brand",
    "dosage form",
]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(SOURCE, low_memory=False)

    if DOSAGE_COL not in df.columns:
        raise KeyError(f"Missing column: {DOSAGE_COL}")

    # Treat nulls and whitespace-only strings as missing.
    dosage = df[DOSAGE_COL].astype("string").str.strip()
    missing = dosage.isna() | dosage.eq("")

    print(f"Source shape: {df.shape}")
    print(
        f"Missing dosage: {missing.sum():,} / {len(df):,} "
        f"({missing.mean() * 100:.2f}%)"
    )
    print(f"Non-missing dosage: {(~missing).sum():,}")

    audit = df.copy()
    audit["_dosage_missing"] = missing

    available_columns = [
        col for col in GROUP_COLUMNS if col in df.columns
    ]

    if not available_columns:
        raise ValueError(
            "None of the expected grouping columns were found."
        )

    for col in available_columns:
        summary = (
            audit.groupby(col, dropna=False)
            .agg(
                total_records=("_dosage_missing", "size"),
                missing_dosage=("_dosage_missing", "sum"),
            )
            .reset_index()
        )

        summary["missing_percentage"] = (
            summary["missing_dosage"]
            / summary["total_records"] * 100
        )

        # Highest number of missing records first.
        summary = summary.sort_values(
            ["missing_dosage", "total_records"],
            ascending=[False, False],
        )

        filename = (
            col.replace("/", "_")
            .replace(" ", "_")
        )
        output_path = (
            OUTPUT / f"missing_dosage_by_{filename}.csv"
        )
        summary.to_csv(output_path, index=False)

        print(f"\n--- Missing dosage by {col} ---")
        print(summary.head(15).to_string(index=False))
        print(f"Saved: {output_path}")

    # Save affected records for traceable review.
    detail_columns = [
        col for col in [
            "id",
            "product group",
            "sub classification",
            "item description",
            "molecule/test type",
            "brand",
            "dosage form",
            "dosage",
        ]
        if col in df.columns
    ]

    detail_path = OUTPUT / "missing_dosage_records_for_review.csv"
    df.loc[missing, detail_columns].to_csv(
        detail_path, index=False
    )

    print(f"\nAffected-record details saved: {detail_path}")
    print("Source data was not modified.")


if __name__ == "__main__":
    main()

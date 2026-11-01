
import pandas as pd

# ============================================================
# DQ-08 - Missing Insurance vs Missing Shipment Mode
# Read-only investigation using the original source CSV
# ============================================================

SOURCE = (
    r"C:\Project_03\dataset\Suppy_Chain_Shipment_Data.csv"
)

INSURANCE_COL = "line item insurance (usd)"
MODE_COL = "shipment mode"


def identify_missing(series):
    """Treat nulls and whitespace-only strings as missing."""
    stripped = series.astype("string").str.strip()

    return (
        series.isna()
        | stripped.eq("").fillna(False)
    )


def count_whitespace_only(series):
    """Count non-null values containing only whitespace."""
    stripped = series.astype("string").str.strip()

    return int(
        (
            series.notna()
            & stripped.eq("").fillna(False)
        ).sum()
    )


def main():
    df = pd.read_csv(
        SOURCE,
        encoding="utf-8-sig",
        low_memory=False,
    )

    required = [INSURANCE_COL, MODE_COL]
    missing_columns = [
        col for col in required if col not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Required columns not found: {missing_columns}"
        )

    insurance_missing = identify_missing(df[INSURANCE_COL])
    mode_missing = identify_missing(df[MODE_COL])

    insurance_whitespace = count_whitespace_only(
        df[INSURANCE_COL]
    )
    mode_whitespace = count_whitespace_only(
        df[MODE_COL]
    )

    both_missing = insurance_missing & mode_missing

    overlap = pd.crosstab(
        insurance_missing.map({
            True: "Missing insurance",
            False: "Insurance present",
        }),
        mode_missing.map({
            True: "Missing shipment mode",
            False: "Shipment mode present",
        }),
        margins=True,
    )

    print("=" * 65)
    print("DQ-08: INSURANCE AND SHIPMENT-MODE MISSINGNESS")
    print("=" * 65)

    print(f"\nTotal records: {len(df):,}")

    print(
        f"Missing insurance: {insurance_missing.sum():,}"
    )
    print(
        f"  Whitespace-only insurance values: "
        f"{insurance_whitespace:,}"
    )

    print(
        f"Missing shipment mode: {mode_missing.sum():,}"
    )
    print(
        f"  Whitespace-only shipment-mode values: "
        f"{mode_whitespace:,}"
    )

    print(f"Missing both: {both_missing.sum():,}")

    print("\nCross-tabulation (record counts):")
    print(overlap.to_string())

    print("\nKey proportions:")

    if mode_missing.sum() > 0:
        print(
            "Among records with missing shipment mode, "
            f"{both_missing.sum() / mode_missing.sum():.2%} "
            "also have missing insurance."
        )

    if insurance_missing.sum() > 0:
        print(
            "Among records with missing insurance, "
            f"{both_missing.sum() / insurance_missing.sum():.2%} "
            "also have missing shipment mode."
        )

    print("\nOriginal source data was not modified.")
    print("No output files were created.")


if __name__ == "__main__":
    main()


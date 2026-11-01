
from pathlib import Path
import re
import pandas as pd

BASE = Path(r"C:\Project_03")
SOURCE = BASE / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT = BASE / "publication" / "execution" / "outputs"


def normalize(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_column(columns, candidates):
    lookup = {normalize(column): column for column in columns}

    for candidate in candidates:
        key = normalize(candidate)
        if key in lookup:
            return lookup[key]

    raise ValueError(
        f"Could not identify any of {candidates}. "
        f"Available columns: {list(columns)}"
    )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        SOURCE,
        encoding="utf-8-sig",
        low_memory=False,
    )

    id_col = find_column(df.columns, ["id"])
    group_col = find_column(df.columns, ["product group"])
    unit_col = find_column(df.columns, ["unit price"])
    pack_col = find_column(df.columns, ["pack price"])
    uom_col = find_column(
        df.columns,
        [
            "unit of measure (per pack)",
            "unit of measure",
            "uom",
        ],
    )

    unit_price = pd.to_numeric(df[unit_col], errors="coerce")
    pack_price = pd.to_numeric(df[pack_col], errors="coerce")
    uom = pd.to_numeric(df[uom_col], errors="coerce")

    valid = (
        unit_price.notna()
        & pack_price.notna()
        & uom.notna()
    )

    result = pd.DataFrame({
        "id": df[id_col],
        "product_group": df[group_col],
        "unit_price": unit_price,
        "uom": uom,
        "pack_price": pack_price,
    })

    result["expected_pack_price"] = (
        result["unit_price"] * result["uom"]
    )

    result["difference"] = (
        result["pack_price"] - result["expected_pack_price"]
    )

    # Original investigation threshold: absolute difference > $0.02.
    result["original_exception"] = (
        result["difference"].abs() > 0.02
    )

    # Test the same relationship after rounding the calculated
    # unit-price × UOM amount to two decimal places.
    result["expected_pack_price_rounded"] = (
        result["expected_pack_price"].round(2)
    )

    result["rounded_difference"] = (
        result["pack_price"]
        - result["expected_pack_price_rounded"]
    )

    result["exact_rounded_match"] = (
        result["rounded_difference"].abs() < 0.000001
    )

    result["rounded_match_within_002"] = (
        result["rounded_difference"].abs() <= 0.020000001
    )

    result["comparable"] = valid

    comparable = result.loc[valid].copy()

    # Preserve the original exception population for all follow-up
    # calculations. This is the critical correction.
    original_exceptions = comparable.loc[
        comparable["original_exception"]
    ].copy()

    resolved_exactly = int(
        original_exceptions["exact_rounded_match"].sum()
    )

    resolved_within_tolerance = int(
        original_exceptions["rounded_match_within_002"].sum()
    )

    remaining = (
        len(original_exceptions) - resolved_within_tolerance
    )

    overall = pd.DataFrame([{
        "source_records": len(df),
        "comparable_records": len(comparable),
        "noncomparable_records": len(df) - len(comparable),
        "original_exceptions_over_002": len(original_exceptions),
        "exceptions_matching_after_rounding_exactly": resolved_exactly,
        "exceptions_matching_after_rounding_within_002": (
            resolved_within_tolerance
        ),
        "remaining_exceptions_after_rounding": remaining,
        "share_resolved_within_tolerance_pct": round(
            100 * resolved_within_tolerance
            / len(original_exceptions),
            2,
        ) if len(original_exceptions) else None,
    }])

    # CORRECTED: group only original exceptions, not all comparable rows.
    by_group = (
        original_exceptions.groupby("product_group", dropna=False)
        .agg(
            original_exceptions=("id", "size"),
            exact_rounded_matches=("exact_rounded_match", "sum"),
            rounded_matches_within_002=(
                "rounded_match_within_002", "sum"
            ),
        )
        .reset_index()
    )

    by_group["remaining_after_rounding"] = (
        by_group["original_exceptions"]
        - by_group["rounded_matches_within_002"]
    )

    # Reconciliation safeguards.
    assert int(
        by_group["original_exceptions"].sum()
    ) == len(original_exceptions)

    assert int(
        by_group["exact_rounded_matches"].sum()
    ) == resolved_exactly

    assert int(
        by_group["rounded_matches_within_002"].sum()
    ) == resolved_within_tolerance

    assert int(
        by_group["remaining_after_rounding"].sum()
    ) == remaining

    assert (by_group["remaining_after_rounding"] >= 0).all()

    # Save record-level checks for the full comparable population.
    comparable.sort_values(
        "difference",
        key=lambda values: values.abs(),
        ascending=False,
    ).to_csv(
        OUTPUT / "unit_price_uom_rounding_record_checks.csv",
        index=False,
    )

    result.loc[~valid].to_csv(
        OUTPUT / "unit_price_uom_rounding_noncomparable.csv",
        index=False,
    )

    overall.to_csv(
        OUTPUT / "unit_price_uom_rounding_overall.csv",
        index=False,
    )

    by_group.to_csv(
        OUTPUT / "unit_price_uom_rounding_by_group.csv",
        index=False,
    )

    print("\nUNIT PRICE × UOM ROUNDING VALIDATION")
    print("=" * 55)
    print(overall.to_string(index=False))

    print("\nResults by product group:")
    print(by_group.to_string(index=False))

    print("\nReconciliation checks: PASSED")
    print("Outputs saved to:", OUTPUT)
    print("Original source data was not modified.")


if __name__ == "__main__":
    main()

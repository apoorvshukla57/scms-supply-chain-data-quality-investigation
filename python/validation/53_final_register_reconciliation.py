

from pathlib import Path
import sys

import pandas as pd


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

PROJECT_DIR = Path(r"C:\Project_03")
PUBLICATION_DIR = PROJECT_DIR / "publication"
EVIDENCE_DIR = PUBLICATION_DIR / "evidence"

FILES = {
    "initial": EVIDENCE_DIR / "initial_findings_register.csv",
    "prioritized": EVIDENCE_DIR / "prioritized_findings_register.csv",
}

EXPECTED_IDS = {f"DQ-{i:02d}" for i in range(1, 9)}

REVIEW_IDS = ["DQ-02", "DQ-03", "DQ-06", "DQ-07"]

SELECTED_COLUMNS = [
    "finding_id",
    "finding",
    "evidence",
    "classification",
    "validation_status",
    "next_validation",
    "investigation_priority",
    "priority_status",
]


# ------------------------------------------------------------
# REGISTER VALIDATION
# ------------------------------------------------------------

def load_and_validate_register(name, path):
    errors = []

    if not path.exists():
        raise FileNotFoundError(
            f"{name.upper()} register not found: {path}"
        )

    df = pd.read_csv(path, encoding="utf-8-sig")

    print(f"\n{'=' * 70}")
    print(f"{name.upper()} REGISTER")
    print(f"{'=' * 70}")

    print(f"File: {path.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    if "finding_id" not in df.columns:
        raise ValueError(
            f"{name.upper()} register is missing the required "
            "'finding_id' column."
        )

    normalized_ids = df["finding_id"].astype("string").str.strip()

    missing_id_count = int(
        normalized_ids.isna().sum()
        + normalized_ids.eq("").sum()
    )

    valid_ids = normalized_ids.dropna()
    valid_ids = valid_ids[valid_ids.ne("")]

    duplicate_count = int(valid_ids.duplicated().sum())

    actual_ids = set(valid_ids.tolist())
    missing_ids = sorted(EXPECTED_IDS - actual_ids)
    unexpected_ids = sorted(actual_ids - EXPECTED_IDS)

    print(f"Missing or blank finding IDs: {missing_id_count}")
    print(f"Duplicate finding IDs: {duplicate_count}")
    print(f"Missing expected IDs: {missing_ids}")
    print(f"Unexpected IDs: {unexpected_ids}")

    if missing_id_count:
        errors.append(
            f"{name}: {missing_id_count} missing or blank finding IDs."
        )

    if duplicate_count:
        errors.append(
            f"{name}: {duplicate_count} duplicate finding IDs."
        )

    if missing_ids:
        errors.append(
            f"{name}: missing expected IDs {missing_ids}."
        )

    if unexpected_ids:
        errors.append(
            f"{name}: unexpected IDs {unexpected_ids}."
        )

    if not errors:
        print(
            f"PASS: {name} register contains all eight expected "
            "finding IDs exactly once."
        )

    if "investigation_priority" in df.columns:
        print("\nPriority distribution:")
        print(
            df["investigation_priority"]
            .value_counts(dropna=False)
            .sort_index()
            .to_string()
        )

    columns = [
        column
        for column in SELECTED_COLUMNS
        if column in df.columns
    ]

    print("\nSelected evidence and status fields:")

    if columns:
        review_mask = normalized_ids.isin(REVIEW_IDS)

        print(
            df.loc[review_mask, columns].to_string(index=False)
        )
    else:
        print("No selected review columns are available.")

    return errors


# ------------------------------------------------------------
# MAIN AUDIT
# ------------------------------------------------------------

def main():
    print("\nFINAL FINDINGS REGISTER RECONCILIATION")
    print("=" * 70)

    all_errors = []

    for name, path in FILES.items():
        try:
            errors = load_and_validate_register(name, path)
            all_errors.extend(errors)

        except (FileNotFoundError, pd.errors.EmptyDataError,
                pd.errors.ParserError, ValueError, OSError) as exc:
            all_errors.append(f"{name}: {exc}")
            print(f"ERROR: {exc}")

    print("\n" + "=" * 70)

    if all_errors:
        print("RECONCILIATION FAILED")
        print("=" * 70)

        for error in all_errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("RECONCILIATION PASSED")
    print("Both registers passed the structural ID checks.")
    print("Read-only audit completed.")
    print("No files were modified.")


if __name__ == "__main__":
    main()


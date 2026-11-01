
from pathlib import Path
import pandas as pd
import sys


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_BASE = Path(r"C:\Project_03")
PUBLICATION_BASE = PROJECT_BASE / "publication"
EVIDENCE = PUBLICATION_BASE / "evidence"

INITIAL = EVIDENCE / "initial_findings_register.csv"
PRIORITIZED = EVIDENCE / "prioritized_findings_register.csv"


# ============================================================
# 2. EXPECTED BASELINE
# ============================================================

EXPECTED_IDS = [f"DQ-{i:02d}" for i in range(1, 9)]

EXPECTED_PRIORITIES = {
    "DQ-01": "P2",
    "DQ-02": "P1",
    "DQ-03": "P3",
    "DQ-04": "P2",
    "DQ-05": "P2",
    "DQ-06": "P1",
    "DQ-07": "P2",
    "DQ-08": "P2",
}

SHARED_COLUMNS = [
    "finding_id",
    "quality_dimension",
    "finding",
    "rule_tested",
    "evidence",
    "classification",
    "severity",
    "recommended_action",
    "validation_status",
    "next_validation",
]

PRIORITY_COLUMNS = [
    "investigation_priority",
    "priority_rationale",
    "priority_status",
]

# Documented historical refinements in the prioritized register.
# All other shared-field differences remain unexpected.
APPROVED_DIFFERENCES = {
    ("DQ-03", "finding"),
    ("DQ-03", "evidence"),
    ("DQ-03", "validation_status"),
}


# ============================================================
# 3. REGISTER LOADING
# ============================================================

def load_register(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Required register not found: {path}"
        )

    df = pd.read_csv(
        path,
        dtype={"finding_id": "string"}
    )

    df.columns = df.columns.str.strip()

    if "finding_id" not in df.columns:
        raise ValueError(
            f"{path.name}: finding_id column missing"
        )

    df["finding_id"] = df["finding_id"].str.strip()

    if df["finding_id"].isna().any():
        raise ValueError(
            f"{path.name}: missing finding IDs"
        )

    if df["finding_id"].eq("").any():
        raise ValueError(
            f"{path.name}: blank finding IDs"
        )

    if df["finding_id"].duplicated().any():

        duplicates = df.loc[
            df["finding_id"].duplicated(keep=False),
            "finding_id"
        ].tolist()

        raise ValueError(
            f"{path.name}: duplicate IDs: {duplicates}"
        )

    actual_ids = set(df["finding_id"])
    expected_ids = set(EXPECTED_IDS)

    if actual_ids != expected_ids:

        raise ValueError(
            f"{path.name}: unexpected finding IDs. "
            f"Missing: {sorted(expected_ids - actual_ids)}; "
            f"Unexpected: {sorted(actual_ids - expected_ids)}"
        )

    return df.sort_values(
        "finding_id"
    ).reset_index(drop=True)


# ============================================================
# 4. MAIN QA WORKFLOW
# ============================================================

def main():

    errors = []

    print("=" * 65)
    print("FULL FINDINGS REGISTER QUALITY ASSURANCE")
    print("=" * 65)

    initial = load_register(INITIAL)
    prioritized = load_register(PRIORITIZED)

    print("\n=== STRUCTURAL CHECKS ===")
    print(f"Initial register: {len(initial)} findings")
    print(f"Prioritized register: {len(prioritized)} findings")
    print(
        "PASS: both registers contain DQ-01 through DQ-08 "
        "exactly once."
    )

    # --------------------------------------------------------
    # REQUIRED COLUMN CHECK
    # --------------------------------------------------------

    print("\n=== REQUIRED COLUMN CHECK ===")

    for name, df in [
        ("initial", initial),
        ("prioritized", prioritized),
    ]:

        required = list(SHARED_COLUMNS)

        if name == "prioritized":
            required += PRIORITY_COLUMNS

        missing_columns = set(required) - set(df.columns)

        if missing_columns:

            message = (
                f"{name} register missing columns: "
                f"{sorted(missing_columns)}"
            )

            errors.append(message)
            print(f"FAIL: {message}")

        else:
            print(
                f"PASS: {name} register has all required columns."
            )

    if errors:
        print("\nQA STOPPED: required columns are missing.")
        raise SystemExit(1)

    # --------------------------------------------------------
    # SHARED-FIELD CONSISTENCY
    # --------------------------------------------------------

    print("\n=== SHARED-FIELD CONSISTENCY ===")

    left = initial[SHARED_COLUMNS].set_index("finding_id")
    right = prioritized[SHARED_COLUMNS].set_index("finding_id")

    mismatches = []
    approved_differences_found = []

    for finding_id in EXPECTED_IDS:

        for column in SHARED_COLUMNS[1:]:

            a = left.loc[finding_id, column]
            b = right.loc[finding_id, column]

            if pd.isna(a) and pd.isna(b):
                continue

            if str(a) != str(b):

                difference = (finding_id, column, a, b)

                if (finding_id, column) in APPROVED_DIFFERENCES:
                    approved_differences_found.append(difference)
                else:
                    mismatches.append(difference)

    print(
        "Approved historical differences: "
        f"{len(approved_differences_found)}"
    )

    for finding_id, column, a, b in approved_differences_found:
        print(f"  APPROVED: {finding_id} | {column}")

    # An approved difference must actually exist.
    missing_approved = (
        APPROVED_DIFFERENCES
        - {
            (finding_id, column)
            for finding_id, column, _, _
            in approved_differences_found
        }
    )

    if missing_approved:

        message = (
            "Expected approved differences were not found: "
            f"{sorted(missing_approved)}"
        )

        errors.append(message)
        print(f"FAIL: {message}")

    if mismatches:

        message = (
            f"{len(mismatches)} unexpected shared-field "
            "differences found."
        )

        errors.append(message)
        print(f"FAIL: {message}")

        for finding_id, column, a, b in mismatches:
            print(f"\n{finding_id} | {column}")
            print(f"  Initial:     {a}")
            print(f"  Prioritized: {b}")

    else:
        print(
            "PASS: no unexpected shared-field differences."
        )

    # --------------------------------------------------------
    # MISSING-FIELD CHECK
    # --------------------------------------------------------

    print("\n=== MISSING-FIELD CHECK ===")

    missing_found = False

    for name, df in [
        ("initial", initial),
        ("prioritized", prioritized),
    ]:

        required = list(SHARED_COLUMNS)

        if name == "prioritized":
            required += PRIORITY_COLUMNS

        for column in required:

            blank = (
                df[column].isna()
                | df[column]
                .astype("string")
                .str.strip()
                .eq("")
            )

            if blank.any():

                missing_found = True

                ids = df.loc[
                    blank, "finding_id"
                ].tolist()

                message = (
                    f"{name}.{column} blank for {ids}"
                )

                errors.append(message)
                print(f"FAIL: {message}")

    if not missing_found:
        print(
            "PASS: no blank values in required register fields."
        )

    # --------------------------------------------------------
    # FINAL PRIORITY BASELINE CHECK
    # --------------------------------------------------------

    print("\n=== FINAL PRIORITY BASELINE CHECK ===")

    actual_priorities = (
        prioritized
        .set_index("finding_id")["investigation_priority"]
        .astype("string")
        .str.strip()
        .to_dict()
    )

    for finding_id, expected in EXPECTED_PRIORITIES.items():

        actual = actual_priorities.get(finding_id)

        if actual != expected:

            message = (
                f"{finding_id}: expected {expected}, "
                f"found {actual}"
            )

            errors.append(message)
            print(f"FAIL: {message}")

        else:
            print(f"PASS: {finding_id} = {expected}")

    # --------------------------------------------------------
    # PRIORITY DISTRIBUTION
    # --------------------------------------------------------

    print("\n=== PRIORITY DISTRIBUTION ===")

    print(
        prioritized["investigation_priority"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # FINDING-BY-FINDING REVIEW
    # --------------------------------------------------------

    print("\n=== FINDING-BY-FINDING REVIEW ===")

    columns = [
        "finding_id",
        "finding",
        "severity",
        "investigation_priority",
        "priority_rationale",
        "priority_status",
    ]

    print(
        prioritized[columns]
        .sort_values("finding_id")
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # VALIDATION STATUS REVIEW
    # --------------------------------------------------------

    print("\n=== VALIDATION STATUS ===")

    print(
        prioritized[
            ["finding_id", "validation_status", "next_validation"]
        ].to_string(index=False)
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 65)

    if errors:

        print(f"QA FAILED: {len(errors)} issue(s) detected.")

        for error in errors:
            print(f"- {error}")

        print("No register files were modified.")
        raise SystemExit(1)

    print("QA PASSED: all automated checks completed successfully.")
    print("No register files were modified.")
    print("=" * 65)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"\nQA ERROR: {exc}")
        sys.exit(1)


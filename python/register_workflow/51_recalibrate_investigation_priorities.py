
from pathlib import Path
from datetime import datetime
import os
import shutil
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

OUTPUT_DIR = Path(r"C:\Project_03\outputs")

INITIAL_PATH = OUTPUT_DIR / "initial_findings_register.csv"
PRIORITIZED_PATH = OUTPUT_DIR / "prioritized_findings_register.csv"

EXPECTED_IDS = {f"DQ-{number:02d}" for number in range(1, 9)}

REQUIRED_COLUMNS = {
    "finding_id",
    "investigation_priority",
    "priority_rationale",
    "priority_status",
}

# Only these cells are permitted to change.
UPDATES = {
    "DQ-03": {
        "investigation_priority": "P3",
        "priority_rationale": (
            "All 10,324 records passed the follow-up rounding-consistency "
            "tests. No confirmed pricing defect or financial impact has "
            "been established. Retain as low-priority documentation and "
            "source-methodology follow-up. Reassess if new evidence "
            "indicates a business-impacting issue."
        ),
        "priority_status": (
            "Provisional - no confirmed pricing defect; low-priority "
            "follow-up pending source-methodology evidence"
        ),
    },
    "DQ-06": {
        "priority_rationale": (
            "Mixed numeric values, cross-record references, and explanatory "
            "text require explicit handling before reliable weight and "
            "freight analysis. DQ-07 covers a related reference-resolution "
            "aspect. Assess both findings together and avoid double-counting "
            "overlapping records or impacts."
        ),
        "priority_status": (
            "Provisional - operational impact and business rules remain "
            "unconfirmed; assess jointly with DQ-07"
        ),
    },
    "DQ-07": {
        "investigation_priority": "P2",
        "priority_rationale": (
            "Cross-record references may require documented value-transfer "
            "rules, but their meaning and downstream impact remain "
            "unconfirmed. This finding overlaps with DQ-06; assess jointly "
            "rather than treating it as an independent affected population."
        ),
        "priority_status": (
            "Provisional - reference semantics and impact unconfirmed; "
            "assess jointly with DQ-06"
        ),
    },
}


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def load_csv(path):
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def validate_ids(df, label):
    if "finding_id" not in df.columns:
        raise ValueError(f"{label}: finding_id column is missing.")

    if df["finding_id"].duplicated().any():
        duplicates = df.loc[
            df["finding_id"].duplicated(keep=False), "finding_id"
        ].tolist()
        raise ValueError(f"{label}: duplicate finding IDs: {duplicates}")

    actual_ids = set(df["finding_id"])

    if actual_ids != EXPECTED_IDS:
        raise ValueError(
            f"{label}: expected DQ-01 through DQ-08 exactly once.\n"
            f"Missing: {sorted(EXPECTED_IDS - actual_ids)}\n"
            f"Unexpected: {sorted(actual_ids - EXPECTED_IDS)}"
        )


def assert_shared_fields_match(initial_df, prioritized_df):
    shared = [
        column
        for column in initial_df.columns
        if column in prioritized_df.columns
    ]

    left = initial_df[shared].sort_values("finding_id").reset_index(drop=True)
    right = prioritized_df[shared].sort_values("finding_id").reset_index(drop=True)

    if not left.equals(right):
        raise ValueError(
            "Shared fields differ between the two registers. "
            "Resolve the discrepancy before recalibrating priorities."
        )


def assert_only_allowed_cells_changed(before, after):
    if list(before.columns) != list(after.columns):
        raise AssertionError("Register columns changed unexpectedly.")

    if len(before) != len(after):
        raise AssertionError("Register row count changed unexpectedly.")

    allowed = {
        (finding_id, column)
        for finding_id, fields in UPDATES.items()
        for column in fields
    }

    before_indexed = before.set_index("finding_id").sort_index()
    after_indexed = after.set_index("finding_id").sort_index()

    if list(before_indexed.columns) != list(after_indexed.columns):
        raise AssertionError("Register columns changed unexpectedly.")

    for finding_id in before_indexed.index:
        for column in before_indexed.columns:
            old_value = before_indexed.loc[finding_id, column]
            new_value = after_indexed.loc[finding_id, column]

            if old_value != new_value:
                if (finding_id, column) not in allowed:
                    raise AssertionError(
                        f"Unexpected change in {finding_id}, "
                        f"column '{column}'."
                    )


# ============================================================
# 3. PRE-FLIGHT CHECKS
# ============================================================

def main():
    if not OUTPUT_DIR.is_dir():
        raise FileNotFoundError(f"Output directory not found: {OUTPUT_DIR}")

    for path in (INITIAL_PATH, PRIORITIZED_PATH):
        if not path.is_file():
            raise FileNotFoundError(f"Required register not found: {path}")

    initial_before = load_csv(INITIAL_PATH)
    prioritized_before = load_csv(PRIORITIZED_PATH)

    validate_ids(initial_before, "Initial register")
    validate_ids(prioritized_before, "Prioritized register")

    missing_columns = REQUIRED_COLUMNS - set(prioritized_before.columns)
    if missing_columns:
        raise ValueError(
            f"Prioritized register is missing columns: "
            f"{sorted(missing_columns)}"
        )

    assert_shared_fields_match(initial_before, prioritized_before)

    # Confirm the intended target rows exist exactly once.
    for finding_id in UPDATES:
        count = (prioritized_before["finding_id"] == finding_id).sum()
        if count != 1:
            raise ValueError(
                f"{finding_id} appears {count} times; expected exactly once."
            )

    # Confirm DQ-06 remains P1, as agreed.
    current_priorities = prioritized_before.set_index("finding_id")[
        "investigation_priority"
    ]

    if current_priorities["DQ-06"] != "P1":
        raise ValueError(
            f"DQ-06 is currently {current_priorities['DQ-06']!r}, "
            "not P1. Review the register before proceeding."
        )

    # If the intended update has already been applied, do not rewrite files.
    already_applied = True

    for finding_id, fields in UPDATES.items():
        for column, expected_value in fields.items():
            actual_value = prioritized_before.loc[
                prioritized_before["finding_id"] == finding_id, column
            ].iloc[0]

            if actual_value != expected_value:
                already_applied = False

    if already_applied:
        print("No changes needed: the intended recalibration is already present.")
        print("Both registers were left untouched.")
        return

    # Ensure we are updating from the expected starting priorities.
    if current_priorities["DQ-03"] != "P1":
        raise ValueError(
            "DQ-03 is not currently P1. Review its existing priority "
            "before applying this recalibration."
        )

    if current_priorities["DQ-07"] != "P1":
        raise ValueError(
            "DQ-07 is not currently P1. Review its existing priority "
            "before applying this recalibration."
        )

    # ========================================================
    # 4. PREPARE CHANGES IN MEMORY
    # ========================================================

    updated = prioritized_before.copy()

    for finding_id, fields in UPDATES.items():
        mask = updated["finding_id"] == finding_id

        for column, value in fields.items():
            updated.loc[mask, column] = value

    assert_only_allowed_cells_changed(prioritized_before, updated)
    assert_shared_fields_match(initial_before, updated)

    # Verify the intended final priority distribution.
    final_priorities = updated.set_index("finding_id")[
        "investigation_priority"
    ]

    expected = {"DQ-03": "P3", "DQ-06": "P1", "DQ-07": "P2"}

    for finding_id, priority in expected.items():
        if final_priorities[finding_id] != priority:
            raise AssertionError(
                f"Unexpected final priority for {finding_id}."
            )

    # ========================================================
    # 5. BACK UP BOTH REGISTERS
    # ========================================================

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    initial_backup = OUTPUT_DIR / (
        f"initial_findings_register.backup_before_priority_recalibration_"
        f"{timestamp}.csv"
    )

    prioritized_backup = OUTPUT_DIR / (
        f"prioritized_findings_register.backup_before_priority_recalibration_"
        f"{timestamp}.csv"
    )

    if initial_backup.exists() or prioritized_backup.exists():
        raise FileExistsError(
            "A backup with this timestamp already exists. "
            "Run the script again in a moment."
        )

    shutil.copy2(INITIAL_PATH, initial_backup)
    shutil.copy2(PRIORITIZED_PATH, prioritized_backup)

    # ========================================================
    # 6. WRITE TEMPORARY FILE, VALIDATE, THEN REPLACE
    # ========================================================

    temp_path = OUTPUT_DIR / (
        f"prioritized_findings_register.tmp_{timestamp}.csv"
    )

    try:
        updated.to_csv(
            temp_path,
            index=False,
            encoding="utf-8-sig",
        )

        temp_check = load_csv(temp_path)

        if not updated.equals(temp_check):
            raise AssertionError(
                "Temporary CSV failed read-back validation. "
                "The existing prioritized register was not replaced."
            )

        assert_only_allowed_cells_changed(prioritized_before, temp_check)
        assert_shared_fields_match(initial_before, temp_check)

        # Detect unexpected external edits before replacing the register.
        initial_current = load_csv(INITIAL_PATH)
        prioritized_current = load_csv(PRIORITIZED_PATH)

        if not initial_before.equals(initial_current):
            raise RuntimeError(
                "Initial register changed during execution. "
                "The prioritized register was not replaced."
            )

        if not prioritized_before.equals(prioritized_current):
            raise RuntimeError(
                "Prioritized register changed during execution. "
                "The prioritized register was not replaced."
            )

        # Atomic replacement within the same directory.
        os.replace(temp_path, PRIORITIZED_PATH)

        final_check = load_csv(PRIORITIZED_PATH)

        if not updated.equals(final_check):
            raise AssertionError(
                "Final read-back differs from the intended register. "
                f"Use this backup for recovery if needed: {prioritized_backup}"
            )

        assert_only_allowed_cells_changed(prioritized_before, final_check)
        assert_shared_fields_match(initial_before, final_check)

    finally:
        if temp_path.exists():
            temp_path.unlink()

    # ========================================================
    # 7. REPORT RESULTS
    # ========================================================

    print("\n=== PRIORITY RECALIBRATION PASSED ===")
    print("PASS: DQ-03 changed from P1 to P3.")
    print("PASS: DQ-06 remains P1; overlap with DQ-07 documented.")
    print("PASS: DQ-07 changed from P1 to P2.")
    print("PASS: All non-target cells remain unchanged.")
    print("PASS: Shared fields still agree between registers.")
    print("PASS: Temporary file and final disk read-back validated.")
    print("PASS: Initial register unchanged.")
    print("PASS: Raw dataset was not accessed or modified.")

    print("\n=== FINAL PRIORITIES ===")
    print(
        final_check[
            ["finding_id", "investigation_priority", "priority_status"]
        ].to_string(index=False)
    )

    print("\n=== PRIORITY DISTRIBUTION ===")
    print(
        final_check["investigation_priority"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\n=== BACKUPS CREATED ===")
    print(initial_backup)
    print(prioritized_backup)


if __name__ == "__main__":
    main()

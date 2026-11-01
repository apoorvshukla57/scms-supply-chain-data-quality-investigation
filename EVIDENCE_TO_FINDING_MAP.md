# Evidence-to-Finding Map

## 1. Purpose

This document maps the eight findings in the finalized prioritized findings register to the evidence files selected for publication.

It documents the role of each selected evidence file, its relationship to the findings, and the limitations of the published evidence package.

The publication package contains **32 unique selected CSV files**. All 32 files were SHA-256 compared against their original project output files, with zero mismatches.

This confirms file-copy integrity. It does not establish that every result has been independently reproduced or that every selected file has been regenerated during publication QA.

## 2. Publication principles

- Preserve the original source dataset and investigation outputs.
- Do not publish historical register backups or temporary files.
- Distinguish summary evidence from detailed record-level audit evidence.
- Do not treat an investigated exception as a confirmed business defect.
- Preserve the assumptions, tolerances, and limitations of each investigation.
- Do not automatically correct, impute, or deduplicate source records.
- Assess DQ-06 and DQ-07 jointly because their underlying records overlap.
- Distinguish files selected for publication from supplementary outputs retained in the original project.
- Do not claim comprehensive evidence coverage where the selected package contains only summary or partial record-level evidence.

## 3. Finding-to-evidence mapping

### DQ-01 — Missing dosage

**Priority:** P2

**Core evidence:**
- `missing_dosage_by_product_group.csv`
- `missing_dosage_by_sub_classification.csv`

**Detailed audit evidence:**
- `missing_dosage_records_for_review.csv`

**Interpretation:**

Missing dosage is concentrated in diagnostic test products, with eight additional malaria records. Applicability and business impact remain unconfirmed.

The detailed review file preserves the affected records for follow-up. Missing dosage should not automatically be interpreted as an error where dosage may not be applicable.

### DQ-02 — Date-field quality

**Priority:** P1

**Core evidence:**
- `date_field_quality_summary.csv`

**Detailed audit evidence:**
- `date_field_quality_exceptions.csv`

**Interpretation:**

Two date fields contain recognized workflow labels and explicitly unavailable values. Workflow meanings have not been independently verified. No other unparseable text was found across the five audited date fields.

The exception file supports record-level review. Recognized date formats and chronological relationships do not, by themselves, establish that the underlying business events were recorded correctly.

### DQ-03 — Pricing arithmetic and recorded precision

**Priority:** P3

**Core evidence:**
- `pricing_discrepancy_overall.csv`
- `pricing_discrepancy_by_product_group.csv`
- `pricing_rounding_hypothesis_overall.csv`
- `unit_price_uom_rounding_overall.csv`
- `unit_price_uom_rounding_by_group.csv`
- `unit_price_uom_rounding_noncomparable.csv`
- `unit_price_uom_rounding_record_checks.csv`
- `line_value_relationship_overall.csv`
- `line_value_rounding_by_group.csv`

**Interpretation:**

The initial pack-price arithmetic test identified 7,774 exceptions. The separate rounded unit-price-times-UOM test brought 90 within the $0.02 tolerance, leaving 7,684 outside it.

Separately, 549 line-value exceptions passed the implied-pack-price rounding test.

These are distinct analytical tests and must not be conflated.

The selected publication package includes the overall rounding summary, a product-group breakdown, and record-level checks for all 10,324 records. The noncomparable-record output contains zero records, confirming that all 10,324 records were included in this test.

The package does not include the full line-value rounding exception and flagged-review files.

These results are investigative arithmetic findings, not confirmed pricing defects or evidence of financial loss. The source-system pricing convention remains unconfirmed.

### DQ-04 — Zero unit prices

**Priority:** P2

**Core evidence:**
- `zero_unit_price_by_group.csv`
- `zero_unit_price_by_product.csv`

**Supplementary evidence:**
- `zero_unit_price_positive_comparison.csv`

**Detailed audit evidence:**
- `zero_unit_price_records.csv`

**Interpretation:**

There are 103 zero-unit-price records. The safety-lancet product has a concentrated pattern, but the reason for the observed price differences remains unverified.

The detailed file preserves the zero-unit-price records for review. No automatic price correction is recommended.

### DQ-05 — Potential duplicate shipment records

**Priority:** P2

**Core evidence:**
- `potential_duplicate_groups.csv`

**Detailed audit evidence:**
- `potential_duplicate_records.csv`

**Interpretation:**

Four candidate pairs involving eight records match across all 32 non-ID fields. Duplicate status is unconfirmed.

These are candidate matches, not confirmed duplicate shipments. No records should be deleted or deduplicated solely on the basis of this investigation.

### DQ-06 — Weight and freight usability

**Priority:** P1

**Core evidence:**
- `weight_freight_classification_summary.csv`
- `weight_freight_refined_categories.csv`

**Detailed audit evidence:**
- `weight_freight_reference_examples.csv`

**Interpretation:**

Weight and freight fields contain numeric values, cross-record references, and explanatory text. Reference semantics and value-transfer rules remain unverified.

The selected evidence includes classification summaries, refined categories, and detailed cross-record reference examples.

The full record-level classification file and nonnumeric-example file are not included in the 32-file publication package. Therefore, the published package does not provide a complete record-level audit trail for every weight and freight value classification.

### DQ-07 — Cross-record reference integrity

**Priority:** P2

**Core evidence:**
- `weight_freight_reference_examples.csv`

**Related evidence:**
- `weight_freight_refined_categories.csv`

**Interpretation:**

There are 4,890 field-level reference occurrences across 2,445 source records. Both fields point to the same target record in each case, and the tested target identifiers and ASN/DN references reconcile.

The reference examples file provides the detailed record-level evidence for this finding. It is shared with DQ-06 because the same source records support both the value-usability and cross-record-reference investigations.

DQ-07 overlaps with DQ-06. Their record populations or impacts must not be added together.

### DQ-08 — Missing insurance

**Priority:** P2

**Core evidence:**
- `missing_insurance_by_product_group.csv`
- `missing_insurance_by_shipment_mode.csv`

**Supplementary evidence:**
- `missing_insurance_by_country.csv`
- `missing_insurance_by_fulfill_via.csv`

**Detailed audit evidence:**
- `missing_insurance_records_for_review.csv`

**Interpretation:**

There are 287 records with missing insurance values. Applicability, cause, and financial impact remain unconfirmed.

The overlap with missing shipment mode should be considered during follow-up. Missing insurance should not automatically be interpreted as a missing insurance policy or an uninsured shipment.

## 4. Shared governance and validation evidence

These four files support the overall findings register and publication QA rather than one individual finding:

- `initial_findings_register.csv`
- `prioritized_findings_register.csv`
- `register_evidence_verification.csv`
- `section04_register_reconciliation.csv`

**Important limitations:**

- The prioritized register preserves the finalized eight-finding priority baseline.
- The register evidence verification file contains selected checks and should not be described as comprehensive independent validation of all eight findings.
- The Section 04 reconciliation checks finding IDs and priorities against the expected baseline. It does not independently validate the underlying analytical evidence.

The historical `final_evidence_manifest.csv` is not part of the selected 32-file package. It records file existence, size, and modification time, but does not provide cryptographic hashes. It must not be treated as the definitive publication snapshot.

## 5. Appendix — Publication Evidence Index

The publication evidence package contains **32 unique selected CSV files**, mapped across the eight investigation findings and shared governance checks.

All 32 selected files were compared against their original project output files using SHA-256 hashes. All 32 matched, with zero mismatches. This confirms file-copy integrity, not independent reproduction of every analytical result.

### 5.1 Finding-Level Evidence

#### DQ-01 — Missing dosage

**Priority:** P2

**Core evidence**
- `missing_dosage_by_product_group.csv`
- `missing_dosage_by_sub_classification.csv`

**Detailed audit evidence**
- `missing_dosage_records_for_review.csv`

These files summarize missing dosage by product group and subclassification and preserve affected records for follow-up. Missing dosage should not automatically be interpreted as an error where dosage may not be applicable.

#### DQ-02 — Date-field quality

**Priority:** P1

**Core evidence**
- `date_field_quality_summary.csv`

**Detailed audit evidence**
- `date_field_quality_exceptions.csv`

These files support review of date-field categories and record-level exceptions. Workflow meanings have not been independently verified. Recognized date formats and chronological relationships do not, by themselves, establish that the underlying business events were recorded correctly.

#### DQ-03 — Pricing arithmetic and recorded precision

**Priority:** P3

**Core evidence**
- `pricing_discrepancy_overall.csv`
- `pricing_discrepancy_by_product_group.csv`
- `pricing_rounding_hypothesis_overall.csv`
- `unit_price_uom_rounding_overall.csv`
- `unit_price_uom_rounding_by_group.csv`
- `unit_price_uom_rounding_noncomparable.csv`
- `unit_price_uom_rounding_record_checks.csv`
- `line_value_relationship_overall.csv`
- `line_value_rounding_by_group.csv`

The initial pack-price arithmetic test identified 7,774 exceptions. The separate rounded unit-price-times-UOM test brought 90 within the $0.02 tolerance, leaving 7,684 outside it.

Separately, 549 line-value exceptions passed the implied-pack-price rounding test. These are distinct analytical tests and must not be conflated.

The selected publication package includes the overall rounding summary, a product-group breakdown, and record-level checks for all 10,324 records. The noncomparable-record output contains zero records, confirming that all 10,324 records were included in this test.

The package does not include the full line-value rounding exception and flagged-review files. These results are investigative arithmetic findings, not confirmed pricing defects or evidence of financial loss. The source-system pricing convention remains unconfirmed.

#### DQ-04 — Zero unit prices

**Priority:** P2

**Core evidence**
- `zero_unit_price_by_group.csv`
- `zero_unit_price_by_product.csv`

**Supplementary evidence**
- `zero_unit_price_positive_comparison.csv`

**Detailed audit evidence**
- `zero_unit_price_records.csv`

These files summarize zero unit prices, provide product-level context, and preserve affected records for review. The reason for the observed price patterns remains unverified. No automatic price correction is recommended.

#### DQ-05 — Potential duplicate shipment records

**Priority:** P2

**Core evidence**
- `potential_duplicate_groups.csv`

**Detailed audit evidence**
- `potential_duplicate_records.csv`

Four candidate pairs involving eight records match across all 32 non-ID fields. Duplicate status is unconfirmed. These are candidate matches, not confirmed duplicate shipments. No records should be deleted or deduplicated solely on the basis of this investigation.

#### DQ-06 — Weight and freight usability

**Priority:** P1

**Core evidence**
- `weight_freight_classification_summary.csv`
- `weight_freight_refined_categories.csv`

**Detailed audit evidence**
- `weight_freight_reference_examples.csv`

Weight and freight fields contain numeric values, cross-record references, and explanatory text. Reference semantics and value-transfer rules remain unverified.

The selected evidence includes classification summaries, refined categories, and detailed cross-record reference examples.

The full record-level classification file and nonnumeric-example file are not included in the 32-file publication package. Therefore, the published package does not provide a complete record-level audit trail for every weight and freight value classification.

#### DQ-07 — Cross-record reference integrity

**Priority:** P2

**Core evidence**
- `weight_freight_reference_examples.csv`

**Related evidence**
- `weight_freight_refined_categories.csv`

There are 4,890 field-level reference occurrences across 2,445 source records. Both fields point to the same target record in each case, and the tested target identifiers and ASN/DN references reconcile.

The reference examples file provides detailed record-level evidence for this finding. It is shared with DQ-06 because the same source records support both the value-usability and cross-record-reference investigations.

DQ-07 overlaps with DQ-06. Their record populations or impacts must not be added together.

#### DQ-08 — Missing insurance

**Priority:** P2

**Core evidence**
- `missing_insurance_by_product_group.csv`
- `missing_insurance_by_shipment_mode.csv`

**Supplementary evidence**
- `missing_insurance_by_country.csv`
- `missing_insurance_by_fulfill_via.csv`

**Detailed audit evidence**
- `missing_insurance_records_for_review.csv`

There are 287 records with missing insurance values. Applicability, cause, and financial impact remain unconfirmed.

The overlap with missing shipment mode should be considered during follow-up. Missing insurance should not automatically be interpreted as a missing insurance policy or an uninsured shipment.

### 5.2 Shared Governance and Validation Evidence

These four files support the overall findings register and publication QA rather than one individual finding:

- `initial_findings_register.csv`
- `prioritized_findings_register.csv`
- `register_evidence_verification.csv`
- `section04_register_reconciliation.csv`

**Important limitations**

- The prioritized register preserves the finalized eight-finding priority baseline.
- The register evidence verification file contains selected checks and should not be described as comprehensive independent validation of all eight findings.
- The Section 04 reconciliation checks finding IDs and priorities against the expected baseline. It does not independently validate the underlying analytical evidence.

The historical `final_evidence_manifest.csv` is not part of the selected 32-file package. It records file existence, size, and modification time, but does not provide cryptographic hashes. It must not be treated as the definitive publication snapshot.

### 5.3 Publication Evidence Inventory

The following table accounts for all 32 unique selected files.

| Finding or purpose | File assignments |
|---|---:|
| DQ-01 | 3 |
| DQ-02 | 2 |
| DQ-03 | 9 |
| DQ-04 | 4 |
| DQ-05 | 2 |
| DQ-06 | 3 |
| DQ-07 | 1 shared file |
| DQ-08 | 5 |
| Shared governance and validation | 4 |
| **Total assignments** | **33** |
| **Unique publication files** | **32** |

The DQ-06 and DQ-07 reference-example file is counted once in the unique publication total. Consequently, the 33 finding/purpose assignments correspond to 32 unique files.

The complete file-level inventory, including file sizes, row counts, and SHA-256 values, is maintained in:

`PUBLICATION_EVIDENCE_MANIFEST.csv`

### 5.4 Evidence Intentionally Not Included

The following original project outputs are not part of the selected 32-file package:

- `line_value_rounding_exceptions.csv`
- `line_value_rounding_flagged_review.csv`
- `weight_freight_value_classification.csv`
- `weight_freight_nonnumeric_examples.csv`

They remain separate from the selected publication evidence package. Their omission is a publication-scope decision, not a conclusion that the underlying analyses or files are invalid.

Other intermediate outputs, historical backups, temporary files, and unselected record-level exports are also excluded unless a specific publication or audit requirement justifies their inclusion.

### 5.5 Publication Verification Status

| Check | Status |
|---|---|
| Selected evidence files identified | Complete |
| Selected evidence files copied | Complete |
| SHA-256 comparison against originals | 32/32 matched |
| Hash mismatches | 0 |
| Evidence-to-finding mapping | Reconciled to 32 unique files and 33 assignments |
| Full independent rerun of all investigations | Not completed |
| Regeneration of all 32 files from publication scripts | Not completed |
| Comprehensive record-level evidence for every finding | Not claimed |

The publication manifest provides file-level integrity evidence. It does not replace analytical validation or controlled execution testing.

### 5.6 Reproducibility and Limitations

The findings are based on the supplied SCMS shipment dataset and the investigations documented in the project.

Some business rules, workflow labels, pricing conventions, and operational meanings could not be independently confirmed from the available source documentation.

The investigation therefore distinguishes observed patterns, tested relationships, and unresolved business interpretations.

The selected publication evidence package is intentionally limited to 32 unique files. Some detailed intermediate and record-level outputs remain in the original project rather than being included in the public package.

No unsupported claims of financial loss, confirmed fraud, confirmed duplicate shipments, or confirmed operational failure should be made.

The publication package is intended to make the selected findings traceable and reviewable without implying that every unresolved business interpretation has been settled.

## 6. Evidence intentionally not included

The following original project outputs are not part of the selected 32-file package:

- `line_value_rounding_exceptions.csv`
- `line_value_rounding_flagged_review.csv`
- `weight_freight_value_classification.csv`
- `weight_freight_nonnumeric_examples.csv`

They remain separate from the selected publication evidence package. Their omission is a publication-scope decision, not a conclusion that the underlying analyses or files are invalid.

Other intermediate outputs, historical backups, temporary files, and unselected record-level exports are also excluded unless a specific publication or audit requirement justifies their inclusion.

## 7. Publication verification status

| Check | Status |
|---|---|
| Selected evidence files identified | Complete |
| Selected evidence files copied | Complete |
| SHA-256 comparison against originals | 32/32 matched |
| Hash mismatches | 0 |
| Evidence-to-finding mapping | Reconciled to 32 unique files and 33 assignments |
| Full independent rerun of all investigations | Not completed |
| Regeneration of all 32 files from publication scripts | Not completed |
| Comprehensive record-level evidence for every finding | Not claimed |

The publication manifest provides file-level integrity evidence. It does not replace analytical validation or controlled execution testing.

## 8. Reproducibility and limitations

The findings are based on the supplied SCMS shipment dataset and the investigations documented in the project.

Some business rules, workflow labels, pricing conventions, and operational meanings could not be independently confirmed from the available source documentation.

The investigation therefore distinguishes observed patterns, tested relationships, and unresolved business interpretations.

The selected publication evidence package is intentionally limited to 32 unique files. Some detailed intermediate and record-level outputs remain in the original project rather than being included in the public package.

No unsupported claims of financial loss, confirmed fraud, confirmed duplicate shipments, or confirmed operational failure should be made.

The publication package is intended to make the selected findings traceable and reviewable without implying that every unresolved business interpretation has been settled.
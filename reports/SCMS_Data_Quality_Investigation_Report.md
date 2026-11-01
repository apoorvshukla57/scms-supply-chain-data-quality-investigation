# The Data Nobody Wants to Clean

## Supply Chain Shipment Data Quality Investigation

**Project type:** Data Quality Investigation  
**Dataset:** SCMS Supply Chain Shipment Data  
**Records investigated:** 10,324  
**Tools:** Python · pandas · PostgreSQL  
**Report status:** Final review

---

## 1. Executive Summary

This investigation assessed the quality, consistency, and interpretability of 10,324 supply chain shipment records covering health commodity procurement and delivery activities.

The analysis examined missing information, date-field consistency, pricing calculations, zero-price records, potential duplicate shipments, and explanatory text embedded in numeric logistics fields.

### Key Findings

- **Date-field exceptions:** 2,476 records contain `Pre-PQ Process` in the first purchase-qualification date field, while 5,404 contain `N/A - From RDC` in the purchase-order date field.
- **Chronology requiring review:** 2,814 records (27.26%) show delivery before the scheduled date, while 1,186 (11.49%) show delivery after the scheduled date. Three records have a delivery-recorded date earlier than the delivered-to-client date and warrant targeted review.
- **Mixed numeric and explanatory values:** Weight is numeric in 61.72% of records and freight cost is numeric in 60.03%.
- **Zero unit prices:** 103 records have a recorded unit price of zero. These require contextual validation before being interpreted as pricing errors.
- **Potential duplicate records:** Four pairs match across all 32 non-ID fields. These are candidates for investigation, not confirmed duplicate shipments.
- **Missing operational information:** Dosage is missing in 1,736 records (16.82%). Insurance information is missing in 287 records (2.78%), and shipment mode is missing in 360 records.

### Pricing Interpretation

An initial comparison flagged 7,774 records for differences between pack price and unit price multiplied by units per pack.

Further analysis found that, across all 10,324 records, the recorded unit price matched the pack price divided by units per pack (UOM), rounded to two decimal places. This is an observed arithmetic relationship; the source system's intended pricing methodology remains unconfirmed.

A separate line-item-value comparison identified 549 records with differences exceeding $0.02. All 549 also passed the implied-pack-price rounding test. These findings do not establish confirmed pricing errors or financial losses.

### Overall Assessment

The dataset contains process-specific text, date-field exceptions, and records requiring contextual validation. These patterns should be addressed through documented business rules and targeted source-owner review rather than automatic deletion, imputation, or correction.

The recommended next step is to prioritize the highest-impact data-quality questions, establish consistent field interpretations, and create a repeatable validation process before relying on affected fields for operational reporting.

---

## 2. Findings and Priorities

| Finding | Priority | Evidence | Recommended Action |
|---|---|---|---|
| DQ-01 — Missing dosage | P2 | 1,736 records (16.82%) lack dosage information. Of these, 1,728 belong to HRDT and 8 to MRDT. | Confirm dosage applicability against authoritative product specifications. Investigate the eight malaria records separately; do not automatically impute values. |
| DQ-02 — Date exceptions and chronology | P1 | 2,476 `Pre-PQ Process` and 205 `Date Not Captured` values in the PQ first-sent field; 5,404 `N/A - From RDC` and 328 `Date Not Captured` values in the PO-sent field; three recorded-date chronology exceptions. | Define approved interpretations for non-date values and review chronology exceptions with the source owner. |
| DQ-03 — Pricing arithmetic and rounding | P3 | 7,774 records initially exceeded the $0.02 tolerance when comparing pack price with unit price × UOM. Separately, all 10,324 recorded unit prices matched pack price ÷ UOM rounded to two decimals. Of 549 separate line-value differences, all passed the implied-pack-price rounding test. The source system's intended calculation method remains unconfirmed. | Document the observed rounding relationships and obtain authoritative source-methodology evidence before classifying any remaining arithmetic differences. Do not treat these results as confirmed pricing defects or financial losses. |
| DQ-04 — Zero unit prices | P2 | 103 zero unit-price records; 85 have positive pack prices. | Validate price units, pricing conventions, and transaction context before changing values. |
| DQ-05 — Potential duplicates | P2 | Four pairs match across all 32 non-ID fields but have different IDs. | Compare against shipment documents and source-system identifiers before any deduplication. |
| DQ-06 — Mixed weight and freight values | P1 | Weight is numeric in 6,372 records (61.72%); freight cost is numeric in 6,198 records (60.03%). The remaining values include explanatory text and cross-record references. | Separate numeric values, explanatory text, and cross-record references using documented rules. |
| DQ-07 — Cross-record references | P2 | 2,445 records contain references in both fields. The tested references point to the same target and match the corresponding document numbers. | Resolve jointly with DQ-06 and confirm the operational meaning before copying any values. |
| DQ-08 — Missing insurance and shipment mode | P2 | Insurance missing in 287 records; shipment mode missing in 360; both missing in 106. | Review records missing both fields first, then investigate the remaining gaps. |

### Priority Interpretation

- **P1 — High:** Resolve definitions or validation rules affecting the usability of core operational data.
- **P2 — Medium:** Investigate targeted completeness, pricing, duplication, and reference-handling questions.
- **P3 — Lower:** Document observed calculation behaviour and retain reviewed exceptions unless new evidence establishes a defect.

These labels represent investigation priorities, not confirmed financial losses or measured operational harm.

### Interpretation Safeguards

1. Missing or nonnumeric values are not automatically errors.
2. Chronology exceptions require confirmation of date-field meanings.
3. A zero price is not necessarily an incorrect price.
4. Matching records are not necessarily duplicate shipments.
5. A valid cross-record reference does not establish permission to copy values.
6. Pricing differences that pass the documented rounding test should not be reported as confirmed pricing defects.

---

## 3. Recommended Action Plan

The recommended actions focus on clarifying business rules, validating exceptions against authoritative records, and improving the reliability of downstream reporting. No source values should be changed solely on the basis of these findings.

### Phase 1 — Resolve High-Priority Interpretation Risks

| Action | Related Finding | Required Evidence | Completion Criteria |
|---|---|---|---|
| Define the meaning of non-date values in PQ and PO date fields. | DQ-02 | Approved source-system definitions and process documentation. | Each non-date category has a documented interpretation and an agreed reporting treatment. |
| Validate the meaning and permitted use of weight and freight references. | DQ-06, DQ-07 | Referenced shipment records, document definitions, and confirmation from the source owner. | Reference values have documented handling rules; unresolved cases remain explicitly identified. |
| Review delivery chronology exceptions. | DQ-02 | Shipment documents and confirmation of the meaning of scheduled, delivered, and recorded dates. | The three records where recorded delivery precedes delivery-to-client date are reviewed and their disposition documented. |

### Phase 2 — Validate Completeness and Transaction Records

| Action | Related Finding | Required Evidence | Completion Criteria |
|---|---|---|---|
| Confirm when dosage information is applicable. | DQ-01 | Authoritative product specifications and applicable product classifications. | Missing dosage is classified as required, not applicable, or unresolved using documented rules. |
| Investigate zero unit-price records. | DQ-04 | Price lists, unit definitions, pack configuration, and relevant transaction documents. | Zero-price records are classified according to verified business rules without unsupported corrections. |
| Investigate potential duplicate pairs. | DQ-05 | Shipment IDs, delivery documents, and source-system transaction identifiers. | Each pair is documented as a confirmed duplicate, a legitimate separate record, or unresolved. |
| Review records missing insurance and shipment mode. | DQ-08 | Source documents and field-applicability rules. | Missing-both records are reviewed first, followed by the remaining gaps; outcomes are recorded. |

### Phase 3 — Standardize Validation and Reporting

| Action | Related Finding | Required Evidence | Completion Criteria |
|---|---|---|---|
| Document the pricing calculation and rounding convention. | DQ-03 | Approved calculation rules and source-system definitions. | Validation checks account for the confirmed rounding method and distinguish expected rounding from unresolved differences. |
| Establish reusable data-quality checks. | DQ-01 to DQ-08 | Approved field definitions, thresholds, and exception-handling rules. | Checks produce repeatable counts, exception-level evidence, and a documented review status. |
| Maintain an exception register. | All findings | Finding ID, record ID, issue category, review owner, decision, evidence, and status. | Every investigated exception can be traced to evidence and a documented disposition. |

### Governance Principles

- Preserve the original source data.
- Never replace missing values or explanatory text without an approved business rule.
- Do not remove potential duplicates without transaction-level confirmation.
- Keep unresolved records visible in reporting rather than silently excluding them.
- Record the evidence, decision, and rationale for each approved correction.
- Re-run validation checks after approved changes and compare results with the original baseline.

### Expected Outcome

Implementing these actions should improve the interpretability, traceability, and consistency of supply chain reporting. The actual improvement should be measured after the source owner confirms the business rules and the agreed validation checks are implemented.

---

## 4. Investigation Methodology and Limitations

### 4.1 Dataset and Scope

The investigation examined 10,324 records from the SCMS supply chain shipment dataset. The analysis focused on data completeness, field interpretability, date consistency, pricing arithmetic, potential duplicate records, and cross-record references.

The investigation retained the original source values and used separate analytical outputs to document findings and exceptions.

### 4.2 Investigation Approach

The work followed a structured, evidence-led process:

1. **Structural validation:** Examined record counts, column structure, ID uniqueness, and exact duplicate rows.
2. **Field-level profiling:** Classified missing, numeric, nonnumeric, and explanatory values in selected fields.
3. **Date investigation:** Examined date-field exceptions, date parsing, delivery chronology, and selected records requiring review.
4. **Pricing reconciliation:** Compared recorded prices and line-item values with calculated values, including a two-decimal rounding test.
5. **Record-level investigation:** Examined zero unit prices, potential duplicate pairs, and cross-record references.
6. **Prioritization:** Recorded findings in a prioritized register using finding IDs, evidence, and proposed actions.
7. **Evidence reconciliation:** Compared selected headline metrics with the findings register and reconciled Section 4 SQL findings against the prioritized register.

### 4.3 Tools and Reproducibility

The investigation used Python with pandas for data profiling and evidence-file generation, PostgreSQL for SQL-based investigation and reconciliation, and CSV outputs for record-level and aggregate evidence.

The SQL investigation is maintained in:

`SQL/project_03_sql_analysis.sql`

The source dataset is stored under `dataset/`, while investigation outputs and supporting evidence are maintained under `outputs/`.

The report is intended to remain traceable to the supporting queries, scripts, and evidence files. Counts should be revalidated if source data or business rules change.

### 4.4 Limitations

**Business definitions are not fully established.**

The analysis identifies patterns in recorded values, but some interpretations require confirmation from the dataset owner or authoritative business documentation.

**Nonnumeric values are not automatically errors.**

Values such as `Pre-PQ Process`, `N/A - From RDC`, and cross-record references may encode legitimate operational context. Their intended meanings must be confirmed before transformation.

**Date consistency is not proof of operational correctness.**

Chronology checks identify records requiring review. They do not establish that a shipment event was recorded incorrectly, because the meaning and timing of each date field may differ.

**Pricing consistency does not establish financial accuracy.**

The rounding tests explain the observed arithmetic patterns under the tested calculation rules. They do not independently verify invoices, contractual prices, currency conventions, or the original calculation method.

**Potential duplicates remain candidates.**

Records matching across non-ID fields may represent separate legitimate transactions. Shipment documentation or source-system identifiers are required before deduplication.

**No unverified corrections were applied.**

The findings support targeted validation and documented remediation. They do not authorize automatic imputation, deletion, or replacement of original values.

**Selected metric checks have a defined scope.**

The evidence verification and register reconciliation checks validate selected headline metrics and finding-register consistency. They should not be interpreted as independent verification of every statement or every record in the full report.

### 4.5 Interpretation Standard

Findings are presented as observed patterns, calculated exceptions, or review candidates according to the evidence available. Where business meaning or source documentation is unavailable, the report explicitly identifies the issue as unresolved.

The investigation does not claim confirmed financial losses, root causes, or measured improvements without supporting evidence.

---

## 5. Appendix — Evidence Index

The following evidence files support the investigation findings. Aggregate files summarize patterns, while exception-level files support targeted record review. The files are maintained in the project's `outputs/` directory.

| Finding | Evidence file | Purpose |
|---|---|---|
| DQ-01 — Missing dosage | `missing_dosage_by_product_group.csv` | Summarizes missing dosage by product group. |
| DQ-01 — Missing dosage | `missing_dosage_by_sub_classification.csv` | Examines missing dosage by product subclassification. |
| DQ-02 — Date exceptions | `date_field_quality_summary.csv` | Summarizes date-field quality categories. |
| DQ-02 — Date exceptions | `date_field_quality_exceptions.csv` | Supports review of date-field exceptions. |
| DQ-03 — Pricing | `line_value_rounding_by_group.csv` | Summarizes line-value rounding results by product group. |
| DQ-03 — Pricing | `line_value_rounding_exceptions.csv` | Contains records failing the implied-price rounding test, if any; the investigation found no mismatches in the tested population. |
| DQ-04 — Zero unit prices | `zero_unit_price_by_group.csv` | Summarizes zero unit prices by product group. |
| DQ-04 — Zero unit prices | `zero_unit_price_positive_comparison.csv` | Supports comparison of zero unit-price records with other price fields. |
| DQ-05 — Potential duplicates | `potential_duplicate_groups.csv` | Summarizes candidate duplicate groups. |
| DQ-05 — Potential duplicates | `potential_duplicate_records.csv` | Lists records in candidate duplicate groups. |
| DQ-06 — Weight and freight | `weight_freight_classification_summary.csv` | Summarizes numeric, blank, and nonnumeric classifications. |
| DQ-06 — Weight and freight | `weight_freight_refined_categories.csv` | Separates numeric values, explanatory text, and reference values. |
| DQ-06 — Weight and freight | `weight_freight_reference_examples.csv` | Provides examples of cross-record references. |
| DQ-07 — Cross-record references | `weight_freight_reference_examples.csv` | Supports inspection of reference patterns; consult the SQL investigation for reconciliation results. |
| DQ-08 — Missing insurance and shipment mode | `missing_insurance_by_shipment_mode.csv` | Examines missing insurance across shipment-mode categories. |
| DQ-08 — Missing insurance and shipment mode | `missing_insurance_by_product_group.csv` | Summarizes missing insurance by product group. |

### Register and Reconciliation Evidence

| Evidence file | Purpose |
|---|---|
| `initial_findings_register.csv` | Records the initial set of findings. |
| `prioritized_findings_register.csv` | Records the prioritized findings and their current priority levels. |
| `register_evidence_verification.csv` | Documents the verification status of selected headline metrics. |
| `section04_register_reconciliation.csv` | Documents the reconciliation between Section 4 SQL findings and the prioritized register. |
| `final_evidence_manifest.csv` | Records the selected evidence files and their manifest metadata. |

### Evidence Interpretation

- A file's presence confirms that an output exists; it does not independently validate every value within it.
- The headline-metric verification covers selected metrics, not every statement in the report.
- The register reconciliation confirms the tested finding IDs and priorities; it is not a complete audit of all analytical logic.
- Exception files support investigation and review. They do not, by themselves, prove that a record is erroneous.
- Source-owner confirmation remains necessary where the intended business meaning is not established by the available data.

### Project Artifacts

- **Source data:** `dataset/`
- **Python scripts:** `python/`
- **SQL investigation:** `SQL/project_03_sql_analysis.sql`
- **Supporting evidence:** `outputs/`
- **Investigation report:** `report/SCMS_Data_Quality_Investigation_Report.md`
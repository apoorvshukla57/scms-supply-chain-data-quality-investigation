-- ============================================================================
-- PROJECT 03: SCMS HEALTH COMMODITY SHIPMENT & PRICING DATA QUALITY
-- SQL investigation and reconciliation script
-- ============================================================================
--
-- Prerequisite: PostgreSQL database scms_data_quality, with the source table
-- raw.scms_shipments loaded using the original 33 source columns.
-- The source table is treated as raw evidence. This script contains SELECT
-- investigations and does not modify source records.
--
-- Execution note: Run statements individually, in section order. Statements
-- are read-only SELECT queries. The final findings CTE is a curated reporting
-- layer using previously validated evidence; it does not recalculate every
-- metric. DQ-03, DQ-04 and DQ-05 are Python-evidence-led (see coverage map).
--
-- Publication note: Superseded exploratory date checks and a redundant
-- scheduled-date query were removed. Retained investigations are read-only
-- SELECT statements. The final findings CTE is a curated reporting layer
-- based on validated Python/SQL evidence; it does not recalculate every metric.
-- ============================================================================

--
-- CONTENTS
-- 01. Database and raw-source validation
-- 02. DQ-01 and DQ-02: dosage and date quality
-- 03. DQ-06 and DQ-07: weight/freight reference validation
-- 04. DQ-08: insurance and shipment-mode completeness
-- 05. Consolidated findings and recommended actions
--
-- INVESTIGATION COVERAGE
-- SQL contains the database checks and investigations shown below.
-- DQ-03 (pricing arithmetic), DQ-04 (zero unit prices), and DQ-05
-- (potential duplicate pairs) are represented in the consolidated findings
-- using the completed Python evidence; this SQL file does not independently
-- reproduce those three investigations. Consult the Python evidence outputs
-- and findings register for their detailed tests and record-level evidence.
-- DQ-06 and DQ-07 describe overlapping aspects of the same 2,445-record
-- reference population and must not be added together as distinct records.
--
-- 01 — Database & Raw Data Validation

-- Database/schema setup, table structure, import checks, row counts, ID uniqueness, and source-value validation.

-- QUERY: Source-value spot checks

SELECT
    COUNT(*) FILTER (
        WHERE pq_first_sent_to_client_date = 'Pre-PQ Process'
    ) AS pq_workflow_labels,

    COUNT(*) FILTER (
        WHERE po_sent_to_vendor_date = 'N/A - From RDC'
    ) AS po_rdc_labels,

    COUNT(*) FILTER (
        WHERE weight_kilograms LIKE 'See %'
    ) AS weight_reference_values,

    COUNT(*) FILTER (
        WHERE freight_cost_usd LIKE 'See %'
    ) AS freight_reference_values,

    COUNT(*) FILTER (
        WHERE country = 'Côte d''Ivoire'
    ) AS cote_divoire_records

FROM raw.scms_shipments;

-- Raw Import Validation — Passed

-- **Source:** Original SCMS shipment and pricing CSV
-- **Target:** `raw.scms_shipments` in PostgreSQL

-- **Structural validation**
-- - Imported rows: 10,324
-- - Unique IDs: 10,324
-- - Missing IDs: 0
-- - Raw table columns: 33

-- **Source-value validation**
-- - `Pre-PQ Process`: 2,476 records
-- - `N/A - From RDC`: 5,404 records
-- - Weight reference values: 2,445 records
-- - Freight reference values: 2,445 records
-- - Côte d’Ivoire records: 1,083

-- **Conclusion:** All checked counts match the established Python audit baselines. No discrepancy was detected in these validation checks.

-- **Limitation:** These checks validate selected counts and values, not every field in every row. Full row-level equivalence has not yet been established.

-- QUERY: Blank Values vs NULLs

SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE country IS NULL
    ) AS country_nulls,

    COUNT(*) FILTER (
        WHERE country = ''
    ) AS country_empty_strings,

    COUNT(*) FILTER (
        WHERE TRIM(country) = ''
    ) AS country_blank_or_whitespace,

    COUNT(*) FILTER (
        WHERE line_item_insurance_usd IS NULL
    ) AS insurance_nulls,

    COUNT(*) FILTER (
        WHERE line_item_insurance_usd = ''
    ) AS insurance_empty_strings

FROM raw.scms_shipments;

-- QUERY: Full-Table NULL and Blank-Value Audit.

SELECT
    v.column_name,

    COUNT(*) FILTER (
        WHERE v.value IS NULL
    ) AS null_count,

    COUNT(*) FILTER (
        WHERE v.value = ''
    ) AS empty_string_count,

    COUNT(*) FILTER (
        WHERE v.value IS NOT NULL
          AND v.value <> ''
          AND BTRIM(v.value) = ''
    ) AS whitespace_only_count

FROM raw.scms_shipments AS s

CROSS JOIN LATERAL (
    VALUES
        ('id', s.id),
        ('project_code', s.project_code),
        ('pq_number', s.pq_number),
        ('po_so_number', s.po_so_number),
        ('asn_dn_number', s.asn_dn_number),
        ('country', s.country),
        ('managed_by', s.managed_by),
        ('fulfill_via', s.fulfill_via),
        ('vendor_inco_term', s.vendor_inco_term),
        ('shipment_mode', s.shipment_mode),
        ('pq_first_sent_to_client_date', s.pq_first_sent_to_client_date),
        ('po_sent_to_vendor_date', s.po_sent_to_vendor_date),
        ('scheduled_delivery_date', s.scheduled_delivery_date),
        ('delivered_to_client_date', s.delivered_to_client_date),
        ('delivery_recorded_date', s.delivery_recorded_date),
        ('product_group', s.product_group),
        ('sub_classification', s.sub_classification),
        ('vendor', s.vendor),
        ('item_description', s.item_description),
        ('molecule_test_type', s.molecule_test_type),
        ('brand', s.brand),
        ('dosage', s.dosage),
        ('dosage_form', s.dosage_form),
        ('unit_of_measure_per_pack', s.unit_of_measure_per_pack),
        ('line_item_quantity', s.line_item_quantity),
        ('line_item_value', s.line_item_value),
        ('pack_price', s.pack_price),
        ('unit_price', s.unit_price),
        ('manufacturing_site', s.manufacturing_site),
        ('first_line_designation', s.first_line_designation),
        ('weight_kilograms', s.weight_kilograms),
        ('freight_cost_usd', s.freight_cost_usd),
        ('line_item_insurance_usd', s.line_item_insurance_usd)
) AS v(column_name, value)

GROUP BY v.column_name
ORDER BY v.column_name;

-- Full-Table Missing-Value Audit — Passed

-- **Scope:** 10,324 records × 33 columns in `raw.scms_shipments`.

-- - `dosage`: 1,736 NULLs (16.82%).
-- - `line_item_insurance_usd`: 287 NULLs (2.78%).
-- - `shipment_mode`: 360 NULLs (3.49%).
-- - All other 30 columns: zero NULLs.
-- - Empty strings: zero across all columns.
-- - Whitespace-only values: zero across all columns.

-- **Validation conclusion:** SQL missing-value counts agree with the previously established Python findings for dosage, insurance, and shipment mode.

-- **Interpretation limitation:** Missingness does not by itself establish invalidity, non-applicability, or business impact. Existing text values—including workflow labels and cross-record references—require separate interpretation.

-- **Data handling:** Raw table remains unchanged.

-- 02 — DQ-01 and DQ-02: Dosage and Date Quality

-- SQL investigations for dosage completeness and date-field quality. Pricing arithmetic, zero unit prices, and potential duplicate pairs are supported by the completed Python evidence, not independently recalculated in this SQL file.

-- QUERY: DQ-01 — Missing Dosage by Product Group.

SELECT
    product_group,
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE dosage IS NULL
    ) AS missing_dosage,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE dosage IS NULL
        ) / COUNT(*),
        2
    ) AS missing_dosage_pct

FROM raw.scms_shipments

GROUP BY product_group
ORDER BY missing_dosage DESC;

-- DQ-01 — Missing Dosage by Product Group

-- **SQL/Python cross-validation:** Passed.

-- - Total records: 10,324
-- - Missing dosage: 1,736 (16.82%)
-- - HRDT: 1,728 of 1,728 missing (100%)
-- - MRDT: 8 of 8 missing (100%)
-- - ARV, ANTM, ACT: zero missing dosage values

-- **Finding:** Missing dosage is entirely concentrated in the HRDT and MRDT product groups in this dataset.

-- **Recommended action:** Review dosage requirements for the affected diagnostic products before classifying these values as data-quality errors.

-- **Limitation:** Product-specific dosage requirements have not been verified. Missingness alone does not establish invalidity.

-- **Data handling:** Raw records remain unchanged.

-- ------------------------------------------------------------------------

SELECT
    sub_classification,
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE dosage IS NULL
    ) AS missing_dosage,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE dosage IS NULL
        ) / COUNT(*),
        2
    ) AS missing_dosage_pct

FROM raw.scms_shipments

GROUP BY sub_classification
ORDER BY missing_dosage DESC, total_records DESC;

-- DQ-01 — Missing Dosage by Subclassification

-- **SQL/Python cross-validation:** Passed for all six subclassifications.

-- - HIV test: 1,567/1,567 missing (100%).
-- - HIV test - Ancillary: 161/161 missing (100%).
-- - Malaria: 8/30 missing (26.67%).
-- - Adult: 0/6,595 missing.
-- - Pediatric: 0/1,955 missing.
-- - ACT: 0/16 missing.

-- **Finding:** Missing dosage is concentrated in diagnostic subclasses, with partial missingness in Malaria and no missingness in Adult, Pediatric, or ACT.

-- **Recommended action:** Validate dosage applicability at the product or item level before classifying records as defective.

-- **Limitation:** The analysis establishes a missingness pattern, not whether dosage is required for every item.

-- **Data handling:** Raw records remain unchanged.

-- QUERY: DQ-02 — PQ Date Field Classification

SELECT
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(pq_first_sent_to_client_date), '') IS NULL
    ) AS actual_missing_values,

    COUNT(*) FILTER (
        WHERE BTRIM(pq_first_sent_to_client_date) = 'Date Not Captured'
    ) AS unavailable_labels,

    COUNT(*) FILTER (
        WHERE BTRIM(pq_first_sent_to_client_date) = 'Pre-PQ Process'
    ) AS workflow_labels,

    COUNT(*) FILTER (
        WHERE BTRIM(pq_first_sent_to_client_date)
              ~ '^\d{1,2}/\d{1,2}/\d{4}$'
    ) AS date_format_candidates,

    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(pq_first_sent_to_client_date), '') IS NOT NULL
          AND BTRIM(pq_first_sent_to_client_date) <> 'Date Not Captured'
          AND BTRIM(pq_first_sent_to_client_date) <> 'Pre-PQ Process'
          AND BTRIM(pq_first_sent_to_client_date)
              !~ '^\d{1,2}/\d{1,2}/\d{4}$'
    ) AS other_values

FROM raw.scms_shipments;

-- DQ-02 — PQ Date Field Classification

-- **SQL/Python cross-validation:** Passed after correcting the SQL date-format pattern.

-- - Total records: 10,324
-- - SQL NULL/blank values: 0
-- - `Date Not Captured`: 205 (1.99%)
-- - `Pre-PQ Process`: 2,476 (23.98%)
-- - US-style date-format candidates: 7,643 (74.03%)
-- - Other values: 0

-- **Finding:** The field contains both workflow/unavailability labels and date-formatted values. These categories must be kept distinct when assessing date completeness.

-- **Limitation:** Matching the date format does not prove that every value is a valid calendar date.

-- **Data handling:** Raw records remain unchanged.

-- QUERY: DQ-02 — PO Sent to Vendor Date Classification

SELECT
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(po_sent_to_vendor_date), '') IS NULL
    ) AS actual_missing_values,

    COUNT(*) FILTER (
        WHERE BTRIM(po_sent_to_vendor_date) = 'N/A - From RDC'
    ) AS rdc_labels,

    COUNT(*) FILTER (
        WHERE BTRIM(po_sent_to_vendor_date)
              ~ '^\d{1,2}/\d{1,2}/\d{4}$'
    ) AS date_format_candidates,

    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(po_sent_to_vendor_date), '') IS NOT NULL
          AND BTRIM(po_sent_to_vendor_date) <> 'N/A - From RDC'
          AND BTRIM(po_sent_to_vendor_date)
              !~ '^\d{1,2}/\d{1,2}/\d{4}$'
    ) AS other_values

FROM raw.scms_shipments;

-- date_not_captured

SELECT
    BTRIM(po_sent_to_vendor_date) AS source_value,
    COUNT(*) AS record_count
FROM raw.scms_shipments
WHERE NULLIF(BTRIM(po_sent_to_vendor_date), '') IS NOT NULL
  AND BTRIM(po_sent_to_vendor_date) <> 'N/A - From RDC'
  AND BTRIM(po_sent_to_vendor_date)
      !~ '^\d{1,2}/\d{1,2}/\d{4}$'
GROUP BY 1
ORDER BY record_count DESC, source_value;

-- DQ-02 — Date Field Classification: SQL Validation Complete

-- **PQ first sent to client**
-- - Date-format candidates: 7,643 (74.03%)
-- - `Pre-PQ Process`: 2,476 (23.98%)
-- - `Date Not Captured`: 205 (1.99%)
-- - Other values: 0

-- **PO sent to vendor**
-- - Date-format candidates: 4,592 (44.48%)
-- - `N/A - From RDC`: 5,404 (52.34%)
-- - `Date Not Captured`: 328 (3.18%)
-- - Other values: 0

-- **Cross-validation:** All category counts match the established Python baseline.

-- **Interpretation:** These fields mix date-formatted values with workflow or unavailable-value labels. The labels must be preserved unless their business meaning and transformation rules are confirmed.

-- **Limitation:** Date-format matching alone does not establish calendar validity or the operational meaning of the labels.

-- **Data handling:** Raw records remain unchanged.

-- QUERY: DQ-02 — Remaining Date Fields Format Validation.

SELECT
    v.column_name,
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(v.source_value), '') IS NULL
    ) AS missing_values,

    COUNT(*) FILTER (
        WHERE BTRIM(v.source_value)
              ~ '^\d{1,2}-[A-Za-z]{3}-\d{2}$'
    ) AS date_format_candidates,

    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(v.source_value), '') IS NOT NULL
          AND BTRIM(v.source_value)
              !~ '^\d{1,2}-[A-Za-z]{3}-\d{2}$'
    ) AS other_values

FROM raw.scms_shipments AS s

CROSS JOIN LATERAL (
    VALUES
        ('scheduled_delivery_date', s.scheduled_delivery_date),
        ('delivered_to_client_date', s.delivered_to_client_date),
        ('delivery_recorded_date', s.delivery_recorded_date)
) AS v(column_name, source_value)

GROUP BY v.column_name
ORDER BY v.column_name;

-- DQ-02 — Date Field Classification: Validation Complete

-- **SQL/Python cross-validation:** Passed for all five date fields.

-- - PQ first sent to client: 7,643 date-format candidates; 2,476 `Pre-PQ Process`; 205 `Date Not Captured`.
-- - PO sent to vendor: 4,592 date-format candidates; 5,404 `N/A - From RDC`; 328 `Date Not Captured`.
-- - Scheduled delivery: 10,324 date-format candidates.
-- - Delivered to client: 10,324 date-format candidates.
-- - Delivery recorded: 10,324 date-format candidates.

-- No unexpected values were identified by the format checks.

-- **Limitation:** Format matching is not a complete calendar-validity test. The operational meaning of workflow and unavailable-value labels remains unverified.

-- **Data handling:** Raw records remain unchanged.

-- QUERY: DQ-02 — Calendar Format and Round-Trip Validation

WITH date_values AS (
    SELECT
        v.column_name,
        BTRIM(v.source_value) AS source_value
    FROM raw.scms_shipments AS s
    CROSS JOIN LATERAL (
        VALUES
            ('scheduled_delivery_date', s.scheduled_delivery_date),
            ('delivered_to_client_date', s.delivered_to_client_date),
            ('delivery_recorded_date', s.delivery_recorded_date)
    ) AS v(column_name, source_value)
),
parsed AS (
    SELECT
        column_name,
        source_value,
        CASE
            WHEN source_value ~ '^\d{1,2}-[A-Za-z]{3}-\d{2}$'
             AND UPPER(SPLIT_PART(source_value, '-', 2)) IN (
                 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'
             )
            THEN TO_DATE(source_value, 'DD-Mon-YY')
            ELSE NULL
        END AS parsed_date
    FROM date_values
)
SELECT
    column_name,
    COUNT(*) AS total_records,
    COUNT(parsed_date) AS parsed_records,
    COUNT(*) FILTER (
        WHERE parsed_date IS NULL
    ) AS excluded_or_unparsed,
    COUNT(*) FILTER (
        WHERE parsed_date IS NOT NULL
          AND UPPER(TO_CHAR(parsed_date, 'FMDD-Mon-YY'))
              = UPPER(source_value)
    ) AS roundtrip_matches,
    COUNT(*) FILTER (
        WHERE parsed_date IS NOT NULL
          AND UPPER(TO_CHAR(parsed_date, 'FMDD-Mon-YY'))
              <> UPPER(source_value)
    ) AS roundtrip_mismatches
FROM parsed
GROUP BY column_name
ORDER BY column_name;

-- DQ-02 — Date Format Validation: Results

-- **Objective:** Validate the consistency and parseability of the three shipment date fields stored in `DD-Mon-YY` format.

-- **Results**

-- | Date field | Records | Parsed | Round-trip matches | Mismatches |
-- |---|---:|---:|---:|---:|
-- | Scheduled delivery date | 10,324 | 10,324 | 10,324 | 0 |
-- | Delivered to client date | 10,324 | 10,324 | 10,324 | 0 |
-- | Delivery recorded date | 10,324 | 10,324 | 10,324 | 0 |
-- | **Total** | **30,972** | **30,972** | **30,972** | **0** |

-- **Conclusion:** All three fields consistently matched the expected source format after parsing and reformatting. No values were excluded by the corrected validation query.

-- **Limitation:** PostgreSQL's `TO_DATE` can normalize certain invalid calendar dates. Therefore, this test does not independently establish strict calendar validity or the logical consistency of shipment dates.

-- **Data handling:** The raw source table remains unchanged.

-- QUERY: DQ-02 — Shipment Date Chronology Check.

WITH parsed_dates AS (
    SELECT
        id,
        TO_DATE(scheduled_delivery_date, 'DD-Mon-YY')
            AS scheduled_date,
        TO_DATE(delivered_to_client_date, 'DD-Mon-YY')
            AS delivered_date,
        TO_DATE(delivery_recorded_date, 'DD-Mon-YY')
            AS recorded_date
    FROM raw.scms_shipments
)
SELECT
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE delivered_date < scheduled_date
    ) AS delivered_before_scheduled,

    COUNT(*) FILTER (
        WHERE delivered_date = scheduled_date
    ) AS delivered_on_scheduled_date,

    COUNT(*) FILTER (
        WHERE delivered_date > scheduled_date
    ) AS delivered_after_scheduled,

    COUNT(*) FILTER (
        WHERE recorded_date < delivered_date
    ) AS recorded_before_delivery,

    COUNT(*) FILTER (
        WHERE recorded_date = delivered_date
    ) AS recorded_on_delivery_date,

    COUNT(*) FILTER (
        WHERE recorded_date > delivered_date
    ) AS recorded_after_delivery

FROM parsed_dates;

-- QUERY: DQ-02 — Early Delivery Recording Review

SELECT
    id,
    country,
    vendor,
    shipment_mode,
    scheduled_delivery_date,
    delivered_to_client_date,
    delivery_recorded_date,
    product_group,
    line_item_quantity
FROM raw.scms_shipments
WHERE TO_DATE(delivery_recorded_date, 'DD-Mon-YY')
    < TO_DATE(delivered_to_client_date, 'DD-Mon-YY')
ORDER BY id;

-- DQ-02 — Delivery Date Chronology Review

-- **Test:** Compared scheduled delivery, delivered-to-client, and delivery-recorded dates.

-- **Results:**
-- - Delivered before scheduled date: 2,814 (27.26%)
-- - Delivered on scheduled date: 6,324 (61.25%)
-- - Delivered after scheduled date: 1,186 (11.49%)
-- - Delivery recorded before delivered-to-client date: 3 (0.03%)
-- - Delivery recorded on the same date: 8,413 (81.49%)
-- - Delivery recorded after the delivery date: 1,908 (18.48%)

-- **Exception review:** IDs 29140 and 57447 (Vietnam) and 72832 (Cameroon) have delivery-recorded dates one day earlier than their delivered-to-client dates.

-- **Interpretation:** These three records warrant source-level verification. Early delivery and delayed recording are not automatically errors. The meaning of each date field must be confirmed before classifying any record as incorrect.

-- **Limitation:** This analysis identifies date relationships; it does not establish the actual delivery date or the source system's recording rules.

-- **Data handling:** No source values were modified.

-- QUERY: DQ-01 — Missing Dosage Item Description Review.

SELECT
    product_group,
    sub_classification,
    item_description,
    COUNT(*) AS affected_records,
    COUNT(DISTINCT vendor) AS distinct_vendors
FROM raw.scms_shipments
WHERE NULLIF(BTRIM(dosage), '') IS NULL
GROUP BY
    product_group,
    sub_classification,
    item_description
ORDER BY
    affected_records DESC,
    product_group,
    sub_classification,
    item_description
LIMIT 40;

-- QUERY: DQ-01 — Dosage Consistency by Item Description

WITH item_dosage AS (
    SELECT
        item_description,
        product_group,
        sub_classification,
        COUNT(*) AS total_records,
        COUNT(*) FILTER (
            WHERE NULLIF(BTRIM(dosage), '') IS NULL
        ) AS missing_dosage_records,
        COUNT(*) FILTER (
            WHERE NULLIF(BTRIM(dosage), '') IS NOT NULL
        ) AS populated_dosage_records,
        COUNT(DISTINCT NULLIF(BTRIM(dosage), ''))
            AS distinct_populated_dosages
    FROM raw.scms_shipments
    GROUP BY
        item_description,
        product_group,
        sub_classification
)
SELECT
    product_group,
    sub_classification,
    item_description,
    total_records,
    missing_dosage_records,
    populated_dosage_records,
    distinct_populated_dosages
FROM item_dosage
WHERE missing_dosage_records > 0
ORDER BY
    populated_dosage_records DESC,
    missing_dosage_records DESC,
    item_description
LIMIT 40;

-- 03 — DQ-06 and DQ-07: Weight/Freight Reference Validation

-- Compare SQL results against verified Python findings and document discrepancies.

-- QUERY: DQ-06/07 — Reference Record Consistency Review

WITH reference_records AS (
    SELECT
        id AS referring_id,
        weight_kilograms,
        freight_cost_usd,
        country,
        shipment_mode,
        vendor,
        fulfill_via,
        product_group,
        item_description,
        line_item_quantity,
        scheduled_delivery_date,
        delivered_to_client_date,
        SUBSTRING(
            weight_kilograms
            FROM 'ID#[: ]*([0-9]+)'
        ) AS weight_target_id,
        SUBSTRING(
            freight_cost_usd
            FROM 'ID#[: ]*([0-9]+)'
        ) AS freight_target_id
    FROM raw.scms_shipments
),
references_long AS (
    SELECT
        referring_id,
        'weight' AS reference_type,
        weight_target_id AS target_id
    FROM reference_records
    WHERE weight_target_id IS NOT NULL

    UNION ALL

    SELECT
        referring_id,
        'freight' AS reference_type,
        freight_target_id AS target_id
    FROM reference_records
    WHERE freight_target_id IS NOT NULL
),
comparison AS (
    SELECT
        r.reference_type,
        r.referring_id,
        r.target_id,
        src.country AS source_country,
        tgt.country AS target_country,
        src.shipment_mode AS source_shipment_mode,
        tgt.shipment_mode AS target_shipment_mode,
        src.vendor AS source_vendor,
        tgt.vendor AS target_vendor,
        src.fulfill_via AS source_fulfill_via,
        tgt.fulfill_via AS target_fulfill_via,
        src.product_group AS source_product_group,
        tgt.product_group AS target_product_group,
        src.item_description AS source_item_description,
        tgt.item_description AS target_item_description,
        src.line_item_quantity AS source_quantity,
        tgt.line_item_quantity AS target_quantity,
        src.scheduled_delivery_date AS source_scheduled_date,
        tgt.scheduled_delivery_date AS target_scheduled_date,
        src.delivered_to_client_date AS source_delivered_date,
        tgt.delivered_to_client_date AS target_delivered_date,
        tgt.weight_kilograms AS target_weight,
        tgt.freight_cost_usd AS target_freight
    FROM references_long AS r
    JOIN raw.scms_shipments AS src
      ON src.id = r.referring_id
    LEFT JOIN raw.scms_shipments AS tgt
      ON tgt.id = r.target_id
)
SELECT
    reference_type,
    COUNT(*) AS reference_occurrences,
    COUNT(*) FILTER (
        WHERE target_country IS NULL
    ) AS missing_targets,
    COUNT(*) FILTER (
        WHERE source_country IS DISTINCT FROM target_country
    ) AS country_differences,
    COUNT(*) FILTER (
        WHERE source_shipment_mode
              IS DISTINCT FROM target_shipment_mode
    ) AS shipment_mode_differences,
    COUNT(*) FILTER (
        WHERE source_vendor IS DISTINCT FROM target_vendor
    ) AS vendor_differences,
    COUNT(*) FILTER (
        WHERE source_fulfill_via IS DISTINCT FROM target_fulfill_via
    ) AS fulfilment_differences,
    COUNT(*) FILTER (
        WHERE source_product_group
              IS DISTINCT FROM target_product_group
    ) AS product_group_differences,
    COUNT(*) FILTER (
        WHERE source_item_description
              IS DISTINCT FROM target_item_description
    ) AS item_description_differences,
    COUNT(*) FILTER (
        WHERE source_quantity IS DISTINCT FROM target_quantity
    ) AS quantity_differences,
    COUNT(*) FILTER (
        WHERE source_scheduled_date
              IS DISTINCT FROM target_scheduled_date
    ) AS scheduled_date_differences,
    COUNT(*) FILTER (
        WHERE source_delivered_date
              IS DISTINCT FROM target_delivered_date
    ) AS delivered_date_differences
FROM comparison
GROUP BY reference_type
ORDER BY reference_type;

-- QUERY: DQ-06/07 — Weight and Freight Target Alignment

WITH extracted AS (
    SELECT
        id,
        SUBSTRING(
            weight_kilograms
            FROM 'ID#[: ]*([0-9]+)'
        ) AS weight_target_id,
        SUBSTRING(
            freight_cost_usd
            FROM 'ID#[: ]*([0-9]+)'
        ) AS freight_target_id
    FROM raw.scms_shipments
)
SELECT
    COUNT(*) FILTER (
        WHERE weight_target_id IS NOT NULL
          AND freight_target_id IS NOT NULL
    ) AS both_fields_reference_target,

    COUNT(*) FILTER (
        WHERE weight_target_id IS NOT NULL
          AND freight_target_id IS NOT NULL
          AND weight_target_id = freight_target_id
    ) AS same_target_id,

    COUNT(*) FILTER (
        WHERE weight_target_id IS NOT NULL
          AND freight_target_id IS NOT NULL
          AND weight_target_id <> freight_target_id
    ) AS different_target_ids,

    COUNT(*) FILTER (
        WHERE weight_target_id IS NOT NULL
          AND freight_target_id IS NULL
    ) AS weight_reference_only,

    COUNT(*) FILTER (
        WHERE weight_target_id IS NULL
          AND freight_target_id IS NOT NULL
    ) AS freight_reference_only

FROM extracted;

-- ------------------------------------------------------------------------

-- QUERY: DQ-06/07 — Scheduled-Date Differences in Linked Records

WITH reference_records AS (
    SELECT
        r.id AS referring_id,
        SUBSTRING(
            r.weight_kilograms
            FROM 'ID#[: ]*([0-9]+)'
        ) AS target_id
    FROM raw.scms_shipments AS r
    WHERE r.weight_kilograms LIKE 'See %'
      AND r.freight_cost_usd LIKE 'See %'
)
SELECT
    x.referring_id,
    x.target_id,
    r.po_so_number AS referring_po_so,
    t.po_so_number AS target_po_so,
    r.asn_dn_number AS referring_asn_dn,
    t.asn_dn_number AS target_asn_dn,
    r.product_group AS referring_product_group,
    t.product_group AS target_product_group,
    r.item_description AS referring_item,
    t.item_description AS target_item,
    r.line_item_quantity AS referring_quantity,
    t.line_item_quantity AS target_quantity,
    r.scheduled_delivery_date AS referring_scheduled_date,
    t.scheduled_delivery_date AS target_scheduled_date
FROM reference_records AS x
JOIN raw.scms_shipments AS r
    ON r.id = x.referring_id
JOIN raw.scms_shipments AS t
    ON t.id = x.target_id
WHERE r.scheduled_delivery_date
      IS DISTINCT FROM t.scheduled_delivery_date
ORDER BY x.referring_id;

-- ------------------------------------------------------------------------

WITH reference_records AS (
    SELECT
        r.id AS referring_id,
        SUBSTRING(
            r.weight_kilograms
            FROM 'ID#[: ]*([0-9]+)'
        ) AS target_id,
        SUBSTRING(
            r.weight_kilograms
            FROM 'See ([^ (]+)'
        ) AS weight_reference_document,
        SUBSTRING(
            r.freight_cost_usd
            FROM 'See ([^ (]+)'
        ) AS freight_reference_document
    FROM raw.scms_shipments r
    WHERE r.weight_kilograms LIKE 'See %'
      AND r.freight_cost_usd LIKE 'See %'
),
validated AS (
    SELECT
        x.*,
        t.asn_dn_number AS target_asn_dn
    FROM reference_records x
    JOIN raw.scms_shipments t
        ON t.id = x.target_id
)
SELECT
    COUNT(*) AS reference_records,
    COUNT(*) FILTER (
        WHERE weight_reference_document = target_asn_dn
    ) AS weight_document_matches,
    COUNT(*) FILTER (
        WHERE freight_reference_document = target_asn_dn
    ) AS freight_document_matches,
    COUNT(*) FILTER (
        WHERE weight_reference_document IS DISTINCT FROM target_asn_dn
    ) AS weight_document_mismatches,
    COUNT(*) FILTER (
        WHERE freight_reference_document IS DISTINCT FROM target_asn_dn
    ) AS freight_document_mismatches
FROM validated;

-- DQ-06 / DQ-07 — Cross-Record Reference Integrity

-- **Scope:** 2,445 records containing cross-record references in both `weight_kilograms` and `freight_cost_usd`.

-- **Validated results**
-- - All 2,445 references resolve to existing target records.
-- - Weight and freight references point to the same target ID in all 2,445 cases.
-- - Both reference document numbers match the target record's `asn_dn_number` in all 2,445 cases.
-- - No target-ID, document-number, or cross-field target-alignment mismatches were identified.
-- - In seven examined cases, referring and target records shared PO/SO numbers, ASN/DN numbers, product groups, and delivered dates, but differed in item description, quantity, and scheduled delivery date.

-- **Interpretation:** Reference linkage is internally consistent in the checks performed. The nonnumeric values appear to encode cross-record references rather than arbitrary text. However, the intended business rules for weight and freight allocation remain unverified.

-- **Limitation:** Consistent references do not prove that the referenced values should be inherited, copied, or summed. No automatic replacements or financial adjustments are justified by these results alone.

-- **Status:** Target-linkage and document-number validation completed; operational meaning and allocation rules remain unconfirmed.

-- 04 — DQ-08: Insurance and Shipment-Mode Completeness
--
-- SQL investigation of missing insurance, missing shipment mode, and their overlap.

-- QUERY: DQ-08 — Insurance and Shipment-Mode Overlap.

SELECT
    COUNT(*) FILTER (
        WHERE line_item_insurance_usd IS NULL
    ) AS missing_insurance,

    COUNT(*) FILTER (
        WHERE shipment_mode IS NULL
    ) AS missing_shipment_mode,

    COUNT(*) FILTER (
        WHERE line_item_insurance_usd IS NULL
          AND shipment_mode IS NULL
    ) AS missing_both,

    COUNT(*) FILTER (
        WHERE line_item_insurance_usd IS NULL
          AND shipment_mode IS NOT NULL
    ) AS insurance_missing_only,

    COUNT(*) FILTER (
        WHERE shipment_mode IS NULL
          AND line_item_insurance_usd IS NOT NULL
    ) AS shipment_mode_missing_only

FROM raw.scms_shipments;

-- ------------------------------------------------------------------------

SELECT
    COALESCE(
        NULLIF(BTRIM(shipment_mode), ''),
        '[MISSING]'
    ) AS shipment_mode_group,

    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE line_item_insurance_usd IS NULL
    ) AS missing_insurance,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE line_item_insurance_usd IS NULL
        ) / COUNT(*),
        2
    ) AS missing_insurance_pct

FROM raw.scms_shipments

GROUP BY 1
ORDER BY missing_insurance DESC, total_records DESC;

-- DQ-08 — Insurance Missingness by Shipment Mode

-- **SQL/Python cross-validation:** Passed.

-- | Shipment mode | Records | Missing insurance | Missing rate |
-- |---|---:|---:|---:|
-- | Air | 6,113 | 181 | 2.96% |
-- | Missing | 360 | 106 | 29.44% |
-- | Truck | 2,830 | 0 | 0.00% |
-- | Air Charter | 650 | 0 | 0.00% |
-- | Ocean | 371 | 0 | 0.00% |

-- **Finding:** Missing insurance is disproportionately represented among records where shipment mode is also missing. Of the 360 records missing shipment mode, 106 also lack insurance.

-- **Recommended action:** Prioritize review of the 106 records missing both fields, followed by the remaining records with missing shipment mode.

-- **Limitations:** The cause of missingness, insurance applicability, and financial impact are unconfirmed. No values should be imputed without source documentation.

-- **Data handling:** Raw records remain unchanged.

-- 05 — Final Findings & Recommendations

-- Validated metrics, evidence limitations, business implications, and recommended actions.

-- -- ============================================================
-- -- 05 — FINAL FINDINGS & RECOMMENDATIONS
-- -- SCMS Shipment Data Quality Investigation
-- -- ============================================================
-- --
-- -- Purpose:
-- -- Consolidate the validated findings from DQ-01 through DQ-08.
-- --
-- -- Important:
-- -- This is a curated reporting layer based on the completed
-- -- investigations. It does not independently recalculate every
-- -- metric from the raw table.
-- --
-- -- Raw source data remains unchanged.
-- -- ============================================================

WITH final_findings AS (

    SELECT *
    FROM (
        VALUES

        (
            'DQ-01',
            'P2',
            'Missing dosage values',
            '1,736 of 10,324 records (16.82%) have missing dosage. '
            || 'Missingness occurs in all 1,728 HRDT records and all '
            || '8 MRDT records. ARV has no missing dosage values.',
            'Dosage-related analyses may be incomplete for affected '
            || 'diagnostic products.',
            'Product-specific dosage requirements and downstream '
            || 'impact have not been confirmed.',
            'Verify dosage applicability against authoritative product '
            || 'specifications. Investigate the eight affected malaria '
            || 'records before deciding whether remediation is required.',
            'Missingness pattern validated; business requirement unconfirmed.'
),

(
'DQ-02',
'P1',
'Date fields contain workflow labels and chronology exceptions',
'PQ date: 7,643 date-format candidates, 2,476 Pre-PQ Process '
|| 'labels and 205 Date Not Captured labels. PO date: 4,592 '
|| 'date-format candidates, 5,404 N/A - From RDC labels and '
|| '328 Date Not Captured labels. Three records have a '
|| 'recording date earlier than the delivered-to-client date.',
'Treating workflow labels as dates or interpreting date fields '
|| 'without their business definitions could distort timing '
|| 'and delivery-performance reporting.',
'Date-format and round-trip checks passed for the three '
|| 'shipment date fields. These checks do not independently '
|| 'prove strict calendar validity or explain the business '
|| 'meaning of every date field and workflow label.',
'Confirm date-field definitions and workflow labels with the '
|| 'source owner. Verify the three chronology exceptions '
|| 'before classifying them as errors.',
'Selected counts and date relationships validated; semantics '
|| 'remain unconfirmed.'
),

(
'DQ-03',
'P3',
'Pack-price and unit-price arithmetic differences',
'The initial unit-price arithmetic test flagged 7,774 of 10,324 '
|| 'records at a tolerance above $0.02 when comparing pack price '
|| 'with unit price multiplied by UOM. A separate reverse-calculation '
|| 'test found that the recorded unit price matched pack price divided '
|| 'by UOM, rounded to two decimals, for all 10,324 records. '
|| 'Rounding unit price multiplied by UOM did not resolve the original '
|| 'differences: 90 of the original 7,774 flagged records fell within '
|| '$0.02 after rounding unit price multiplied by UOM; 7,684 remained '
|| 'outside the tolerance. '
|| 'Separately, 549 line-item values differed from quantity multiplied '
|| 'by pack price by more than $0.02; all 549 passed the implied-price '
|| 'rounding test.',
'Price arithmetic differences may affect interpretation of unit '
|| 'prices, pack prices and line-item values in downstream analysis.',
'The recorded reverse-calculation relationship is consistent across '
|| 'the dataset, but the authoritative pricing convention has not '
|| 'been confirmed. The remaining arithmetic differences do not, '
|| 'by themselves, establish financial loss or incorrect pricing.',
'Confirm the intended pricing formula and rounding convention '
|| 'with source documentation. Keep the unit-price/UOM test separate '
|| 'from the quantity/pack-price line-value test.',
'Pricing relationships and separate rounding tests validated; '
|| 'authoritative pricing rules remain unconfirmed.'
),

(
'DQ-04',
'P2',
'Zero unit prices require contextual review',
'103 records have unit_price = 0. Of these, 85 have positive '
|| 'pack prices and 86 have positive line-item values. '
|| 'A recurring HIV safety-lancet product pattern accounts '
|| 'for 58 zero-unit-price records.',
'Price-based analysis may be misleading if zero unit prices '
|| 'are interpreted without understanding the applicable '
|| 'pricing convention.',
'The reason for the observed price scales and zero values '
|| 'has not been confirmed. No financial loss or pricing '
|| 'error has been established.',
'Check source pricing rules and product documentation. '
|| 'Do not automatically replace zero values or recalculate '
|| 'prices without authoritative evidence.',
'Zero-price pattern validated; business meaning unconfirmed.'
),

(
'DQ-05',
'P2',
'Potential duplicate shipment records',
'Four candidate pairs involving eight records match across '
|| 'all 32 non-ID fields.',
'If any candidates are accidental duplicates, record counts '
|| 'and aggregate metrics could be overstated. This impact '
|| 'has not been established.',
'Identical non-ID attributes do not prove that two records '
|| 'represent the same shipment or an accidental duplicate.',
'Verify all four pairs against shipment documents or source '
|| 'system records. Deduplicate only after confirmation.',
'Four candidate pairs reproduced; duplicate status unconfirmed.'
),

(
'DQ-06',
'P1',
'Weight and freight fields mix numbers and explanatory text',
'Weight: 6,372 numeric records (61.72%), 2,445 cross-record '
|| 'references (23.68%) and 1,507 other explanatory-text '
|| 'records (14.60%). Freight: 6,198 numeric records (60.03%), '
|| '2,445 cross-record references (23.68%) and 1,681 other '
|| 'explanatory-text records (16.28%). Neither field has '
|| 'blank values in the classification results.',
'Direct numeric aggregation may omit or misinterpret records '
|| 'whose values are represented by references or explanatory '
|| 'text.',
'Reference links were validated with DQ-07, but the intended '
|| 'weight and freight allocation rules remain unconfirmed. '
|| 'The same underlying reference population must not be '
|| 'counted as a separate issue twice.',
'Confirm how referenced values should be interpreted with '
|| 'the source owner. Do not copy, impute, or sum target '
|| 'values without documented rules.',
'Value classifications validated. DQ-07 linkage checks cover the same '
|| '2,445 records; operational meaning remains unconfirmed.'
),

(
'DQ-07',
'P2',
'Cross-record references in weight and freight',
'There are 2,445 records containing references in both fields '
|| '(the same underlying records classified in DQ-06), '
|| 'representing 4,890 field-level reference occurrences. '
|| 'Both fields point to the same target ID in every case. '
|| 'Target document numbers matched in all tested references.',
'The references appear internally consistent, but their '
|| 'meaning must be understood before values can be used '
|| 'for shipment-level calculations.',
'Linkage consistency does not establish whether referenced '
|| 'values are shared, inherited, allocated, or otherwise '
|| 'intended to be used.',
'Resolve the operational meaning jointly with DQ-06. '
|| 'Confirm the source-system convention before transforming '
|| 'referenced values.',
'Tested reference integrity validated; semantics unresolved. '
|| 'Assess jointly with DQ-06 to avoid double-counting.'
),

(
'DQ-08',
'P2',
'Missing insurance values and shipment-mode overlap',
'Insurance is missing in 287 of 10,324 records (2.78%). '
|| 'Shipment mode is missing in 360 records. Both fields '
|| 'are missing in 106 records; 181 records have missing '
|| 'insurance while shipment mode is present.',
'Incomplete insurance and shipment information may limit '
|| 'insurance-related analysis and interpretation of '
|| 'shipment costs.',
'Insurance applicability, cause of missingness and financial '
|| 'impact have not been confirmed.',
'Review the 106 records missing both fields first. Confirm '
|| 'insurance requirements and shipment-mode rules before '
|| 'imputing or reclassifying any values.',
'Missingness counts and descriptive patterns validated; '
|| 'business impact unconfirmed.'
)

) AS v (
finding_id,
investigation_priority,
finding,
validated_evidence,
potential_business_implication,
evidence_limitation,
recommended_action,
validation_status
)
)

SELECT
    finding_id,
    investigation_priority,
    finding,
    validated_evidence,
    potential_business_implication,
    evidence_limitation,
    recommended_action,
    validation_status
FROM final_findings

ORDER BY
    CASE investigation_priority
        WHEN 'P1' THEN 1
        WHEN 'P2' THEN 2
        WHEN 'P3' THEN 3
        ELSE 4
    END,
    finding_id;

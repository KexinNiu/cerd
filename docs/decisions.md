# CERD decision log

## 2026-08-26 — Record schema v1 (task 01)

**Status: PENDING team sign-off** — post the field list below in the group
chat; curators confirm every field is checkable against a paper. Record
names + date here when agreed, then task 03 may start.

Field list (see `schema/record_schema.py` / `schema/record_schema.json`):

- Identity: `record_id`, `organism` (NCBI name), `taxid`, `strain` (verbatim)
- Condition: `condition` (UV | temperature)
  - UV: `uv_band` (UV-A/B/C), `dose_value` (>= 0), `dose_unit`
  - Temperature: `temp_c`, `temp_shift` (heat_shock | cold_shock | constant)
- Context: `exposure_time_s`, `medium`, `growth_phase`
- Measurement: `assay` (CFU | OD | spot_assay | survival_curve | microscopy |
  other), `response_type` (survival | growth_rate | growth_inhibition |
  recovery_time | expression_change | morphology | other), `response_value`,
  `response_unit`, `response_direction` (increase | decrease | none)
- Interpretation: `mechanism_reported` (list), `evidence_level`
  (measured | inferred | speculated)
- Provenance: `source_doi` and/or `source_pmid` (at least one required),
  `source_quote` (max 300 chars, verification only)
- QC: `extracted_by`, `verified_by`, `verified_date`, `notes`

Validation rules: dose >= 0; percent responses within [0, 100] (fold_change
exempt); DOI/PMID format checks; UV and temperature parameter fields are
mutually exclusive; unknown fields rejected.

Sign-off:

| Curator | Organism | Date | OK? |
|---------|----------|------|-----|
|         | E. coli  |      |     |
|         | B. subtilis |   |     |
|         | S. cerevisiae | |     |
|         | C. elegans |    |     |

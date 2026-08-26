# Task 01 — Finalize the record schema

## Goal
`schema/record_schema.py` compiles, validates the two hand-made example
records, and the team has signed off on the field list.

## Prompt for Claude Code session

Read CLAUDE.md and schema/record_schema.py (a draft already exists).

1. Review the draft pydantic schema. Check it covers: organism (name +
   taxid + strain), condition (enum: UV, temperature), condition parameters
   (dose_value/dose_unit for UV; temp_c + shift type for temperature),
   exposure_time_s, medium, growth_phase, assay (enum: CFU, OD, spot_assay,
   survival_curve, microscopy, other), response_type (enum: survival,
   growth_rate, growth_inhibition, recovery_time, expression_change,
   morphology, other), response_value, response_unit, response_direction,
   mechanism_reported (list), evidence_level (measured | inferred |
   speculated), source_doi, source_pmid, source_quote (max 300 chars,
   enforce), extracted_by, verified_by, verified_date, notes.
2. Write validators: dose_value >= 0; percent responses in [0, 100] unless
   response_unit is "fold_change"; source_quote length cap; DOI regex;
   at least one of source_doi/source_pmid present.
3. Create `schema/examples/` with 2 hand-written example records (one
   E. coli UV survival, one S. cerevisiae heat shock) that validate.
4. Write `pytest` tests: valid examples pass, 5 deliberately broken records
   fail with the right error.
5. Generate `schema/record_schema.json` (JSON Schema export) — the frontend
   and the extraction prompt both reference it.

## Team checkpoint
Post the field list in the group chat for sign-off before task 03 starts.
Curators must agree the fields are checkable against a paper.

## Done when
Tests pass; JSON schema exported; team sign-off recorded in docs/decisions.md.

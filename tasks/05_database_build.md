# Task 05 — Unit normalization & database build

## Goal
One command turns verified records into the release dataset the frontend
consumes.

## Prompt for Claude Code session

Read CLAUDE.md. Build:

1. `pipeline/normalize.py` — pure functions with pytest tests:
   - UV dose: mJ/cm² → J/m² (×10), µW/cm²×seconds → J/m², W/m²×s → J/m²
   - temperature: keep °C; K and °F converted
   - time: min/h → seconds
   - survival: fraction → percent; log10 reduction ↔ percent where stated
   Every conversion appends to a `normalization_applied` list on the record
   — provenance, never silent mutation. Ambiguous units → flag, don't guess.
2. `pipeline/build_release.py`:
   - Collect all records with verified_by != null.
   - Apply normalization; re-validate.
   - Emit `data/records/release/cerd_v<semver>.json` (one array) +
     per-organism CSVs + `stats.json` (counts per cell, papers per cell,
     verification coverage).
   - Fail the build if any cell has < 3 papers (warn threshold, override
     flag exists) or any record is unverified.
3. GitHub Action: on PR touching data/records/, run schema validation +
   normalization tests. On tag, build release and attach artifacts.

## Done when
`python -m pipeline.build_release` produces the JSON, tests green, CI runs
on a test PR.

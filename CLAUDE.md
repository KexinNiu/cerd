# CERD — Comparative Environmental Response Database

iGEM software project. Literature-mined database comparing how model organisms
respond to environmental stress conditions, with an interactive comparison UI.

## Locked decisions (do not re-litigate without team approval)

- **Scope v1**: 3–4 organisms (E. coli, B. subtilis, S. cerevisiae, C. elegans)
  × 2 conditions (UV radiation, temperature). Full 16×5 matrix is future work.
- **Data = facts only**: structured records extracted from papers. NEVER store
  paper full text, PDFs, or long verbatim passages in the repo — copyright.
  `source_quote` field is capped at 1–2 sentences, used only for verification.
- **Visualization**: dose–response scatter (all data points, hover = strain/
  assay/DOI). No single-dose cross-species bar charts — pseudo-comparability.
  Final plot form decided after first real data batch.
- **QC**: every record is LLM-extracted, then human-verified by an organism
  curator. Extractor ≠ verifier. A record without `verified_by` is not
  released.
- **Database = this git repo** (JSON/CSV in `data/records/`). No server DB.
- **Frontend**: static React app, deployed to GitHub Pages. Data bundled as
  static JSON. No backend.
- **Licenses**: data CC-BY 4.0, code MIT.

## Repo layout

- `tasks/` — numbered task prompts. Work through them in order; each is a
  self-contained brief for a Claude Code/Cowork session.
- `schema/record_schema.py` — pydantic schema. Single source of truth for
  what a record looks like. Change here first, everywhere else follows.
- `prompts/extraction_prompt.md` — LLM extraction prompt template.
- `pipeline/` — Python scripts: PubMed search, full-text fetch (PMC OA only),
  extraction, validation, unit normalization.
- `data/papers/papers.csv` — screened paper list (metadata only, no PDFs).
- `data/records/` — extracted + verified records. The actual database.
- `frontend/` — React (Vite) app.
- `docs/` — methods documentation for the iGEM wiki.

## Conventions

- Python 3.11+, `uv` or `pip` with `requirements.txt`. Type hints everywhere.
- All records validate against `schema/record_schema.py` before commit.
- Units: UV dose in J/m², temperature in °C, time in seconds. Conversion
  helpers live in `pipeline/normalize.py` and have tests.
- Organism names: NCBI Taxonomy scientific name + taxid. Strain names verbatim
  from paper.
- Never fabricate DOIs, PMIDs, or data values. Missing = null.
- Legal full text only: PMC OA subset via API, or institution-subscribed PDFs
  kept OUTSIDE this repo (local only, gitignored).

## Team workflow

- Dry lab (this repo's owner): pipeline, schema, frontend, review tool.
- Wet lab teammates: organism curators. They verify records via the Streamlit
  review tool (`pipeline/review_app.py`, built in task 04).
- Community contribution = GitHub PRs against `data/records/`.

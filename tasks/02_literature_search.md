# Task 02 — Literature search & screening

## Goal
`data/papers/papers.csv` with 10–15 included papers per organism×condition
cell (8 cells max in v1), each with legal full-text access confirmed.

## Prompt for Claude Code session

Read CLAUDE.md. Build `pipeline/search_pubmed.py`:

1. Use Bio.Entrez (email from .env). For each organism×condition pair, run
   an esearch with a query template, e.g.:
   - `"Escherichia coli"[TIAB] AND (ultraviolet OR "UV radiation" OR
     "UV-C")[TIAB] AND (survival OR viability OR inactivation)[TIAB]`
   - temperature: `("heat shock" OR "cold shock" OR thermotolerance)[TIAB]`
   Cap at 200 results per query, fetch title/abstract/PMID/DOI/year/journal.
2. Check each PMID against the PMC OA subset (efetch / OA web service);
   record `oa_status` and `pmc_id`.
3. Output `data/papers/candidates_<organism>_<condition>.csv`.
4. Do NOT auto-screen. Screening is human work.

Then create `data/papers/SCREENING.md` — the inclusion criteria checklist:
- primary research (no reviews), quantitative dose/temperature reported,
  untreated control present, assay identifiable, strain named.
- target 10–15 papers per cell; prefer papers with dose gradients (≥3 doses)
  — one such paper is worth five single-dose papers.
- record include/exclude + reason in a `screened` column.

## Human step (not Claude's)
Team screens candidates in the CSVs. Papers not in PMC OA: check
institutional access; if no legal full text, exclude. Full-text PDFs from
subscriptions go in `local_pdfs/` (gitignored), named `<pmid>.pdf`.

## Done when
`papers.csv` merged (screened-in only), every row has full-text source
(pmc_id or local pdf), counts per cell reported.

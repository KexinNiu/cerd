# Task 03 — LLM extraction pipeline

## Goal
`pipeline/extract.py` turns one paper into N validated draft records.

## Prompt for Claude Code session

Read CLAUDE.md, schema/record_schema.py, prompts/extraction_prompt.md.

1. Build `pipeline/fetch_fulltext.py`: given a papers.csv row, return plain
   text — from PMC OA XML (parse with lxml, keep section headers, tables as
   TSV blocks) or from `local_pdfs/<pmid>.pdf` (pymupdf). Cache to
   `cache/fulltext/<pmid>.txt` (gitignored).
2. Build `pipeline/extract.py`:
   - Loads the extraction prompt template, injects the JSON schema and the
     two few-shot examples from schema/examples/.
   - Calls the Anthropic API (model from config; support `--endpoint` for a
     future local vLLM). Ask for a JSON array only.
   - Parse response, strip code fences, validate every record with pydantic.
     Valid → `data/records/drafts/<pmid>.json` with `verified_by: null`.
     Invalid → `data/records/rejected/<pmid>.json` + error log.
   - Idempotent: skip PMIDs already extracted unless `--force`.
3. Extraction rules (already in the prompt template — keep them enforced):
   - one record per (strain × dose/temp × response_type × timepoint)
   - treatment groups only; control defines the 100% baseline
   - source_quote = the exact sentence(s) supporting the values, ≤300 chars
   - null for anything not stated; never infer dose from figures' axis
     labels alone if numbers aren't readable
   - discussion-section claims → evidence_level: "speculated"
4. Run on the 2 pilot papers first, print a human-readable diff-style
   summary (paper → extracted records table) for eyeballing.
5. `--batch` mode with cost estimate printed before running all papers.

## Done when
Both pilot papers extract cleanly; batch mode works; a run log records
model, date, prompt version (git hash) per record.

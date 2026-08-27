# CERD handoff

State of the dry-lab work as of **2026-08-27**, written so the next session —
human or Claude Code — can pick up without re-deriving anything.

Read `CLAUDE.md` first for the locked decisions. This file is the *current
state*: what is done, what is blocked, and the traps that already cost time.

---

## Where each task stands

| # | Task | Status | Reality |
|---|------|--------|---------|
| 00 | Environment | **done** | venv (py 3.11), `requirements.txt`, `.env.example`. Repo private, pushed. |
| 01 | Schema | **code done, sign-off pending** | `schema/record_schema.py` frozen and tested. The curator sign-off table in `docs/decisions.md` is still empty. |
| 02 | Literature search | **machine part done, screening pending** | 8 candidate CSVs, 1531 papers. Nobody has filled the `screened` column. |
| 03 | Extraction pipeline | **NOT built** | The 175 records exist but were produced by ad-hoc subagents, not by a script. See "Debts". |
| 04 | Review tool | **done** | `make review`. Verified end-to-end. Calibration meeting not held. |
| 05 | Normalization + release | **partial** | `normalize.py` covers a subset; `build_release.py` does not exist. Blocked on verified records anyway. |
| 06 | Frontend | **done, on draft data** | Live at https://kexinniu.github.io/cerd/ |
| 07 | Docs / wiki | **partial** | `docs/methods.md` written. Licence files and wiki pages not done. |

## The one thing blocking everything

**0 of 175 records are curator-verified.** `build_release.py` is specified to
refuse unverified records, the frontend is therefore stuck on draft data, and
the wiki has no releasable dataset to describe.

The unblock is not code. It is: hold the calibration meeting (see
`CURATORS.md`), then have curators run `make review`.

## Commands

```bash
make review     # curator review tool  -> localhost:8501
make test       # 54 tests
make audit      # re-check every draft record independently
make bundle     # rebuild the JSON the frontend imports
make frontend   # vite dev server

.venv/bin/python -m pipeline.search_pubmed --retmax 200          # all 8 cells
.venv/bin/python -m pipeline.search_pubmed --cells ecoli_uv      # one cell
.venv/bin/python -m pipeline.fetch_fulltext PMC9392361           # cache full text
```

After changing records, run `make audit && make bundle` — the frontend reads
`frontend/src/data/cerd_draft.json`, which `build_bundle` regenerates.

## Traps already hit — do not rediscover these

**PubMed's default sort is newest-first.** The first search run returned 200
nanomaterial papers per cell and zero classic dose–response work. `search_pubmed.py`
now passes `sort="relevance"`. If you write another Entrez query, do the same.

**NCBI retired the `oa.fcgi` Open Access service.** It 404s. Open Access status
now comes from `esearch db=pmc ... AND "open access"[filter]`, which is also
batchable and ~100× faster.

**`IncompleteRead` is an `http.client.HTTPException`, not an `OSError`.** A
retry wrapper that catches `OSError` silently never fires and the whole run dies
mid-way. NCBI drops chunked responses often enough that this matters.

**Papers and extractors disagree about typography, not about claims.** JATS
flattening turns `mJ/cm²` into `mJ/cm 2`; extractors retype `°C` as `C`, `±` as
`+/-`, `×` as `x`, `µ` as `u`. A naive verbatim check reported 55 "fabricated"
quotes that were all real. `pipeline/textmatch.py` folds exactly this and keeps
digits exact. Use it; do not write a second copy.

**Flattened tables contain no sentence punctuation.** "±2 sentences of context"
around a table-derived quote swallows the entire table. `context_around` caps at
700 characters for this reason.

**Response units are wildly heterogeneous** — 18 families across the drafts.
Putting them on one y-axis flattens every percent value onto zero next to an
8000-fold change. The frontend has a measure selector so the axis is always one
unit; do not "simplify" it away.

**Four categorical colours barely fit.** Only two 4-hue combinations from the
reference ramp pass the all-pairs colourblind and normal-vision floors in *both*
themes; the app uses one of them (`frontend/src/lib/palette.ts`). Colour is tied
to organism identity and must not be reassigned when a filter changes the
series count.

**Plotly's full distribution is 1.5 MB gzipped.** `plotly.js-basic-dist-min`
covers scatter and is a third the size.

**GitHub Pages needs Source = "GitHub Actions"** in repo settings. With the
default "Deploy from a branch" the workflow builds fine and then fails at the
deploy step with an opaque 404.

**The review tool's E2E test writes to real records.** It stamped three fake
`verified_by` values into `data/records/drafts/` and they were committed by
mistake (reverted in `e72c5e9`). Run that test against a copy, or `git checkout
data/records/` immediately afterwards.

## Debts — known, deliberate, not yet paid

**Task 03 does not exist as code.** The 175 records were extracted by subagents
reading full text directly. They are schema-valid and every quote was verified
against the source, but **the process is not reproducible**, so it cannot be
written up as methods for the iGEM wiki. A real `pipeline/extract.py` with a
versioned prompt is still required. It needs `ANTHROPIC_API_KEY` in `.env`,
which is currently empty.

**`normalize.py` is a subset of the task 05 spec.** Missing: µW/cm²×s and
W/m²×s → J/m², K and °F → °C, min/h → seconds, and — most importantly — the
`normalization_applied` provenance list. The spec is explicit that conversion
must never be a silent mutation. Do this when building `build_release.py`.

**`Methods.tsx` duplicates `docs/methods.md` by hand.** Task 07 should render
the markdown file instead.

**The frontend has no tests.** Typecheck only.

**`data/records/bundle.json` is committed and generated.** It is regenerated by
`make bundle`; if it ever conflicts, regenerate rather than merge.

## Data facts worth knowing before planning

- 175 draft records, 24 open-access papers, 4 organisms × 2 conditions.
- Only 41 UV and 12 temperature records land on a dose→survival-% axis. The rest
  report lifespan in days, growth rate, expression change, and so on. That is a
  property of the literature, not an extraction failure.
- `C. elegans` has **no** UV survival-percentage records at all; its UV papers
  report lifespan.
- `data/records/drafts/` is the working set. Rejections go to
  `data/records/rejected/` as `{record, rejection}` pairs — the reason cannot
  live inside the record because the schema forbids extra fields.

## Human steps nobody can do for the team

1. **Schema sign-off** — fill the table in `docs/decisions.md`. Do it before
   curators start; the schema gets much harder to change once records are being
   reviewed against it.
2. **Calibration meeting** — the whole team reviews the same 20 records, writes
   the disagreements into `CURATORS.md` as rules.
3. **Screening** — fill the `screened` column in `data/papers/candidates_*.csv`.
4. **Decide whether the repo goes public.** The Pages site is already public
   even though the repo is private, and it currently serves unverified data
   behind a warning banner.

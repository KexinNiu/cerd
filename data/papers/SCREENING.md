# CERD paper screening checklist (task 02)

Screening is **human work**. Open your organism's
`candidates_<organism>_<condition>.csv`, read title + abstract, and fill the
`screened` and `screen_reason` columns. Do not delete rows.

## Include only if ALL of these hold

- [ ] Primary research article (no reviews, no methods-only papers)
- [ ] Quantitative dose (UV: J/m² or convertible) or temperature (°C) reported
- [ ] Untreated / permissive-condition control present
- [ ] Assay identifiable (CFU, OD, spot assay, survival curve, microscopy)
- [ ] Strain named (verbatim strain designation available)

## Priorities

- Target **10–15 included papers per organism×condition cell**.
- **Prefer dose gradients (≥3 doses/temperatures)** — one gradient paper is
  worth five single-dose papers for the dose–response plots.
- Prefer `oa_status = oa` (legal full text via PMC OA API, zero friction).

## `screened` column values

| Value | Meaning |
|-------|---------|
| `include` | passes all criteria, full text obtainable |
| `exclude` | fails a criterion — put which one in `screen_reason` |
| `maybe` | needs full-text look to decide — resolve before merge |

## Full-text access rule (copyright)

- `oa` → full text fetched automatically via PMC OA API (task 03).
- `pmc_not_oa` / `no_pmc` → check institutional access. If we have it,
  download the PDF **manually** to `local_pdfs/<pmid>.pdf` (gitignored,
  never committed). If no legal full text → `exclude`, reason `no_access`.

## Merge (dry lab does this after screening)

All `include` rows are merged into `data/papers/papers.csv`; every row must
have `pmcid` (OA) or a `local_pdfs/<pmid>.pdf`. Counts per cell get reported
in the task 02 closeout.

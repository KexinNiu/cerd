# CERD methods

This is the prose behind the numbers. The Methods tab in the app mirrors it;
task 07 replaces the hand-kept copy with this file rendered directly.

## Paper discovery

One PubMed query per organism × condition cell, e.g.

```
"Escherichia coli"[TIAB]
  AND (ultraviolet OR "UV radiation" OR "UV-C" OR "UV irradiation")[TIAB]
  AND (survival OR viability OR inactivation OR resistance)[TIAB]
  NOT Review[Publication Type]
```

Results are sorted by **relevance**, not date. This matters: PubMed's default
order is newest-first, which buries the classic dose–response literature under
recent applied work. Each query keeps the top 200 hits; the true hit counts run
from 131 (*C. elegans* UV) to 2729 (*E. coli* UV).

Every PMID is mapped to a PMCID and checked against the PMC Open Access subset
via `esearch db=pmc ... AND "open access"[filter]` — the old `oa.fcgi` web
service has been retired by NCBI.

## Screening

Human work, by the organism curators. Inclusion needs all of: primary research,
a quantitative dose or temperature, an untreated control, an identifiable assay,
and a named strain. Papers with a gradient of three or more levels are worth far
more than single-dose papers and are taken first.

## Extraction

PMC OA full text is fetched as JATS XML and flattened to plain text
(`pipeline/fetch_fulltext.py`); references and back matter are dropped, tables
kept. The text never enters the repository — the cache lives in a gitignored
directory.

Extraction rules (`prompts/extraction_prompt.md`), all binding:

1. One record per strain × level × response type × timepoint. A five-dose
   gradient is five records.
2. The untreated control is the baseline and is never emitted as a record.
3. Values must be readable from text or tables. A value that exists only as a
   point in a figure is recorded as `null` with the trend in `notes` — never
   estimated off an axis.
4. `source_quote` is the exact sentence stating the values, 300 characters max,
   mandatory on every record.
5. Anything not explicitly stated is `null`. Strain, medium and growth phase are
   never inferred from common practice.
6. Units are copied verbatim; conversion happens downstream.

## Automated checks

`pipeline/audit_drafts.py` re-checks every draft record independently of the
extractor:

- validates against `schema/record_schema.py`;
- confirms the PMID exists in the candidate list it came from and that the DOI
  matches that row;
- confirms `source_quote` appears verbatim in the cached full text.

The quote comparison folds typography before matching — Unicode superscripts,
`°`, `±`, `×`, `µ` and the various dashes — because extractors routinely retype
`42 °C` as `42 C` and `5.6 × 10⁻²` as `5.6 x 10-2`. Those are the same claim.
Numbers are not folded.

## Normalization

`pipeline/normalize.py`, with tests:

- UV dose to J/m²: `mJ/cm² × 10`, `kJ/m² × 1000`, `J/cm² × 10000`.
- **J/mL is never converted.** It is a volumetric in-flow dose; giving it an
  areal equivalent would invent a path length. Those records simply carry no
  normalized dose.
- Survival to percent of control: percent as-is, fractions × 100, log₁₀
  reduction as `100 × 10⁻ˣ`. Units that do not express survival (fold-change,
  days, OD₆₀₀, h⁻¹) return nothing rather than being coerced.

## Reading the chart

The y-axis is always **one** measure in **one** unit. Response units in this
literature are wildly heterogeneous — putting fold-change beside percent on a
shared axis flattens every small value onto zero and implies a comparison the
papers do not support. The measure selector exists to prevent that.

A dotted line joins points only when they share a paper, strain, assay and
response unit — the one case where a gradient is a real curve rather than an
artifact of grouping.

Marker shape encodes assay, so identity never rests on color alone.

Cross-organism comparison is **indicative, not quantitative**. Two organisms at
the same J/m² are not running the same experiment: assay, strain background,
growth phase, medium and repair capacity all differ.

## Quality control

Every record is LLM-extracted and then verified by an organism curator, and the
extractor is never the verifier. A record without `verified_by` is not released.
The current dataset is entirely unverified draft data.

## Licences

Data CC-BY 4.0. Code MIT. No paper full text, PDF, or long verbatim passage is
stored in this repository.

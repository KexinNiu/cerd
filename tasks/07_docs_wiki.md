# Task 07 — Methods docs, licensing, iGEM wiki content

## Goal
The methodology is the judges' main course. Written, versioned, reusable.

## Prompt for Claude Code / Cowork session

Read CLAUDE.md, SCREENING.md, CURATORS.md, the extraction prompt, and
normalize.py.

1. Write `docs/methods.md` covering, in this order:
   - problem: fragmented, non-comparable stress-response literature
   - inclusion/exclusion criteria (import from SCREENING.md)
   - extraction: LLM + prompt version + model, with the anti-hallucination
     rules; error modes found in pilot and how prompts were fixed
   - QC: curator workflow, extractor≠verifier, calibration session results,
     field-level accuracy from the audit (task 03/04 numbers)
   - normalization rules table with formulas
   - comparability statement: why dose–response scatter, why no cross-
     species bar chart, known limits (assay heterogeneity, strain effects)
   - versioning + how to contribute (PR workflow)
2. `LICENSE` (MIT for code) + `data/records/LICENSE` (CC-BY 4.0) +
   CITATION.cff.
3. `CONTRIBUTING.md`: how an external person adds records (fork → follow
   schema → PR → CI validates → curator reviews).
4. Draft the wiki Software page from methods.md — same content, judge-
   facing framing: emphasize reproducibility, honesty about limits, and
   that the pipeline generalizes beyond the v1 matrix.
5. Zenodo: deposit the release JSON + get a DOI (manual step; write the
   checklist).

## Done when
methods.md reviewed by one wet-lab teammate ("could you re-run this from
the doc alone?" — answer must be yes), licenses in place, wiki draft ready.

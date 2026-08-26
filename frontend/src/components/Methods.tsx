import type { BundleMeta } from "../types";

interface Props {
  meta: BundleMeta;
}

/**
 * Renders the method summary. Kept in sync with docs/methods.md by hand for
 * now; task 07 replaces this with the rendered markdown file.
 */
export function Methods({ meta }: Props) {
  return (
    <main className="prose">
      <h2>Methods</h2>

      <h3>Where the records come from</h3>
      <p>
        Candidate papers are found with a PubMed query per organism × condition
        cell, sorted by relevance and restricted to primary research. Only papers
        in the PMC Open Access subset are read automatically; anything else needs
        an institutional copy kept outside this repository.
      </p>

      <h3>Extraction</h3>
      <p>
        Full text is flattened from JATS XML and passed to a language model with
        the schema and a fixed rule set: one record per strain × level ×
        response × timepoint, never the untreated control, values only from text
        and tables — never estimated off a figure axis — and a verbatim quote of
        at most 300 characters for every record.
      </p>

      <h3>What is checked automatically</h3>
      <ul>
        <li>Every record validates against the pydantic schema.</li>
        <li>
          Each PMID and DOI is checked back against the candidate list it came
          from.
        </li>
        <li>
          Each quote must appear verbatim in the cached full text, compared with
          typography folded (superscripts, ±, ×, µ, dashes).
        </li>
      </ul>

      <h3>Units</h3>
      <p>
        UV dose is normalized to J/m² and temperature stays in °C. Volumetric
        doses (J/mL) have no areal equivalent and are never converted — those
        records simply do not appear on the dose axis. Response values are shown
        in the unit the paper used.
      </p>

      <h3>Why comparison is indicative only</h3>
      <p>
        Two organisms exposed to the same J/m² are not doing the same experiment:
        assay, strain background, growth phase, medium and repair capacity all
        differ. The scatter exists so the shapes of the responses can be looked
        at side by side, not so one number can be subtracted from another. Points
        joined by a dotted line come from a single paper, strain and assay — the
        only case where a gradient is a real curve.
      </p>

      <h3>Verification status</h3>
      <p>
        {meta.verified_count} of {meta.record_count} records have been signed off
        by an organism curator. Extraction and verification are always done by
        different parties; a record without a verifier is not released.
      </p>

      <h3>Licences</h3>
      <p>Data CC-BY 4.0. Code MIT. No paper full text is stored in this repository.</p>
    </main>
  );
}

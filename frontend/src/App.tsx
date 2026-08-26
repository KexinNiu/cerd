import { useMemo, useState } from "react";
import bundleJson from "./data/cerd_draft.json";
import type { Bundle, Condition, EvidenceLevel, Filters } from "./types";
import {
  applyFilters, distinctAssays, isPlottable, levelExtent, recordsForCondition,
} from "./lib/filters";
import { availableMeasures, findMeasure, SURVIVAL_MEASURE_ID } from "./lib/measures";
import { downloadCsv } from "./lib/csv";
import { OrganismPanel } from "./components/OrganismPanel";
import { ConditionPanel } from "./components/ConditionPanel";
import { ScatterPlot } from "./components/ScatterPlot";
import { EvidenceTable } from "./components/EvidenceTable";
import { Methods } from "./components/Methods";

const BUNDLE = bundleJson as unknown as Bundle;

const DEFAULT_EVIDENCE: EvidenceLevel[] = ["measured", "inferred"];

export function App() {
  const [page, setPage] = useState<"explore" | "methods">("explore");
  const [condition, setCondition] = useState<Condition>("UV");
  const [organisms, setOrganisms] = useState<string[]>(BUNDLE.meta.organisms);
  const [assays, setAssays] = useState<string[]>([]);
  const [evidenceLevels, setEvidenceLevels] = useState<EvidenceLevel[]>(DEFAULT_EVIDENCE);
  const [strainQuery, setStrainQuery] = useState("");
  const [range, setRange] = useState<[number, number] | null>(null);
  const [measureId, setMeasureId] = useState<string>(SURVIVAL_MEASURE_ID);
  const [yLog, setYLog] = useState(true);

  const conditionRecords = useMemo(
    () => recordsForCondition(BUNDLE.records, condition).filter(isPlottable),
    [condition],
  );
  const measures = useMemo(() => availableMeasures(conditionRecords), [conditionRecords]);
  const measure = findMeasure(measures, measureId);
  const measureRecords = useMemo(
    () => (measure ? conditionRecords.filter((r) => measure.valueOf(r) !== null) : []),
    [conditionRecords, measure],
  );
  const extent = useMemo(() => levelExtent(measureRecords), [measureRecords]);
  const activeRange = range ?? extent;

  const filters: Filters = {
    organisms, condition, measure: measureId, range: activeRange,
    assays, evidenceLevels, strainQuery,
  };
  const filtered = useMemo(
    () => applyFilters(conditionRecords, filters, measure),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [conditionRecords, organisms, measure, activeRange, assays, evidenceLevels, strainQuery],
  );

  const onConditionChange = (next: Condition) => {
    setCondition(next);
    setRange(null); // extents differ per condition; recompute from the data
    setMeasureId(SURVIVAL_MEASURE_ID);
  };

  const onMeasureChange = (next: string) => {
    setMeasureId(next);
    setRange(null); // a different measure exposes a different level span
  };

  const hiddenByLog = measure
    ? filtered.filter((r) => (measure.valueOf(r) ?? 0) <= 0).length
    : 0;

  const missing = organisms.filter(
    (o) => !measureRecords.some((r) => r.organism === o),
  );

  return (
    <div className="app">
      <header className="masthead">
        <div className="brand">
          <p className="eyebrow">iGEM · Comparative Environmental Response Database</p>
          <h1>How model organisms answer the same stress</h1>
        </div>
        <nav className="tabs" aria-label="Sections">
          <button
            type="button"
            className={page === "explore" ? "tab active" : "tab"}
            onClick={() => setPage("explore")}
          >
            Explore
          </button>
          <button
            type="button"
            className={page === "methods" ? "tab active" : "tab"}
            onClick={() => setPage("methods")}
          >
            Methods
          </button>
        </nav>
      </header>

      {BUNDLE.meta.status === "draft" && (
        <p className="banner" role="status">
          <b>Unverified draft data.</b> All {BUNDLE.meta.record_count} records were
          extracted by a language model and none has been signed off by an organism
          curator yet. Do not cite these values.
        </p>
      )}

      {page === "methods" ? (
        <Methods meta={BUNDLE.meta} />
      ) : (
        <main className="layout">
          <div className="controls">
            <OrganismPanel
              available={BUNDLE.meta.organisms}
              selected={organisms}
              onChange={setOrganisms}
              records={measureRecords}
            />
            <ConditionPanel
              condition={condition}
              onConditionChange={onConditionChange}
              extent={extent}
              range={activeRange}
              onRangeChange={setRange}
              assays={distinctAssays(measureRecords)}
              selectedAssays={assays}
              onAssaysChange={setAssays}
              evidenceLevels={evidenceLevels}
              onEvidenceChange={setEvidenceLevels}
              strainQuery={strainQuery}
              onStrainQueryChange={setStrainQuery}
              measures={measures}
              measureId={measure?.id ?? measureId}
              onMeasureChange={onMeasureChange}
              yLog={yLog}
              onYLogChange={setYLog}
            />
          </div>

          <section className="results" aria-labelledby="results-heading">
            <div className="results-head">
              <h2 id="results-heading">
                {filtered.length} record{filtered.length === 1 ? "" : "s"}
                <span className="of"> of {measureRecords.length} with this measure</span>
              </h2>
              <button
                type="button"
                className="download"
                disabled={filtered.length === 0}
                onClick={() =>
                  downloadCsv(filtered, `cerd_${condition}_${filtered.length}_records.csv`)
                }
              >
                Download CSV
              </button>
            </div>

            {missing.length > 0 && (
              <p className="note">
                No {condition === "UV" ? "UV" : "temperature"} records for{" "}
                {missing.map((o) => <i key={o} className="sci">{o}</i>)
                  .reduce<React.ReactNode[]>((acc, el, i) =>
                    i === 0 ? [el] : [...acc, ", ", el], [])}
                {" "}on this measure — those papers report a different quantity.
              </p>
            )}

            {yLog && hiddenByLog > 0 && (
              <p className="note">
                {hiddenByLog} record{hiddenByLog === 1 ? "" : "s"} at zero cannot sit on a
                logarithmic axis and {hiddenByLog === 1 ? "is" : "are"} not drawn — they stay
                in the table below.
              </p>
            )}

            {measure ? (
              <ScatterPlot records={filtered} condition={condition} measure={measure} yLog={yLog} />
            ) : (
              <p className="empty">No plottable measure for this condition.</p>
            )}

            <p className="caption">
              Cross-organism comparison is indicative, not quantitative — assays and
              strains differ. See Methods.
            </p>

            <EvidenceTable records={filtered} />
          </section>
        </main>
      )}

      <footer>
        <span>Data CC-BY 4.0 · Code MIT</span>
        <span>{BUNDLE.meta.paper_count} open-access papers</span>
        <a href="https://github.com/KexinNiu/cerd">Source</a>
      </footer>
    </div>
  );
}

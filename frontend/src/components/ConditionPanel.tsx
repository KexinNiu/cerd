import type { Condition, EvidenceLevel } from "../types";
import type { Measure } from "../lib/measures";

interface Props {
  condition: Condition;
  onConditionChange: (condition: Condition) => void;
  extent: [number, number];
  range: [number, number];
  onRangeChange: (range: [number, number]) => void;
  assays: string[];
  selectedAssays: string[];
  onAssaysChange: (assays: string[]) => void;
  evidenceLevels: EvidenceLevel[];
  onEvidenceChange: (levels: EvidenceLevel[]) => void;
  strainQuery: string;
  onStrainQueryChange: (query: string) => void;
  measures: Measure[];
  measureId: string;
  onMeasureChange: (id: string) => void;
  yLog: boolean;
  onYLogChange: (yLog: boolean) => void;
}

const ALL_EVIDENCE: EvidenceLevel[] = ["measured", "inferred", "speculated"];

export function ConditionPanel(props: Props) {
  const {
    condition, onConditionChange, extent, range, onRangeChange,
    assays, selectedAssays, onAssaysChange,
    evidenceLevels, onEvidenceChange, strainQuery, onStrainQueryChange,
    measures, measureId, onMeasureChange, yLog, onYLogChange,
  } = props;

  const unit = condition === "UV" ? "J/m²" : "°C";
  const step = condition === "UV" ? Math.max(1, (extent[1] - extent[0]) / 200) : 0.5;

  const toggle = <T,>(list: T[], value: T): T[] =>
    list.includes(value) ? list.filter((v) => v !== value) : [...list, value];

  return (
    <section className="panel" aria-labelledby="condition-heading">
      <h2 id="condition-heading" className="panel-title">Condition</h2>
      <div className="panel-body">
        <div className="segmented" role="radiogroup" aria-label="Stress condition">
          {(["UV", "temperature"] as Condition[]).map((c) => (
            <button
              key={c}
              type="button"
              role="radio"
              aria-checked={condition === c}
              className={condition === c ? "seg active" : "seg"}
              onClick={() => onConditionChange(c)}
            >
              {c === "UV" ? "UV" : "Temperature"}
            </button>
          ))}
        </div>

        <label className="field">
          <span>Response measure (y-axis)</span>
          <select value={measureId} onChange={(e) => onMeasureChange(e.target.value)}>
            {measures.map((m) => (
              <option key={m.id} value={m.id}>
                {m.label} — {m.unit} ({m.count})
              </option>
            ))}
          </select>
        </label>

        <label className="check">
          <input
            type="checkbox"
            checked={yLog}
            onChange={(e) => onYLogChange(e.target.checked)}
          />
          <span>Logarithmic y-axis</span>
        </label>

        <fieldset className="group">
          <legend>
            Range · {Math.round(range[0])}–{Math.round(range[1])} {unit}
          </legend>
          <label className="slider">
            <span>min</span>
            <input
              type="range"
              min={extent[0]}
              max={extent[1]}
              step={step}
              value={range[0]}
              onChange={(e) =>
                onRangeChange([Math.min(Number(e.target.value), range[1]), range[1]])
              }
            />
          </label>
          <label className="slider">
            <span>max</span>
            <input
              type="range"
              min={extent[0]}
              max={extent[1]}
              step={step}
              value={range[1]}
              onChange={(e) =>
                onRangeChange([range[0], Math.max(Number(e.target.value), range[0])])
              }
            />
          </label>
        </fieldset>

        <fieldset className="group">
          <legend>Assay</legend>
          {assays.map((assay) => (
            <label key={assay} className="check">
              <input
                type="checkbox"
                checked={selectedAssays.length === 0 || selectedAssays.includes(assay)}
                onChange={() => onAssaysChange(toggle(selectedAssays, assay))}
              />
              <span>{assay.replace(/_/g, " ")}</span>
            </label>
          ))}
        </fieldset>

        <fieldset className="group">
          <legend>Evidence level</legend>
          {ALL_EVIDENCE.map((level) => (
            <label key={level} className="check">
              <input
                type="checkbox"
                checked={evidenceLevels.includes(level)}
                onChange={() => onEvidenceChange(toggle(evidenceLevels, level))}
              />
              <span>{level}</span>
              {level === "speculated" && <span className="count">hidden by default</span>}
            </label>
          ))}
        </fieldset>

        <label className="field">
          <span>Strain contains</span>
          <input
            type="search"
            value={strainQuery}
            placeholder="e.g. MG1655"
            onChange={(e) => onStrainQueryChange(e.target.value)}
          />
        </label>
      </div>
    </section>
  );
}

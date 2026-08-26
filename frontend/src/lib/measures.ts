import type { CerdRecord } from "../types";

/**
 * A measure is one homogeneous y-axis. Mixing response units on a single axis
 * (fold-change next to percent) makes every small value collapse onto zero and
 * invites comparisons the data cannot support, so the axis is always one
 * measure and the selector decides which.
 */
export interface Measure {
  id: string;
  label: string;
  unit: string;
  /** Records this measure can plot. */
  count: number;
  valueOf: (record: CerdRecord) => number | null;
}

export const SURVIVAL_MEASURE_ID = "survival_pct";

function survivalValue(record: CerdRecord): number | null {
  return record.survival_pct;
}

/**
 * Survival first — it is the one measure normalized across papers
 * (percent, N/N0 and log reduction all fold into % of control). Everything
 * else is offered in the unit the papers used, one family at a time.
 */
export function availableMeasures(records: CerdRecord[]): Measure[] {
  const measures: Measure[] = [];

  const survivalCount = records.filter((r) => r.survival_pct !== null).length;
  if (survivalCount > 0) {
    measures.push({
      id: SURVIVAL_MEASURE_ID,
      label: "Survival",
      unit: "% of control",
      count: survivalCount,
      valueOf: survivalValue,
    });
  }

  const families = new Map<string, { type: string; unit: string; count: number }>();
  for (const r of records) {
    if (r.response_value === null || r.response_unit === null) continue;
    if (r.survival_pct !== null) continue; // already covered by the survival axis
    const id = `${r.response_type}|${r.response_unit}`;
    const seen = families.get(id);
    if (seen) seen.count += 1;
    else families.set(id, { type: r.response_type, unit: r.response_unit, count: 1 });
  }

  for (const [id, family] of families) {
    measures.push({
      id,
      label: family.type.replace(/_/g, " "),
      unit: family.unit,
      count: family.count,
      valueOf: (record) =>
        `${record.response_type}|${record.response_unit}` === id
          ? record.response_value
          : null,
    });
  }

  return measures.sort((a, b) => b.count - a.count);
}

export function findMeasure(measures: Measure[], id: string): Measure | null {
  return measures.find((m) => m.id === id) ?? measures[0] ?? null;
}

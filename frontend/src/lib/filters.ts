import type { CerdRecord, Condition, Filters } from "../types";
import type { Measure } from "./measures";

/** The x-axis value for a record: normalized UV dose, or temperature. */
export function levelOf(record: CerdRecord): number | null {
  return record.condition === "UV" ? record.dose_j_m2 : record.temp_c;
}

/** A record can be plotted only if both axes resolve to numbers. */
export function isPlottable(record: CerdRecord): boolean {
  return levelOf(record) !== null && record.response_value !== null;
}

export function recordsForCondition(
  records: CerdRecord[],
  condition: Condition,
): CerdRecord[] {
  return records.filter((r) => r.condition === condition);
}

export function levelExtent(records: CerdRecord[]): [number, number] {
  const levels = records
    .map(levelOf)
    .filter((v): v is number => v !== null);
  if (levels.length === 0) return [0, 1];
  return [Math.min(...levels), Math.max(...levels)];
}

export function distinctAssays(records: CerdRecord[]): string[] {
  return [...new Set(records.map((r) => r.assay))].sort();
}

export function applyFilters(
  records: CerdRecord[],
  filters: Filters,
  measure: Measure | null,
): CerdRecord[] {
  const query = filters.strainQuery.trim().toLowerCase();
  return records.filter((r) => {
    if (r.condition !== filters.condition) return false;
    if (!filters.organisms.includes(r.organism)) return false;
    if (!filters.evidenceLevels.includes(r.evidence_level)) return false;
    if (filters.assays.length > 0 && !filters.assays.includes(r.assay)) {
      return false;
    }
    const level = levelOf(r);
    if (level === null) return false;
    if (level < filters.range[0] || level > filters.range[1]) return false;
    if (query && !(r.strain ?? "").toLowerCase().includes(query)) return false;
    // A record belongs on the chart only if it can supply the chosen measure.
    if (measure && measure.valueOf(r) === null) return false;
    return true;
  });
}

/**
 * Group a condition's records into dose gradients: same paper, same strain,
 * same assay and same response unit. Only these may be joined by a line —
 * connecting anything else would imply a curve the papers do not support.
 */
export function doseGradients(records: CerdRecord[]): CerdRecord[][] {
  const groups = new Map<string, CerdRecord[]>();
  for (const r of records) {
    const key = [
      r.source_pmid ?? r.source_doi ?? "?",
      r.strain ?? "?",
      r.assay,
      r.response_type,
      r.response_unit ?? "?",
      r.notes ?? "",
    ].join("|");
    const bucket = groups.get(key);
    if (bucket) bucket.push(r);
    else groups.set(key, [r]);
  }
  return [...groups.values()]
    .map((g) =>
      [...g].sort((a, b) => (levelOf(a) ?? 0) - (levelOf(b) ?? 0)),
    )
    .filter((g) => g.length >= 2);
}

export function sourceUrl(record: CerdRecord): string | null {
  if (record.source_doi) return `https://doi.org/${record.source_doi}`;
  if (record.source_pmid) {
    return `https://pubmed.ncbi.nlm.nih.gov/${record.source_pmid}/`;
  }
  return null;
}

export function sourceLabel(record: CerdRecord): string {
  if (record.source_doi) return record.source_doi;
  if (record.source_pmid) return `PMID ${record.source_pmid}`;
  return "no identifier";
}

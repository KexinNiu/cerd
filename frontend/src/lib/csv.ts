import type { CerdRecord } from "../types";

const COLUMNS: (keyof CerdRecord)[] = [
  "record_id", "organism", "taxid", "strain", "condition", "uv_band",
  "dose_value", "dose_unit", "dose_j_m2", "temp_c", "temp_shift",
  "exposure_time_s", "medium", "growth_phase", "assay", "response_type",
  "response_value", "response_unit", "response_direction", "survival_pct",
  "evidence_level", "source_doi", "source_pmid", "source_quote",
  "verified_by", "notes",
];

function escapeCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  const text = Array.isArray(value) ? value.join("; ") : String(value);
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function toCsv(records: CerdRecord[]): string {
  const header = COLUMNS.join(",");
  const rows = records.map((r) =>
    COLUMNS.map((c) => escapeCell(r[c])).join(","),
  );
  return [header, ...rows].join("\n") + "\n";
}

export function downloadCsv(records: CerdRecord[], filename: string): void {
  const blob = new Blob([toCsv(records)], {
    type: "text/csv;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

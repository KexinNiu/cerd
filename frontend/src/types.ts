export type Condition = "UV" | "temperature";

export type EvidenceLevel = "measured" | "inferred" | "speculated";

export interface CerdRecord {
  record_id: string;
  organism: string;
  taxid: number;
  strain: string | null;
  condition: Condition;
  uv_band: string | null;
  dose_value: number | null;
  dose_unit: string | null;
  temp_c: number | null;
  temp_shift: string | null;
  exposure_time_s: number | null;
  medium: string | null;
  growth_phase: string | null;
  assay: string;
  response_type: string;
  response_value: number | null;
  response_unit: string | null;
  response_direction: string | null;
  mechanism_reported: string[];
  evidence_level: EvidenceLevel;
  source_doi: string | null;
  source_pmid: string | null;
  source_quote: string;
  verified_by: string | null;
  notes: string | null;
  /** Derived by pipeline/normalize.py; null when units are not convertible. */
  dose_j_m2: number | null;
  survival_pct: number | null;
}

export interface BundleMeta {
  record_count: number;
  verified_count: number;
  status: "draft" | "released";
  organisms: string[];
  paper_count: number;
  plottable_uv: number;
  plottable_temperature: number;
}

export interface Bundle {
  meta: BundleMeta;
  records: CerdRecord[];
}

export interface Filters {
  organisms: string[];
  condition: Condition;
  /** Which homogeneous response measure the y-axis shows. */
  measure: string;
  /** Inclusive [min, max] on dose (J/m2) or temperature (degC). */
  range: [number, number];
  assays: string[];
  evidenceLevels: EvidenceLevel[];
  strainQuery: string;
}

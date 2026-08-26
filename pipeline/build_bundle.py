"""Bundle draft records into a single JSON payload for the frontend.

Emits data/records/bundle.json and a copy at frontend/src/data/cerd_draft.json,
which the Vite app imports statically. Only fields the UI needs are kept.
source_quote is included because the task 06 hover card shows it; the schema
caps it at 300 characters, well inside fair quotation.

Usage:  python -m pipeline.build_bundle
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pipeline.normalize import survival_to_percent, uv_dose_to_j_per_m2
from pipeline.search_pubmed import REPO_ROOT

logger = logging.getLogger(__name__)

DRAFTS_DIR = REPO_ROOT / "data" / "records" / "drafts"
OUT_PATH = REPO_ROOT / "data" / "records" / "bundle.json"
# The Vite app imports this statically — no fetch, no backend.
FRONTEND_PATH = REPO_ROOT / "frontend" / "src" / "data" / "cerd_draft.json"

UI_FIELDS = (
    "record_id", "organism", "taxid", "strain", "condition", "uv_band",
    "dose_value", "dose_unit", "temp_c", "temp_shift", "exposure_time_s",
    "medium", "growth_phase", "assay", "response_type", "response_value",
    "response_unit", "response_direction", "mechanism_reported",
    "evidence_level", "source_doi", "source_pmid", "source_quote",
    "verified_by", "notes",
)


def build() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path in sorted(DRAFTS_DIR.glob("*.json")):
        for raw in json.loads(path.read_text()):
            rec = {k: raw.get(k) for k in UI_FIELDS}
            # Derived plotting fields — null whenever the source units are not
            # convertible, so the chart silently drops them instead of lying.
            rec["dose_j_m2"] = uv_dose_to_j_per_m2(
                raw.get("dose_value"), raw.get("dose_unit")
            )
            rec["survival_pct"] = (
                survival_to_percent(raw.get("response_value"), raw.get("response_unit"))
                if raw.get("response_type") == "survival"
                else None
            )
            records.append(rec)
    verified = sum(1 for r in records if r["verified_by"])
    plottable_uv = sum(
        1 for r in records
        if r["dose_j_m2"] is not None and r["survival_pct"] is not None
    )
    plottable_temp = sum(
        1 for r in records
        if r["condition"] == "temperature"
        and r["temp_c"] is not None and r["survival_pct"] is not None
    )
    return {
        "meta": {
            "record_count": len(records),
            "verified_count": verified,
            "status": "draft" if verified < len(records) else "released",
            "organisms": sorted({r["organism"] for r in records}),
            "paper_count": len({r["source_pmid"] for r in records}),
            "plottable_uv": plottable_uv,
            "plottable_temperature": plottable_temp,
        },
        "records": records,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    bundle = build()
    payload = json.dumps(bundle, indent=1, ensure_ascii=False) + "\n"
    OUT_PATH.write_text(payload)
    FRONTEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_PATH.write_text(payload)
    meta = bundle["meta"]
    logger.info(
        f"wrote {OUT_PATH}: {meta['record_count']} records, "
        f"{meta['paper_count']} papers, {meta['verified_count']} verified"
    )


if __name__ == "__main__":
    main()

"""Audit draft records against schema, source CSVs, and paper full text.

Independent check of extractor output — catches the failure modes that
schema validation cannot: fabricated identifiers and quotes that are not
actually in the paper.

Checks per record:
  1. validates against schema/record_schema.py
  2. pmid exists in a data/papers/candidates_*.csv row, and the doi on that
     row matches the record's source_doi
  3. source_quote appears verbatim in the cached PMC full text
  4. response_value appears in the quote (soft warning — dose and temperature
     are usually stated in Methods rather than in the quoted result sentence)

Quote comparison is delegated to pipeline.textmatch, which folds the
typography papers and extractors disagree about while keeping numbers exact.

Usage:  python -m pipeline.audit_drafts
"""
from __future__ import annotations

import csv
import json
import logging
import sys
from pathlib import Path

from pydantic import ValidationError

from pipeline.search_pubmed import REPO_ROOT
from pipeline.textmatch import fold_str
from schema.record_schema import Record

logger = logging.getLogger(__name__)

DRAFTS_DIR = REPO_ROOT / "data" / "records" / "drafts"
PAPERS_DIR = REPO_ROOT / "data" / "papers"
FULLTEXT_DIR = REPO_ROOT / "local_pdfs" / "fulltext"




def load_candidate_index() -> dict[str, dict[str, str]]:
    """pmid -> candidate CSV row."""
    index: dict[str, dict[str, str]] = {}
    for path in PAPERS_DIR.glob("candidates_*.csv"):
        for row in csv.DictReader(path.open()):
            index[row["pmid"]] = row
    return index


def load_fulltexts() -> dict[str, str]:
    """pmcid -> normalized full text."""
    if not FULLTEXT_DIR.exists():
        return {}
    return {
        p.stem: fold_str(p.read_text()) for p in FULLTEXT_DIR.glob("PMC*.txt")
    }


def audit() -> tuple[list[str], list[str]]:
    """Return (hard problems, soft warnings)."""
    candidates = load_candidate_index()
    fulltexts = load_fulltexts()
    problems: list[str] = []
    soft: list[str] = []
    total = 0

    for path in sorted(DRAFTS_DIR.glob("*.json")):
        try:
            records = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{path.name}: unreadable JSON — {e}")
            continue

        for raw in records:
            total += 1
            rid = raw.get("record_id", "<no id>")
            where = f"{path.name}:{rid}"

            try:
                rec = Record.model_validate(raw)
            except ValidationError as e:
                problems.append(f"{where}: schema — {e.errors()[0]['msg']}")
                continue

            row = candidates.get(rec.source_pmid or "")
            if rec.source_pmid and row is None:
                problems.append(f"{where}: pmid {rec.source_pmid} not in any candidates CSV")
            elif row and rec.source_doi and row["doi"] and rec.source_doi != row["doi"]:
                problems.append(
                    f"{where}: doi {rec.source_doi} != CSV doi {row['doi']}"
                )

            pmcid = row["pmcid"] if row else ""
            text = fulltexts.get(pmcid, "")
            if not text:
                problems.append(f"{where}: no cached full text for {pmcid or 'unknown pmcid'}")
                continue
            if fold_str(rec.source_quote) not in text:
                problems.append(f"{where}: source_quote not found verbatim in full text")
                continue

            if rec.response_value is not None:
                quote = rec.source_quote.replace(",", "")
                value = rec.response_value
                shown = {f"{value:g}", f"{value:.1f}", f"{value:.2f}", str(value)}
                if value >= 1000:  # 14900 may be written 1.49 x 10^4
                    shown.add(f"{value / 1000:g}")
                if 0 < value < 0.01:  # 0.000106 may be written 1.06 x 10^-4
                    shown.add(f"{value * 1e4:g}")
                    shown.add(f"{value * 1e6:g}")
                if not any(s in quote for s in shown):
                    soft.append(f"{where}: response_value={value:g} not visible in quote")

    logger.info(f"audited {total} records in {len(list(DRAFTS_DIR.glob('*.json')))} files")
    return problems, soft


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    problems, soft = audit()
    for p in problems:
        logger.error(p)
    for s in soft:
        logger.warning(s)
    logger.info(f"{len(problems)} hard problems, {len(soft)} soft warnings")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()

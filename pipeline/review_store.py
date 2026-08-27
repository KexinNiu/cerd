"""Persistence for the curator review tool.

Records live in per-paper JSON arrays under data/records/drafts/. Approving
sets verified_by/verified_date in place; rejecting moves the record out to
data/records/rejected/ wrapped with its reason, so the rejection metadata
never has to fit inside the (deliberately strict) record schema.

Every write is atomic — a curator closing the laptop mid-save must not be
able to truncate a records file.
"""
from __future__ import annotations

import csv
import json
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterator

from pipeline.search_pubmed import REPO_ROOT
from schema.record_schema import Record

logger = logging.getLogger(__name__)

DRAFTS_DIR = REPO_ROOT / "data" / "records" / "drafts"
REJECTED_DIR = REPO_ROOT / "data" / "records" / "rejected"
FULLTEXT_DIR = REPO_ROOT / "local_pdfs" / "fulltext"
PAPERS_DIR = REPO_ROOT / "data" / "papers"

REJECTION_REASONS: tuple[str, ...] = (
    "wrong value",
    "control-vs-treatment mixup",
    "wrong strain",
    "speculation marked as measured",
    "unit error",
    "other",
)


@dataclass(frozen=True)
class Progress:
    total: int
    verified: int

    @property
    def fraction(self) -> float:
        return self.verified / self.total if self.total else 0.0


def _atomic_write(path: Path, text: str) -> None:
    """Write via a temp file in the same directory, then rename over."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
        tmp.replace(path)
    except OSError:
        tmp.unlink(missing_ok=True)
        raise


def _dump(records: list[dict[str, Any]]) -> str:
    return json.dumps(records, indent=2, ensure_ascii=False) + "\n"


def iter_draft_files() -> Iterator[Path]:
    return iter(sorted(DRAFTS_DIR.glob("*.json")))


def load_records() -> list[dict[str, Any]]:
    """Every draft record, each tagged with the file it came from."""
    out: list[dict[str, Any]] = []
    for path in iter_draft_files():
        try:
            records = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            logger.error(f"{path.name}: unreadable JSON — {e}")
            continue
        for record in records:
            out.append({**record, "_file": path.name})
    return out


def progress_for(records: list[dict[str, Any]], organism: str | None) -> Progress:
    scope = [r for r in records if organism in (None, r.get("organism"))]
    return Progress(
        total=len(scope),
        verified=sum(1 for r in scope if r.get("verified_by")),
    )


def _rewrite_file(filename: str, mutate) -> None:
    """Apply `mutate(records) -> records` to one drafts file, atomically."""
    path = DRAFTS_DIR / filename
    records = json.loads(path.read_text())
    _atomic_write(path, _dump(mutate(records)))


def approve(record_id: str, filename: str, reviewer: str,
            edits: dict[str, Any] | None = None) -> None:
    """Mark a record verified, optionally applying curator edits first.

    The edited record is validated before it is written — a curator cannot
    save a record that would fail the schema.
    """
    def mutate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for record in records:
            if record["record_id"] != record_id:
                out.append(record)
                continue
            updated = {**record, **(edits or {})}
            updated["verified_by"] = reviewer
            updated["verified_date"] = date.today().isoformat()
            Record.model_validate(updated)
            out.append(updated)
        return out

    _rewrite_file(filename, mutate)


def reject(record_id: str, filename: str, reviewer: str,
           reason: str, note: str = "") -> None:
    """Move a record to rejected/ with its reason attached.

    Rejections feed prompt improvement (task 03), so the reason is structured
    rather than free text wherever possible.
    """
    path = DRAFTS_DIR / filename
    records = json.loads(path.read_text())
    rejected = [r for r in records if r["record_id"] == record_id]
    if not rejected:
        raise KeyError(f"{record_id} not in {filename}")

    target = REJECTED_DIR / filename
    existing = json.loads(target.read_text()) if target.exists() else []
    existing.append({
        "record": rejected[0],
        "rejection": {
            "reason": reason,
            "note": note,
            "rejected_by": reviewer,
            "rejected_date": date.today().isoformat(),
        },
    })
    _atomic_write(target, _dump(existing))
    _atomic_write(path, _dump([r for r in records if r["record_id"] != record_id]))


def rejected_count() -> int:
    """How many records have been rejected across all papers."""
    total = 0
    for path in REJECTED_DIR.glob("*.json"):
        try:
            total += len(json.loads(path.read_text()))
        except json.JSONDecodeError as e:
            logger.error(f"{path.name}: unreadable JSON — {e}")
    return total


def fulltext_for(pmid: str | None) -> str | None:
    """Cached full text for a record's paper, or None if not downloaded.

    The cache is gitignored, so a curator on a fresh clone has no context
    pane. That is a missing convenience, never a reason to doubt the quote.
    """
    if not pmid:
        return None
    for candidates in PAPERS_DIR.glob("candidates_*.csv"):
        with candidates.open() as handle:
            for row in csv.DictReader(handle):
                if row["pmid"] == pmid and row["pmcid"]:
                    cached = FULLTEXT_DIR / f"{row['pmcid']}.txt"
                    return cached.read_text() if cached.exists() else None
    return None

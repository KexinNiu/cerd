"""Tests for pipeline/review_store.py — approve/reject round trips."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline import review_store


def _record(record_id: str) -> dict:
    return {
        "record_id": record_id,
        "organism": "Escherichia coli",
        "taxid": 562,
        "strain": "MG1655",
        "condition": "UV",
        "dose_value": 40.0,
        "dose_unit": "J/m2",
        "assay": "CFU",
        "response_type": "survival",
        "response_value": 1.5,
        "response_unit": "percent",
        "evidence_level": "measured",
        "source_pmid": "123456",
        "source_quote": "Survival fell to 1.5 %.",
        "extracted_by": "agent-claude",
        "verified_by": None,
        "verified_date": None,
    }


@pytest.fixture
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    (drafts / "ecoli_123456.json").write_text(
        json.dumps([_record("ecoli-uv-1"), _record("ecoli-uv-2")])
    )
    monkeypatch.setattr(review_store, "DRAFTS_DIR", drafts)
    monkeypatch.setattr(review_store, "REJECTED_DIR", tmp_path / "rejected")
    return tmp_path


def _drafts(store: Path) -> list[dict]:
    return json.loads((store / "drafts" / "ecoli_123456.json").read_text())


def test_approve_stamps_reviewer_and_date(store: Path) -> None:
    review_store.approve("ecoli-uv-1", "ecoli_123456.json", "Kexin")
    approved = next(r for r in _drafts(store) if r["record_id"] == "ecoli-uv-1")
    assert approved["verified_by"] == "Kexin"
    assert approved["verified_date"]


def test_approve_leaves_other_records_untouched(store: Path) -> None:
    review_store.approve("ecoli-uv-1", "ecoli_123456.json", "Kexin")
    other = next(r for r in _drafts(store) if r["record_id"] == "ecoli-uv-2")
    assert other["verified_by"] is None


def test_approve_applies_edits(store: Path) -> None:
    review_store.approve(
        "ecoli-uv-1", "ecoli_123456.json", "Kexin", {"response_value": 2.5}
    )
    edited = next(r for r in _drafts(store) if r["record_id"] == "ecoli-uv-1")
    assert edited["response_value"] == 2.5


def test_approve_rejects_edits_that_break_the_schema(store: Path) -> None:
    """A curator must not be able to save a record the schema forbids."""
    with pytest.raises(ValidationError):
        review_store.approve(
            "ecoli-uv-1", "ecoli_123456.json", "Kexin", {"response_value": 150.0}
        )


def test_failed_approve_leaves_the_file_intact(store: Path) -> None:
    with pytest.raises(ValidationError):
        review_store.approve(
            "ecoli-uv-1", "ecoli_123456.json", "Kexin", {"response_value": 150.0}
        )
    assert len(_drafts(store)) == 2
    assert all(r["verified_by"] is None for r in _drafts(store))


def test_reject_moves_record_with_reason(store: Path) -> None:
    review_store.reject(
        "ecoli-uv-1", "ecoli_123456.json", "Kexin", "unit error", "J/mL not areal"
    )
    assert [r["record_id"] for r in _drafts(store)] == ["ecoli-uv-2"]
    rejected = json.loads((store / "rejected" / "ecoli_123456.json").read_text())
    assert rejected[0]["record"]["record_id"] == "ecoli-uv-1"
    assert rejected[0]["rejection"]["reason"] == "unit error"
    assert rejected[0]["rejection"]["rejected_by"] == "Kexin"


def test_reject_appends_rather_than_overwrites(store: Path) -> None:
    review_store.reject("ecoli-uv-1", "ecoli_123456.json", "Kexin", "wrong value")
    review_store.reject("ecoli-uv-2", "ecoli_123456.json", "Kexin", "wrong strain")
    rejected = json.loads((store / "rejected" / "ecoli_123456.json").read_text())
    assert len(rejected) == 2
    assert _drafts(store) == []


def test_reject_unknown_record_raises(store: Path) -> None:
    with pytest.raises(KeyError):
        review_store.reject("nope", "ecoli_123456.json", "Kexin", "other")


def test_progress_counts_only_the_chosen_organism(store: Path) -> None:
    records = [
        {"organism": "Escherichia coli", "verified_by": "Kexin"},
        {"organism": "Escherichia coli", "verified_by": None},
        {"organism": "Bacillus subtilis", "verified_by": None},
    ]
    progress = review_store.progress_for(records, "Escherichia coli")
    assert (progress.total, progress.verified) == (2, 1)
    assert progress.fraction == 0.5

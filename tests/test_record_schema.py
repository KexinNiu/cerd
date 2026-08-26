"""Tests for schema/record_schema.py — task 01."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from schema.record_schema import Record

EXAMPLES_DIR = Path(__file__).parent.parent / "schema" / "examples"


def _load(name: str) -> dict[str, Any]:
    return json.loads((EXAMPLES_DIR / name).read_text())


@pytest.mark.parametrize(
    "name", ["ecoli_uv_survival.json", "scerevisiae_heat_shock.json"]
)
def test_examples_validate(name: str) -> None:
    record = Record.model_validate(_load(name))
    assert record.record_id


def _base() -> dict[str, Any]:
    """A minimal valid UV record to break in targeted ways."""
    return {
        "record_id": "test-uv-001",
        "organism": "Escherichia coli",
        "taxid": 562,
        "condition": "UV",
        "dose_value": 10.0,
        "dose_unit": "J/m2",
        "assay": "CFU",
        "response_type": "survival",
        "response_value": 50.0,
        "response_unit": "percent",
        "evidence_level": "measured",
        "source_pmid": "123456",
        "source_quote": "half the cells survived.",
    }


def test_missing_both_sources_fails() -> None:
    data = _base()
    data.pop("source_pmid")
    with pytest.raises(ValidationError, match="source_doi or source_pmid"):
        Record.model_validate(data)


def test_negative_dose_fails() -> None:
    data = _base() | {"dose_value": -5.0}
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        Record.model_validate(data)


def test_percent_out_of_range_fails() -> None:
    data = _base() | {"response_value": 150.0}
    with pytest.raises(ValidationError, match=r"percent response outside \[0, 100\]"):
        Record.model_validate(data)


def test_bad_doi_fails() -> None:
    data = _base() | {"source_doi": "doi:not-a-doi"}
    with pytest.raises(ValidationError, match="invalid DOI"):
        Record.model_validate(data)


def test_overlong_quote_fails() -> None:
    data = _base() | {"source_quote": "x" * 301}
    with pytest.raises(ValidationError, match="at most 300 characters"):
        Record.model_validate(data)


def test_fold_change_above_100_ok() -> None:
    data = _base() | {"response_unit": "fold_change", "response_value": 400.0}
    assert Record.model_validate(data).response_value == 400.0


def test_uv_record_without_dose_fails() -> None:
    data = _base()
    data.pop("dose_value")
    with pytest.raises(ValidationError, match="UV record needs dose_value"):
        Record.model_validate(data)


def test_temperature_record_with_uv_fields_fails() -> None:
    data = _base() | {
        "condition": "temperature",
        "temp_c": 42.0,
        "temp_shift": "heat_shock",
    }
    with pytest.raises(ValidationError, match="must not carry UV fields"):
        Record.model_validate(data)


def test_unknown_field_fails() -> None:
    data = _base() | {"surprise_field": 1}
    with pytest.raises(ValidationError, match="surprise_field"):
        Record.model_validate(data)

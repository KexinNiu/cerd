"""Tests for pipeline/normalize.py."""
from __future__ import annotations

import pytest

from pipeline.normalize import (
    seconds_from_hours,
    survival_to_percent,
    uv_dose_to_j_per_m2,
)


@pytest.mark.parametrize(
    "value,unit,expected",
    [
        (40.0, "J/m2", 40.0),
        (4.0, "mJ/cm2", 40.0),
        (0.7425, "kJ/m2", 742.5),
        (1.0, "J/cm2", 10000.0),
        (40.0, "j/m2", 40.0),      # case-insensitive
        (40.0, " J/m2 ", 40.0),    # whitespace tolerated
    ],
)
def test_uv_dose_conversions(value: float, unit: str, expected: float) -> None:
    assert uv_dose_to_j_per_m2(value, unit) == pytest.approx(expected)


@pytest.mark.parametrize("unit", ["J/mL", "mJ", "unknown", None])
def test_uv_dose_non_areal_returns_none(unit: str | None) -> None:
    """Volumetric or unknown dose units must not be guessed at."""
    assert uv_dose_to_j_per_m2(10.0, unit) is None


def test_uv_dose_none_value() -> None:
    assert uv_dose_to_j_per_m2(None, "J/m2") is None


@pytest.mark.parametrize(
    "value,unit,expected",
    [
        (1.5, "percent", 1.5),
        (0.036, "surviving_fraction", 3.6),
        (0.056, "fraction (N/N0)", 5.6),
        (1.0, "log10 reduction", 10.0),
        (3.0, "log10_CFU/mL_reduction", 0.1),
        (0.0, "log10 reduction", 100.0),
    ],
)
def test_survival_conversions(value: float, unit: str, expected: float) -> None:
    assert survival_to_percent(value, unit) == pytest.approx(expected)


@pytest.mark.parametrize(
    "unit", ["fold_change", "days", "OD600", "h-1", "uM indole", None]
)
def test_survival_non_survival_units_return_none(unit: str | None) -> None:
    """Units that do not express survival must not be coerced into a percent."""
    assert survival_to_percent(5.0, unit) is None


def test_negative_log_reduction_rejected() -> None:
    assert survival_to_percent(-1.0, "log10 reduction") is None


def test_seconds_from_hours() -> None:
    assert seconds_from_hours(2.0) == 7200.0
    assert seconds_from_hours(None) is None

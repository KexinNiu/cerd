"""Unit normalization for CERD records.

Canonical units: UV dose in J/m2, temperature in degC, time in seconds.
Conversions are deliberately conservative — an unrecognized or
non-convertible unit returns None rather than a guess.

See CLAUDE.md ("Units") and tests/test_normalize.py.
"""
from __future__ import annotations

from typing import Optional

# Areal UV dose units -> multiplier to J/m2.
# J/mL is a volumetric (in-flow) dose and has NO areal equivalent: converting
# it would invent a path length. Such records carry no dose_j_m2.
_UV_DOSE_TO_J_M2: dict[str, float] = {
    "j/m2": 1.0,
    "j m-2": 1.0,
    "mj/cm2": 10.0,      # 1 mJ/cm2 = 10 J/m2
    "kj/m2": 1000.0,
    "j/cm2": 10000.0,
}

_SURVIVAL_AS_PERCENT: frozenset[str] = frozenset({"percent", "%"})
_SURVIVAL_AS_FRACTION: frozenset[str] = frozenset(
    {"surviving_fraction", "fraction", "fraction (n/n0)", "n/n0"}
)
_SURVIVAL_AS_LOG_REDUCTION: frozenset[str] = frozenset(
    {"log10 reduction", "log10_reduction", "log10_cfu/ml_reduction"}
)


def _key(unit: Optional[str]) -> str:
    return (unit or "").strip().lower()


def uv_dose_to_j_per_m2(value: Optional[float], unit: Optional[str]) -> Optional[float]:
    """Convert an areal UV dose to J/m2, or None if not convertible."""
    if value is None:
        return None
    factor = _UV_DOSE_TO_J_M2.get(_key(unit))
    return None if factor is None else value * factor


def survival_to_percent(value: Optional[float], unit: Optional[str]) -> Optional[float]:
    """Convert a survival readout to percent of the untreated control.

    Handles percent, fractional (N/N0) and log10-reduction readouts. Returns
    None for units that do not express survival (fold_change, days, OD600...).
    """
    if value is None:
        return None
    unit_key = _key(unit)
    if unit_key in _SURVIVAL_AS_PERCENT:
        return value
    if unit_key in _SURVIVAL_AS_FRACTION:
        return value * 100.0
    if unit_key in _SURVIVAL_AS_LOG_REDUCTION:
        if value < 0:
            return None
        return 100.0 * (10.0 ** -value)
    return None


def seconds_from_hours(hours: Optional[float]) -> Optional[float]:
    """Hours to seconds — the one time conversion the drafts need so far."""
    return None if hours is None else hours * 3600.0

"""The editable record form for the review tool.

Split out of review_app so the field list — the part that changes whenever the
schema changes — sits in one small file.
"""
from __future__ import annotations

from typing import Any

import streamlit as st

from schema.record_schema import Assay, EvidenceLevel, ResponseType

# Fields a curator is expected to correct while reading the quote. Identity and
# provenance fields (record_id, organism, taxid, source_*) are shown read-only
# elsewhere and are never editable here: fixing those is a re-extraction, not a
# review.
_TEXT_FIELDS = ("strain", "medium", "growth_phase", "response_unit", "dose_unit")
_NUMBER_FIELDS = ("dose_value", "temp_c", "response_value", "exposure_time_s")

_DIRECTIONS = ("", "increase", "decrease", "none")
_TEMP_SHIFTS = ("", "heat_shock", "cold_shock", "constant")
_UV_BANDS = ("", "UV-A", "UV-B", "UV-C")


def _options(enum_cls) -> list[str]:
    return [member.value for member in enum_cls]


def _index(options: list[str] | tuple[str, ...], value: Any) -> int:
    text = "" if value is None else str(value)
    return list(options).index(text) if text in options else 0


def render_edit_form(
    record: dict[str, Any], disabled: bool
) -> tuple[dict[str, Any], bool]:
    """Draw the form. Returns (edited fields, whether approve was submitted).

    Submitting the form IS approval — pressing Enter in any field approves,
    which is the whole point of a tool meant to run at ~30 seconds a record.
    """
    with st.form("record", clear_on_submit=False):
        edits: dict[str, Any] = {}
        condition = record["condition"]

        st.caption(f"{condition} · {record['assay']} · {record['evidence_level']}")

        if condition == "UV":
            band = st.selectbox("uv_band", _UV_BANDS, _index(_UV_BANDS, record.get("uv_band")))
            edits["uv_band"] = band or None
        else:
            shift = st.selectbox(
                "temp_shift", _TEMP_SHIFTS, _index(_TEMP_SHIFTS, record.get("temp_shift"))
            )
            edits["temp_shift"] = shift or None

        columns = st.columns(2)
        for i, field in enumerate(_NUMBER_FIELDS):
            value = record.get(field)
            with columns[i % 2]:
                entered = st.text_input(field, "" if value is None else str(value))
            entered = entered.strip()
            if not entered:
                edits[field] = None
                continue
            try:
                edits[field] = float(entered)
            except ValueError:
                st.warning(f"{field}: “{entered}” is not a number — left unchanged.")
                edits[field] = value

        for field in _TEXT_FIELDS:
            entered = st.text_input(field, record.get(field) or "")
            edits[field] = entered.strip() or None

        edits["assay"] = st.selectbox(
            "assay", _options(Assay), _index(_options(Assay), record.get("assay"))
        )
        edits["response_type"] = st.selectbox(
            "response_type", _options(ResponseType),
            _index(_options(ResponseType), record.get("response_type")),
        )
        edits["response_direction"] = st.selectbox(
            "response_direction", _DIRECTIONS,
            _index(_DIRECTIONS, record.get("response_direction")),
        ) or None
        edits["evidence_level"] = st.selectbox(
            "evidence_level", _options(EvidenceLevel),
            _index(_options(EvidenceLevel), record.get("evidence_level")),
            help="Downgrade to 'speculated' if the paper only proposes this.",
        )

        approved = st.form_submit_button(
            "✅ Approve  (Enter)", type="primary", disabled=disabled,
            use_container_width=True,
        )

    changed = {k: v for k, v in edits.items() if v != record.get(k)}
    return changed, approved

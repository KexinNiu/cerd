"""Curator review tool — task 04.

Launch with:  make review     (or: streamlit run pipeline/review_app.py)

One record at a time: the quote in its original context on the left, the
record as an editable form on the right. Approve, edit-and-approve, or reject
with a reason. Every action writes to disk immediately.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import review_store as store  # noqa: E402
from pipeline.review_fields import render_edit_form  # noqa: E402
from pipeline.textmatch import context_around, find_span  # noqa: E402

st.set_page_config(page_title="CERD curator review", page_icon="🔬", layout="wide")

QUOTE_CSS = """
<style>
  .ctx { font-size: 1.05rem; line-height: 1.7; }
  .ctx mark { background: #ffe8a3; padding: 0.1em 0.15em; border-radius: 2px; }
  .ctx .dim { color: #7b7f78; }
  .missing { color: #7b7f78; font-style: italic; }
</style>
"""


def _pending(records: list[dict], organism: str | None) -> list[dict]:
    return [
        r for r in records
        if not r.get("verified_by") and organism in (None, r.get("organism"))
    ]


def _render_context(record: dict) -> None:
    """Quote in situ when the full text is cached, quote alone otherwise."""
    quote = record["source_quote"]
    text = store.fulltext_for(record.get("source_pmid"))
    span = find_span(text, quote) if text else None

    if text and span:
        excerpt, start, end = context_around(text, span, sentences=2)
        st.markdown(
            f'<div class="ctx"><span class="dim">{excerpt[:start]}</span>'
            f"<mark>{excerpt[start:end]}</mark>"
            f'<span class="dim">{excerpt[end:]}</span></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(f'<div class="ctx"><mark>{quote}</mark></div>', unsafe_allow_html=True)
    if text is None:
        st.markdown(
            '<p class="missing">Full text not cached on this machine, so there is '
            "no surrounding context. Follow the source link to check the quote.</p>",
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "This quote was not found in the cached full text. Treat that as a "
            "reason to open the paper, not proof the record is wrong — but if the "
            "sentence really is not in the paper, reject it.",
            icon="⚠️",
        )


def _source_link(record: dict) -> str:
    if record.get("source_doi"):
        return f"https://doi.org/{record['source_doi']}"
    if record.get("source_pmid"):
        return f"https://pubmed.ncbi.nlm.nih.gov/{record['source_pmid']}/"
    return ""


def main() -> None:
    st.markdown(QUOTE_CSS, unsafe_allow_html=True)
    records = store.load_records()

    with st.sidebar:
        st.header("Reviewer")
        reviewer = st.text_input(
            "Your name", key="reviewer",
            help="Stamped onto every record you approve. Persists while the app runs.",
        )
        organisms = sorted({r["organism"] for r in records})
        organism = st.selectbox("Organism", ["All organisms", *organisms])
        organism = None if organism == "All organisms" else organism

        progress = store.progress_for(records, organism)
        st.progress(progress.fraction)
        st.caption(f"{progress.verified} of {progress.total} verified")

        st.caption(f"{store.rejected_count()} rejected so far")

    queue = _pending(records, organism)
    if not queue:
        st.success("Nothing left to review in this selection.", icon="✅")
        st.stop()

    record = queue[0]
    if not reviewer.strip():
        st.info("Enter your name in the sidebar to start reviewing.", icon="👈")

    st.subheader(f"*{record['organism']}* · {record['record_id']}")
    st.caption(f"{len(queue)} left in this selection")

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown("**What the paper says**")
        _render_context(record)
        link = _source_link(record)
        if link:
            st.markdown(f"[Open the source]({link})")
        if record.get("notes"):
            st.info(record["notes"], icon="📝")

    with right:
        st.markdown("**The record**")
        edits, approved = render_edit_form(record, disabled=not reviewer.strip())

        if approved:
            try:
                store.approve(record["record_id"], record["_file"], reviewer.strip(), edits)
            except Exception as e:  # surfaced to the curator, never swallowed
                st.error(f"Not saved — {e}")
            else:
                st.rerun()

        st.divider()
        with st.expander("Reject this record"):
            reason = st.selectbox("Reason", store.REJECTION_REASONS, key="reason")
            note = st.text_input("Note (required for 'other')", key="note")
            if st.button("Reject", type="secondary", disabled=not reviewer.strip()):
                if reason == "other" and not note.strip():
                    st.error("'other' needs a note.")
                else:
                    store.reject(
                        record["record_id"], record["_file"],
                        reviewer.strip(), reason, note.strip(),
                    )
                    st.rerun()


if __name__ == "__main__":
    main()

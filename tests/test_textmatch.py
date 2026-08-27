"""Tests for pipeline/textmatch.py."""
from __future__ import annotations

from pipeline.textmatch import context_around, find_span, fold, fold_str

PAPER = (
    "Cells were grown to mid-log phase. Survival fell to 1.5 % after "
    "40 J/m² of 254 nm irradiation at 42 °C. Repair was scored after 2 h. "
    "The effect was abolished in the mutant. A final unrelated sentence."
)


def test_fold_index_map_points_into_original() -> None:
    folded, index_map = fold("A ± B")
    assert len(folded) == len(index_map)
    for i, ch in enumerate(folded):
        assert ch in "ab"
        assert "A ± B".lower()[index_map[i]] == ch


def test_superscript_and_degree_are_folded() -> None:
    assert fold_str("40 J/m²") == fold_str("40 J/m2")
    assert fold_str("42 °C") == fold_str("42 C")
    assert fold_str("µM") == fold_str("uM")
    assert fold_str("5.6 × 10-2") == fold_str("5.6 x 10-2")


def test_digits_are_not_folded_away() -> None:
    assert fold_str("40 J/m2") != fold_str("41 J/m2")


def test_find_span_locates_retyped_quote() -> None:
    span = find_span(PAPER, "Survival fell to 1.5 % after 40 J/m2 of 254 nm irradiation at 42 C.")
    assert span is not None
    assert PAPER[span[0]:span[1]].startswith("Survival fell")
    assert "42 °C" in PAPER[span[0]:span[1]]


def test_find_span_returns_none_when_absent() -> None:
    assert find_span(PAPER, "Survival fell to 99 % after 40 J/m2.") is None


def test_context_expands_both_sides() -> None:
    span = find_span(PAPER, "Survival fell to 1.5 % after 40 J/m2 of 254 nm irradiation at 42 C.")
    assert span is not None
    excerpt, start, end = context_around(PAPER, span, sentences=1)
    assert excerpt.startswith("Cells were grown")
    assert excerpt[start:end].startswith("Survival fell")
    assert "Repair was scored" in excerpt


def test_context_clamps_at_document_edges() -> None:
    span = find_span(PAPER, "Cells were grown to mid-log phase.")
    assert span is not None
    excerpt, start, _ = context_around(PAPER, span, sentences=5)
    assert start == 0
    assert excerpt.startswith("Cells were grown")


def test_context_is_capped_for_text_without_sentence_breaks() -> None:
    """Flattened tables have no punctuation — the cap keeps the quote findable."""
    table = "col " * 400 + "Wild-type 6.6 x 10-2 " + "col " * 400
    span = find_span(table, "Wild-type 6.6 x 10-2")
    assert span is not None
    excerpt, start, end = context_around(table, span, max_chars=300)
    assert len(excerpt) <= 300
    assert excerpt[start:end] == "Wild-type 6.6 x 10-2"


def test_cap_does_not_truncate_a_quote_longer_than_the_budget() -> None:
    long_quote = "x " * 200
    text = f"Before. {long_quote}After."
    span = find_span(text, long_quote)
    assert span is not None
    excerpt, start, end = context_around(text, span, max_chars=50)
    assert excerpt[start:end].strip() == long_quote.strip()

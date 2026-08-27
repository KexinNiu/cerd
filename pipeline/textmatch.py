"""Locate an extracted quote inside a paper's full text.

Papers and extractors disagree on typography, not on claims: a paper's
"42 °C" is retyped as "42 C", "5.6 × 10⁻²" as "5.6 x 10-2", "µM" as "uM".
Folding removes that difference so a quote can still be found, while keeping
digits, decimal points and minus signs intact so numbers must still match.

`fold` also returns an index map, which is what lets the review tool show the
quote highlighted in its original, readable context.
"""
from __future__ import annotations

import re
import unicodedata

_DASHES = re.compile(r"[‐-―−]")
_SCI_TIMES = re.compile(r"(?<=\d)\s*[x×]\s*(?=10)")
_KEEP = re.compile(r"[a-z0-9.\-]")


def _pre_fold(text: str) -> str:
    """Character-level folding that preserves length wherever possible."""
    text = unicodedata.normalize("NFKC", text).lower()
    text = _DASHES.sub("-", text)
    return text.replace("μ", "u").replace("µ", "u")


def fold(text: str) -> tuple[str, list[int]]:
    """Return (folded text, index map back into `text`).

    `index_map[i]` is the offset in `text` of folded character `i`.
    """
    folded_chars: list[str] = []
    index_map: list[int] = []
    for original_index, char in enumerate(_pre_fold(text)):
        if _KEEP.match(char):
            folded_chars.append(char)
            index_map.append(original_index)
    return "".join(folded_chars), index_map


def fold_str(text: str) -> str:
    """Folded form only — for containment checks that need no positions."""
    # "±" typed as "+/-", and the multiplication sign in scientific notation,
    # are multi-character substitutions and so are handled before folding.
    text = _pre_fold(text).replace("+/-", "").replace("±", "")
    text = _SCI_TIMES.sub("", text)
    return "".join(ch for ch in text if _KEEP.match(ch)).strip(".")


def find_span(haystack: str, needle: str) -> tuple[int, int] | None:
    """Offsets of `needle` inside `haystack`, comparing folded forms.

    Returns None when the quote is not present — which the caller must treat
    as "cannot show context", never as "the quote is wrong".
    """
    folded_hay, index_map = fold(haystack)
    folded_needle = "".join(
        ch for ch in _pre_fold(needle).replace("+/-", "").replace("±", "")
        if _KEEP.match(ch)
    ).strip(".")
    if not folded_needle:
        return None
    at = folded_hay.find(folded_needle)
    if at == -1:
        return None
    start = index_map[at]
    end = index_map[at + len(folded_needle) - 1] + 1
    return start, end


_SENTENCE_END = re.compile(r"(?<=[.!?])\s")


def context_around(
    text: str, span: tuple[int, int], sentences: int = 2, max_chars: int = 700
) -> tuple[str, int, int]:
    """Expand a span by `sentences` on each side, capped at `max_chars`.

    The cap matters: flattened tables contain no sentence punctuation, so
    without it a quote taken from a table drags the whole table along and the
    curator has to hunt for the highlight.

    Returns (excerpt, quote start within excerpt, quote end within excerpt).
    """
    start, end = span
    # before[-1] is the boundary the quote's own sentence starts at, so one
    # sentence of lead-in means stepping back one boundary further.
    before = [m.end() for m in _SENTENCE_END.finditer(text, 0, start)]
    after = [m.start() for m in _SENTENCE_END.finditer(text, end)]
    left = before[-(sentences + 1)] if len(before) > sentences else 0
    right = after[sentences] if len(after) > sentences else len(text)

    # Share whatever budget the quote itself does not use, evenly either side.
    spare = max_chars - (end - start)
    if spare > 0:
        left = max(left, start - spare // 2)
        right = min(right, end + spare // 2)
    else:
        left, right = start, end
    return text[left:right], start - left, end - left

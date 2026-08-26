"""Fetch PMC OA full text as plain text — task 03 helper.

Only the PMC Open Access subset is fetched. Full text is written to
local_pdfs/ (gitignored) as a working copy; it must never be committed.

Usage:  python -m pipeline.fetch_fulltext PMC9392361 [PMC...]
"""
from __future__ import annotations

import logging
import re
import sys
import time
from pathlib import Path

from Bio import Entrez
from lxml import etree

from pipeline.search_pubmed import REPO_ROOT, load_env

logger = logging.getLogger(__name__)

CACHE_DIR = REPO_ROOT / "local_pdfs" / "fulltext"
DROP_TAGS = {"ref-list", "back", "table-wrap-foot", "fn-group"}


def _configure() -> None:
    env = load_env(REPO_ROOT / ".env")
    email = env.get("NCBI_EMAIL", "")
    if not email:
        raise SystemExit("NCBI_EMAIL missing in .env")
    Entrez.email = email
    if env.get("NCBI_API_KEY"):
        Entrez.api_key = env["NCBI_API_KEY"]


def xml_to_text(xml_bytes: bytes) -> str:
    """Flatten JATS XML to readable text, keeping tables, dropping references."""
    root = etree.fromstring(xml_bytes)
    for tag in DROP_TAGS:
        for node in root.iter(tag):
            node.getparent().remove(node)
    text = " ".join(root.itertext())
    return re.sub(r"\s+", " ", text).strip()


def fetch(pmcid: str, use_cache: bool = True) -> str:
    """Return plain-text full text for a PMC id (e.g. 'PMC9392361')."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = CACHE_DIR / f"{pmcid}.txt"
    if use_cache and cached.exists():
        return cached.read_text()
    numeric = pmcid.removeprefix("PMC")
    with Entrez.efetch(
        db="pmc", id=numeric, rettype="full", retmode="xml"
    ) as handle:
        raw = handle.read()
    time.sleep(0.35)
    if isinstance(raw, str):
        raw = raw.encode()
    text = xml_to_text(raw)
    if len(text) < 2000:
        logger.warning(f"{pmcid}: only {len(text)} chars — likely not OA full text")
    cached.write_text(text)
    return text


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _configure()
    for pmcid in sys.argv[1:]:
        text = fetch(pmcid)
        logger.info(f"{pmcid}: {len(text)} chars -> {CACHE_DIR / (pmcid + '.txt')}")


if __name__ == "__main__":
    main()

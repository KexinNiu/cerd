"""PubMed candidate search for CERD — task 02.

For each organism x condition cell: esearch PubMed (capped at 200), fetch
title/abstract/PMID/DOI/year/journal, map PMID -> PMCID via elink, check the
PMC OA subset via the OA web service, and write
data/papers/candidates_<organism>_<condition>.csv.

Screening is human work — this script does NOT filter by relevance.

Usage:  python -m pipeline.search_pubmed [--retmax 200]
"""
from __future__ import annotations

import argparse
import csv
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from Bio import Entrez

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
OUT_DIR = REPO_ROOT / "data" / "papers"

ORGANISMS: dict[str, str] = {
    "ecoli": "Escherichia coli",
    "bsubtilis": "Bacillus subtilis",
    "scerevisiae": "Saccharomyces cerevisiae",
    "celegans": "Caenorhabditis elegans",
}

CONDITION_TERMS: dict[str, str] = {
    "uv": (
        '(ultraviolet OR "UV radiation" OR "UV-C" OR "UV irradiation")[TIAB] '
        "AND (survival OR viability OR inactivation OR resistance)[TIAB]"
    ),
    "temperature": (
        '("heat shock" OR "cold shock" OR thermotolerance OR '
        '"heat stress" OR "temperature stress")[TIAB] '
        "AND (survival OR viability OR growth OR tolerance)[TIAB]"
    ),
}

CSV_COLUMNS = [
    "pmid", "doi", "pmcid", "oa_status", "year", "journal", "title",
    "abstract", "organism", "condition", "screened", "screen_reason",
]


@dataclass(frozen=True)
class EntrezConfig:
    email: str
    api_key: Optional[str] = None

    @property
    def delay_s(self) -> float:
        """NCBI rate limit: 3/s without key, 10/s with key. Stay under."""
        return 0.12 if self.api_key else 0.35


def load_env(path: Path) -> dict[str, str]:
    """Minimal .env parser (no external dependency)."""
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def configure_entrez(cfg: EntrezConfig) -> None:
    Entrez.email = cfg.email
    if cfg.api_key:
        Entrez.api_key = cfg.api_key


def _entrez_read(make_handle, cfg: EntrezConfig, retries: int = 3):
    """Open an Entrez handle and parse it, retrying on transient failures.

    NCBI occasionally drops chunked responses mid-stream (IncompleteRead),
    so both the request and the parse live inside the retry loop.
    """
    for attempt in range(1, retries + 1):
        try:
            with make_handle() as handle:
                result = Entrez.read(handle)
            time.sleep(cfg.delay_s)
            return result
        except (OSError, RuntimeError, ValueError) as e:
            if attempt == retries:
                raise
            wait = 5 * attempt
            logger.warning(f"Entrez call failed ({e!r}); retry {attempt} in {wait}s")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def search_pmids(query: str, retmax: int, cfg: EntrezConfig) -> list[str]:
    result = _entrez_read(
        lambda: Entrez.esearch(db="pubmed", term=query, retmax=retmax), cfg
    )
    return list(result["IdList"])


def _article_field(article: dict[str, Any]) -> dict[str, str]:
    """Pull title/abstract/year/journal/doi out of one PubmedArticle."""
    medline = article["MedlineCitation"]
    art = medline["Article"]
    title = str(art.get("ArticleTitle", ""))
    abstract = ""
    if "Abstract" in art:
        abstract = " ".join(str(t) for t in art["Abstract"].get("AbstractText", []))
    journal = str(art.get("Journal", {}).get("Title", ""))
    year = ""
    pub_date = art.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
    year = str(pub_date.get("Year", pub_date.get("MedlineDate", "")))[:4]
    doi = ""
    for aid in article.get("PubmedData", {}).get("ArticleIdList", []):
        if aid.attributes.get("IdType") == "doi":
            doi = str(aid)
    return {
        "title": title, "abstract": abstract, "journal": journal,
        "year": year, "doi": doi,
    }


def fetch_metadata(
    pmids: list[str], cfg: EntrezConfig, batch_size: int = 100
) -> dict[str, dict[str, str]]:
    """PMID -> {title, abstract, journal, year, doi}."""
    meta: dict[str, dict[str, str]] = {}
    for start in range(0, len(pmids), batch_size):
        batch = pmids[start:start + batch_size]
        records = _entrez_read(
            lambda: Entrez.efetch(db="pubmed", id=",".join(batch), retmode="xml"),
            cfg,
        )
        for article in records.get("PubmedArticle", []):
            pmid = str(article["MedlineCitation"]["PMID"])
            meta[pmid] = _article_field(article)
    return meta


def map_pmcids(pmids: list[str], cfg: EntrezConfig) -> dict[str, str]:
    """PMID -> PMCID (only PMIDs deposited in PMC appear)."""
    if not pmids:
        return {}
    linksets = _entrez_read(
        lambda: Entrez.elink(
            dbfrom="pubmed", db="pmc", id=pmids, linkname="pubmed_pmc"
        ),
        cfg,
    )
    mapping: dict[str, str] = {}
    for linkset in linksets:
        ids = linkset.get("IdList", [])
        links = linkset.get("LinkSetDb", [])
        if not ids or not links:
            continue
        pmid = str(ids[0])
        pmc_numeric = str(links[0]["Link"][0]["Id"])
        mapping[pmid] = f"PMC{pmc_numeric}"
    return mapping


def filter_oa(
    pmcids: list[str], cfg: EntrezConfig, batch_size: int = 100
) -> set[str]:
    """Subset of the given PMCIDs that are in the PMC Open Access subset.

    Uses esearch db=pmc with the "open access"[filter] — the classic
    oa.fcgi web service was retired by NCBI.
    """
    oa: set[str] = set()
    numeric = [p.removeprefix("PMC") for p in pmcids]
    for start in range(0, len(numeric), batch_size):
        batch = numeric[start:start + batch_size]
        term = (
            "(" + " OR ".join(f"{n}[UID]" for n in batch) + ")"
            ' AND "open access"[filter]'
        )
        result = _entrez_read(
            lambda: Entrez.esearch(db="pmc", term=term, retmax=batch_size), cfg
        )
        oa.update(f"PMC{n}" for n in result["IdList"])
    return oa


def build_cell(
    org_key: str, cond_key: str, retmax: int, cfg: EntrezConfig
) -> list[dict[str, str]]:
    organism = ORGANISMS[org_key]
    query = f'"{organism}"[TIAB] AND {CONDITION_TERMS[cond_key]}'
    logger.info(f"[{org_key} x {cond_key}] query: {query}")
    pmids = search_pmids(query, retmax, cfg)
    logger.info(f"[{org_key} x {cond_key}] {len(pmids)} PMIDs")
    meta = fetch_metadata(pmids, cfg)
    pmcids = map_pmcids(pmids, cfg)
    logger.info(f"[{org_key} x {cond_key}] {len(pmcids)} have a PMCID; checking OA")
    oa_set = filter_oa(list(pmcids.values()), cfg)
    rows: list[dict[str, str]] = []
    for pmid in pmids:
        m = meta.get(pmid, {})
        pmcid = pmcids.get(pmid, "")
        if pmcid:
            oa_status = "oa" if pmcid in oa_set else "pmc_not_oa"
        else:
            oa_status = "no_pmc"
        rows.append({
            "pmid": pmid,
            "doi": m.get("doi", ""),
            "pmcid": pmcid,
            "oa_status": oa_status,
            "year": m.get("year", ""),
            "journal": m.get("journal", ""),
            "title": m.get("title", ""),
            "abstract": m.get("abstract", ""),
            "organism": organism,
            "condition": cond_key,
            "screened": "",
            "screen_reason": "",
        })
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"wrote {path} ({len(rows)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retmax", type=int, default=200)
    parser.add_argument(
        "--cells", nargs="*", default=None,
        help="subset like ecoli_uv scerevisiae_temperature (default: all 8)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    env = load_env(REPO_ROOT / ".env")
    email = env.get("NCBI_EMAIL", "")
    if not email:
        raise SystemExit("NCBI_EMAIL missing in .env — Entrez requires it")
    cfg = EntrezConfig(email=email, api_key=env.get("NCBI_API_KEY") or None)
    configure_entrez(cfg)

    cells = args.cells or [
        f"{o}_{c}" for o in ORGANISMS for c in CONDITION_TERMS
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary: dict[str, dict[str, int]] = {}
    for cell in cells:
        org_key, _, cond_key = cell.partition("_")
        if org_key not in ORGANISMS or cond_key not in CONDITION_TERMS:
            raise SystemExit(f"unknown cell: {cell}")
        rows = build_cell(org_key, cond_key, args.retmax, cfg)
        write_csv(rows, OUT_DIR / f"candidates_{org_key}_{cond_key}.csv")
        summary[cell] = {
            "total": len(rows),
            "oa": sum(1 for r in rows if r["oa_status"] == "oa"),
        }

    logger.info("=== summary (candidates / OA full text) ===")
    for cell, counts in summary.items():
        logger.info(f"  {cell}: {counts['total']} candidates, {counts['oa']} OA")


if __name__ == "__main__":
    main()

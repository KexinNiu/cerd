"""Inline the record bundle into the standalone coverage-audit page.

Reads frontend/audit/audit_template.html, substitutes __CERD_DATA__ with the JSON
bundle, and writes frontend/audit/audit.html. The output is self-contained: no fetch,
no external data file, so it works from a file:// path or any static host.

Usage:  python -m pipeline.build_demo_page
"""
from __future__ import annotations

import json
import logging

from pipeline.build_bundle import OUT_PATH as BUNDLE_PATH
from pipeline.search_pubmed import REPO_ROOT

logger = logging.getLogger(__name__)

TEMPLATE_PATH = REPO_ROOT / "frontend" / "audit" / "audit_template.html"
PAGE_PATH = REPO_ROOT / "frontend" / "audit" / "audit.html"
PLACEHOLDER = "__CERD_DATA__"


def build() -> str:
    template = TEMPLATE_PATH.read_text()
    if PLACEHOLDER not in template:
        raise SystemExit(f"{PLACEHOLDER} missing from {TEMPLATE_PATH}")
    bundle = json.loads(BUNDLE_PATH.read_text())
    # Compact, and escaped so the payload cannot close the <script> element.
    payload = json.dumps(bundle, separators=(",", ":"), ensure_ascii=False)
    payload = payload.replace("</", "<\\/")
    return template.replace(PLACEHOLDER, payload)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if not BUNDLE_PATH.exists():
        raise SystemExit("bundle.json missing — run python -m pipeline.build_bundle")
    page = build()
    PAGE_PATH.write_text(page)
    logger.info(f"wrote {PAGE_PATH} ({len(page) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

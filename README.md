# CERD — Comparative Environmental Response Database

iGEM software project: a literature-mined, human-curated database comparing
model organism responses to environmental stresses, with an interactive
dose–response comparison UI.

**Start here:** read `CLAUDE.md` (project context), then work through
`tasks/00_setup.md` → `tasks/07_docs_wiki.md` in order. Each task file is a
self-contained brief for a Claude Code / Cowork session.

| # | Task | Owner | Status |
|---|------|-------|--------|
| 00 | Environment setup (local, IBEX decision) | dry lab | ☑ |
| 01 | Schema finalization + team sign-off | dry lab + all | ☐ |
| 02 | Literature search & screening | dry lab + curators | ☐ |
| 03 | LLM extraction pipeline | dry lab | ☐ |
| 04 | Curator review tool (Streamlit) | dry lab | ☐ |
| 05 | Normalization + release build + CI | dry lab | ☐ |
| 06 | Frontend (React, GitHub Pages) | dry lab | ◐ |
| 07 | Methods docs, licenses, wiki | all | ☐ |

## Setup

```bash
uv venv --python 3.11
uv pip install -r requirements.txt
cp .env.example .env   # fill in keys; .env is gitignored
```

Frontend (task 06) needs Node >= 18:

```bash
cd frontend && npm install && npm run dev
```

`pipeline/build_bundle.py` regenerates `frontend/src/data/cerd_draft.json`,
which the app imports statically. Deployed to GitHub Pages by
`.github/workflows/pages.yml` on any push touching `frontend/`.

Scope v1: E. coli, B. subtilis, S. cerevisiae, C. elegans × UV, temperature.
Data: CC-BY 4.0. Code: MIT.

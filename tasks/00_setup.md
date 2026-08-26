# Task 00 — Environment setup (local + optional IBEX)

## Goal
Working dev environment locally; decide whether IBEX is needed at all.

## Prompt for Claude Code session

You are setting up the CERD project (read CLAUDE.md first).

1. Create a GitHub repo `cerd` (private for now), push this scaffold.
2. Local Python env: create venv, `requirements.txt` with: biopython,
   requests, pydantic>=2, anthropic, streamlit, pandas, pytest, lxml.
   Verify `python -c "import Bio, pydantic, streamlit"` passes.
3. Add `.gitignore`: venv, __pycache__, .env, `local_pdfs/`, .DS_Store.
4. Create `.env.example` with ANTHROPIC_API_KEY= and NCBI_EMAIL= and
   NCBI_API_KEY= (optional, raises rate limit). Never commit .env.
5. Frontend prerequisites: check node >= 18 installed; do NOT scaffold the
   app yet (that's task 06).

## IBEX decision (read before doing anything on IBEX)

IBEX is NOT needed if extraction uses the Anthropic API (default plan).
The entire pipeline runs on a laptop. Only set up IBEX if the team decides
to run a local open-weights model for extraction (e.g. for paywalled PDFs
the university license doesn't allow sending to external APIs — check the
license terms first, many allow TDM).

If and only if that decision is made:
- `ssh <user>@ilogin.ibex.kaust.edu.sa`
- Work dir: `/ibex/user/<user>/cerd` (scratch is purged; don't keep the
  only copy of anything there — git push is the backup)
- `module load python/3.11` (or conda), clone the repo, same requirements.
- LLM inference: request a GPU node via slurm, run vLLM with an open model;
  extraction script takes an `--endpoint` flag so the same code hits either
  Anthropic API or the local vLLM server.

## Done when
- Repo pushed, venv works, .env.example present, README links to tasks/.

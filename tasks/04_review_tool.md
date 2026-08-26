# Task 04 — Curator review tool (Streamlit)

## Goal
A teammate with zero coding background reviews one record in ~30 seconds.
This tool is the whole curator recruitment pitch — polish matters here.

## Prompt for Claude Code session

Read CLAUDE.md. Build `pipeline/review_app.py` (Streamlit):

1. Sidebar: reviewer name (persisted), organism filter, progress bar
   (verified / total for this organism).
2. Main view, one record at a time:
   - LEFT: `source_quote` in large text, plus ±2 sentences of context pulled
     from the cached fulltext (highlight the quote). Link to DOI.
   - RIGHT: the record's fields as a compact editable form (st.form).
3. Buttons: ✅ Approve (sets verified_by + date, next record) /
   ✏️ Save edits & approve / ❌ Reject (requires a reason from a dropdown:
   wrong value | control-vs-treatment mixup | wrong strain | speculation
   marked as measured | unit error | other+text).
4. Rejects go to `data/records/rejected/` with the reason — these feed
   prompt improvements (task 03 iteration).
5. Keyboard-first: approve on Enter. Autosave. No login system — this runs
   locally or on one shared machine; reviewer name field is enough.
6. `make review` (or a run script) so curators launch it with one command.
   Write a 10-line CURATORS.md quickstart with screenshots.

## Calibration session (human step)
First team meeting after this ships: everyone reviews the same 20 records
together, disagreements resolved and written into CURATORS.md as rules.

## Done when
You can demo: launch, review 5 records end-to-end, progress persists across
restarts, rejected records carry reasons.

# Task 06 — Frontend (static React app on GitHub Pages)

## Goal
Select organisms + condition → see dose–response scatter + evidence table.
No backend; release JSON bundled at build time.

## Prompt for Claude Code session

Read CLAUDE.md and the release JSON shape from task 05.

1. Scaffold with Vite + React + TypeScript in `frontend/`. Plotly.js for
   charts (react-plotly.js). Import `cerd_v*.json` statically.
2. Layout (match the team's mockup structure, not its bar chart):
   - Panel 1: organism multi-select (checkboxes, grouped bacteria/yeast/
     multicellular)
   - Panel 2: condition select (UV | temperature) + parameter range slider
   - Panel 3: results
3. Results panel:
   - Dose–response scatter: x = dose (J/m²) or temperature (°C), y =
     response_value, color = organism, marker shape = assay. Points from
     the same paper's dose gradient connected with a thin dashed line.
     Hover: strain, assay, medium, DOI (clickable), source_quote.
   - Filters: assay type, evidence_level (default hides "speculated"),
     strain search.
   - Below: evidence table = filtered records, sortable, DOI links, CSV
     download of the current filtered view.
   - Permanent caption: "Cross-organism comparison is indicative, not
     quantitative — assays and strains differ. See Methods."
4. A Methods page rendering docs/methods.md.
5. Deploy: GitHub Action → GitHub Pages on push to main. Set Vite `base`
   correctly for project pages.

## Explicitly out of scope for v1
User accounts, data upload UI, backend API, the full 16×5 matrix, any
"AI answer" chat box. Do not add these even if they seem easy.

## Done when
Live URL works on mobile + desktop, loads < 2s, every plotted point traces
to a DOI.

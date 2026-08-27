.PHONY: review test audit bundle frontend

VENV := .venv/bin

## Launch the curator review tool
review:
	$(VENV)/streamlit run pipeline/review_app.py

## Run the Python test suite
test:
	$(VENV)/python -m pytest tests/ -q

## Re-check every draft record against schema, sources and full text
audit:
	$(VENV)/python -m pipeline.audit_drafts

## Rebuild the JSON the frontend imports
bundle:
	$(VENV)/python -m pipeline.build_bundle

## Run the frontend dev server
frontend:
	cd frontend && npm run dev

.PHONY: evidence-install evidence streamlit-install streamlit rill

evidence-install:
	cd evidence && npm install

evidence:
	cd evidence && npm run dev

streamlit-install:
	cd streamlit && poetry install

streamlit:
	cd streamlit && poetry run streamlit run app.py

rill:
	rill start rill/rill-project --db rill/data/duckdb_stats.db	

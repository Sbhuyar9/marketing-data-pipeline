PY ?= python
export DUCKDB_PATH ?= $(CURDIR)/data/marketing.duckdb
export DBT_PROFILES_DIR := $(CURDIR)/dbt_project

.PHONY: install demo ingest-local dbt-build quality test docs count-checks clean

install:
	pip install -r requirements.txt

## Full local demo: mock API -> raw -> bronze/silver/gold -> checks (DuckDB, no cloud accounts needed)
demo: ingest-local dbt-build quality

ingest-local:
	$(PY) -m ingestion.run_ingestion --mode local --with-mock-api

dbt-build:
	cd dbt_project && dbt deps && dbt build

quality:
	$(PY) -m quality.run_expectations

test:
	$(PY) -m pytest -q

docs:
	cd dbt_project && dbt docs generate && dbt docs serve

count-checks:
	$(PY) -m quality.count_checks

clean:
	rm -rf data reports dbt_project/target dbt_project/dbt_packages dbt_project/logs

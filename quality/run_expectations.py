"""Run Great Expectations suites (quality/expectations.yml) against the Gold marts.

Exits non-zero if any expectation fails, so it can gate CI / orchestration.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
import yaml

from ingestion.config import load_settings

SUITES_FILE = Path(__file__).with_name("expectations.yml")


def load_frame(table: str, backend: str) -> pd.DataFrame:
    settings = load_settings()
    if backend == "duckdb":
        import duckdb
        con = duckdb.connect(settings.duckdb_path, read_only=True)
        try:
            return con.execute(f"select * from {table}").df()
        finally:
            con.close()

    import snowflake.connector
    sf = settings.snowflake
    conn = snowflake.connector.connect(account=sf.account, user=sf.user, password=sf.password,
                                       role=sf.role, warehouse=sf.warehouse, database=sf.database)
    try:
        cur = conn.cursor()
        cur.execute(f"select * from {table}")
        frame = pd.DataFrame(cur.fetchall(), columns=[c[0].lower() for c in cur.description])
    finally:
        conn.close()
    return frame


def run_suites(backend: str) -> list[dict]:
    import great_expectations as ge

    suites = yaml.safe_load(SUITES_FILE.read_text())["suites"]
    results: list[dict] = []
    for suite in suites:
        dataset = ge.from_pandas(load_frame(suite["table"], backend))
        for exp in suite["expectations"]:
            outcome = getattr(dataset, exp["expectation_type"])(**exp.get("kwargs", {}))
            results.append({
                "suite": suite["name"],
                "expectation": exp["expectation_type"],
                "kwargs": exp.get("kwargs", {}),
                "success": bool(outcome.success),
                "observed": json.loads(json.dumps(outcome.result, default=str)),
            })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["duckdb", "snowflake"], default=os.environ.get("DBT_TARGET", "duckdb"))
    parser.add_argument("--report", default="reports/ge_results.json")
    args = parser.parse_args()

    results = run_suites(args.backend)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(results, indent=2))

    for r in results:
        print(f"[{'PASS' if r['success'] else 'FAIL'}] {r['suite']}: {r['expectation']}")
    failed = [r for r in results if not r["success"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} expectations passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

"""Loads landed NDJSON files into a local DuckDB `raw` schema (mirrors the Snowflake RAW schema)."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .sources import SourceSpec


def load_raw_tables(duckdb_path: str, raw_dir: str, specs: Iterable[SourceSpec]) -> None:
    import duckdb

    Path(duckdb_path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(duckdb_path)
    try:
        con.execute("create schema if not exists raw")
        for spec in specs:
            pattern = (Path(raw_dir) / spec.name / "*.ndjson").resolve().as_posix().replace("'", "''")
            con.execute(
                f"""
                create or replace table raw.{spec.name} as
                select * exclude (filename),
                       filename as _source_file,
                       current_timestamp as _loaded_at
                from read_json_auto('{pattern}', format='newline_delimited', filename=true)
                """
            )
    finally:
        con.close()

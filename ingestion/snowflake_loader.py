"""COPY INTO from the S3 external stage into Snowflake RAW tables.

Snowflake tracks loaded files per table (64 days), so re-running is idempotent.
Run sql/snowflake_setup.sql once before using this module.
"""
from __future__ import annotations

from typing import Iterable

from .config import SnowflakeSettings
from .sources import SourceSpec

COPY_SQL = """
COPY INTO RAW.{table}
FROM @RAW.MARKETING_S3_STAGE/{table}/
FILE_FORMAT = (FORMAT_NAME = RAW.NDJSON_FORMAT)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
INCLUDE_METADATA = (_source_file = METADATA$FILENAME)
ON_ERROR = ABORT_STATEMENT
"""


def copy_into_raw(settings: SnowflakeSettings, specs: Iterable[SourceSpec]) -> dict[str, int]:
    import snowflake.connector

    conn = snowflake.connector.connect(
        account=settings.account, user=settings.user, password=settings.password,
        role=settings.role, warehouse=settings.warehouse, database=settings.database,
    )
    loaded: dict[str, int] = {}
    try:
        cur = conn.cursor()
        for spec in specs:  # table names come from the static SOURCES catalogue, never user input
            cur.execute(COPY_SQL.format(table=spec.name.upper()))
            rows = cur.fetchall()
            loaded[spec.name] = sum(int(r[3]) for r in rows if len(r) > 3 and str(r[3]).isdigit())
    finally:
        conn.close()
    return loaded

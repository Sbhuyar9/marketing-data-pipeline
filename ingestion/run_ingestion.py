"""Ingestion entry point.

  cloud: REST APIs -> gzip NDJSON -> S3 -> Snowflake RAW (COPY INTO)
  local: REST APIs -> NDJSON files -> DuckDB raw schema (demo / CI)
"""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .api_client import ApiClient
from .config import Settings, load_settings
from .extract import extract
from .sources import SOURCES, SOURCES_BY_NAME, SourceSpec
from .writer import write_ndjson


def run(mode: str, specs: list[SourceSpec], settings: Settings) -> dict[str, int]:
    clients = {
        "marketing": ApiClient(settings.marketing_api.base_url, settings.marketing_api.token),
        "crm": ApiClient(settings.crm_api.base_url, settings.crm_api.token),
    }
    cloud = mode == "cloud"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    counts: dict[str, int] = {}

    for spec in specs:
        out_dir = Path(settings.raw_dir) / spec.name
        if not cloud:
            shutil.rmtree(out_dir, ignore_errors=True)   # keep local demo runs idempotent
        filename = f"{spec.name}_{stamp}.ndjson" + (".gz" if cloud else "")
        path = out_dir / filename
        counts[spec.name] = write_ndjson(extract(spec, clients[spec.system]), path, compress=cloud)
        print(f"extracted {counts[spec.name]:>6} rows  {spec.name}")

        if cloud:
            from .s3_loader import build_key, upload_file
            uri = upload_file(path, settings.s3_bucket, build_key(settings.s3_prefix, spec.name, filename),
                              settings.aws_region)
            print(f"uploaded  {uri}")

    if cloud:
        from .snowflake_loader import copy_into_raw
        copy_into_raw(settings.snowflake, specs)
        print("COPY INTO RAW complete")
    else:
        from .local_loader import load_raw_tables
        load_raw_tables(settings.duckdb_path, settings.raw_dir, specs)
        print(f"loaded raw tables into {settings.duckdb_path}")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["cloud", "local"], default="local")
    parser.add_argument("--source", choices=["all", *SOURCES_BY_NAME], default="all")
    parser.add_argument("--with-mock-api", action="store_true",
                        help="start the built-in mock API and ingest from it (no credentials needed)")
    args = parser.parse_args()

    settings = load_settings()
    if args.with_mock_api:
        from dataclasses import replace
        from .config import ApiSettings
        from .mock_api import start_in_thread
        _, base_url = start_in_thread()
        settings = replace(settings, marketing_api=ApiSettings(base_url, None), crm_api=ApiSettings(base_url, None))

    specs = SOURCES if args.source == "all" else [SOURCES_BY_NAME[args.source]]
    run(args.mode, specs, settings)


if __name__ == "__main__":
    main()

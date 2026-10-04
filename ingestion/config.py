"""Runtime configuration, read from environment variables (and a local .env file)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class ApiSettings:
    base_url: str
    token: str | None


@dataclass(frozen=True)
class SnowflakeSettings:
    account: str
    user: str
    password: str
    role: str
    warehouse: str
    database: str


@dataclass(frozen=True)
class Settings:
    marketing_api: ApiSettings
    crm_api: ApiSettings
    raw_dir: str
    duckdb_path: str
    s3_bucket: str
    s3_prefix: str
    aws_region: str
    snowflake: SnowflakeSettings


def load_settings() -> Settings:
    load_dotenv()
    env = os.environ.get
    return Settings(
        marketing_api=ApiSettings(env("MARKETING_API_URL", ""), env("MARKETING_API_TOKEN") or None),
        crm_api=ApiSettings(env("CRM_API_URL", ""), env("CRM_API_TOKEN") or None),
        raw_dir=env("RAW_DIR", "data/raw"),
        duckdb_path=env("DUCKDB_PATH", "data/marketing.duckdb"),
        s3_bucket=env("S3_BUCKET", ""),
        s3_prefix=env("S3_PREFIX", "marketing-raw"),
        aws_region=env("AWS_REGION", "us-east-1"),
        snowflake=SnowflakeSettings(
            account=env("SNOWFLAKE_ACCOUNT", ""),
            user=env("SNOWFLAKE_USER", ""),
            password=env("SNOWFLAKE_PASSWORD", ""),
            role=env("SNOWFLAKE_ROLE", "TRANSFORMER"),
            warehouse=env("SNOWFLAKE_WAREHOUSE", "MARKETING_WH"),
            database=env("SNOWFLAKE_DATABASE", "MARKETING"),
        ),
    )

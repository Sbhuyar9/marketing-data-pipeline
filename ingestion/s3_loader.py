from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def build_key(prefix: str, source: str, filename: str, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return f"{prefix.strip('/')}/{source}/dt={now:%Y-%m-%d}/{filename}"


def upload_file(path: str | Path, bucket: str, key: str, region: str) -> str:
    import boto3

    boto3.client("s3", region_name=region).upload_file(str(path), bucket, key)
    return f"s3://{bucket}/{key}"

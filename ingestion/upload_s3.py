"""Stage landing files into S3 (date-partitioned). No-op when S3_BUCKET is unset."""
import os
from datetime import date
from pathlib import Path

LANDING = Path(__file__).resolve().parents[1] / "data" / "landing"


def run():
    bucket = os.getenv("S3_BUCKET")
    if not bucket:
        print("S3_BUCKET not set -> keeping files in local landing zone")
        return
    import boto3
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
    prefix = os.getenv("S3_PREFIX", "marketing/raw")
    for f in LANDING.glob("*.*"):
        key = f"{prefix}/{f.stem}/load_date={date.today():%Y-%m-%d}/{f.name}"
        s3.upload_file(str(f), bucket, key, ExtraArgs={"ServerSideEncryption": "AES256"})
        print(f"s3://{bucket}/{key}")


if __name__ == "__main__":
    run()

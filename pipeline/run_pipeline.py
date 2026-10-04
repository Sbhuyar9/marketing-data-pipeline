"""Orchestrates: extract -> stage (S3) -> bronze load -> dbt build -> GE validation -> docs.
Usage: python pipeline/run_pipeline.py [--skip-generate] [--target dev|snowflake]"""
import argparse, subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingestion"))


def sh(cmd, cwd=ROOT):
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-generate", action="store_true")
    ap.add_argument("--target", default="dev")
    a = ap.parse_args()
    dbt = ["dbt"]
    dbt_args = ["--profiles-dir", ".", "--target", a.target]

    print("== 1. Ingest =="); 
    if not a.skip_generate:
        import extract; extract.run()
    import upload_s3; upload_s3.run()

    if a.target == "dev":
        print("== 2. Bronze load (local Snowpipe stand-in) ==")
        import load_bronze_local; load_bronze_local.run()
    else:
        print("== 2. Bronze load == handled by Snowpipe (see snowflake/setup.sql)")

    print("== 3. dbt build (models + tests) ==")
    sh(dbt + ["build"] + dbt_args, cwd=ROOT / "dbt")

    if a.target == "dev":
        print("== 4. Great Expectations ==")
        sh([sys.executable, "quality/validate.py"])

    print("== 5. dbt docs (lineage) ==")
    sh(dbt + ["docs", "generate"] + dbt_args, cwd=ROOT / "dbt")
    print("\nPipeline complete. View lineage: cd dbt && dbt docs serve --profiles-dir .")


if __name__ == "__main__":
    main()

"""Local stand-in for Snowpipe/COPY INTO: loads landing files into DuckDB bronze
tables. Raw event payload is kept as a JSON column (Snowflake VARIANT analogue)."""
import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "warehouse" / "marketing.duckdb"
LAND = ROOT / "data" / "landing"


def run():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB))
    land = LAND.as_posix()
    con.execute("create schema if not exists bronze")
    con.execute(f"""
        create or replace table bronze.ga_events as
        select raw::JSON as payload_json, current_timestamp as _loaded_at, 'ga_events.jsonl' as _source_file
        from read_csv('{land}/ga_events.jsonl', columns={{'raw':'VARCHAR'}}, delim='\x01', quote='', escape='', header=false)
    """)
    con.execute(f"""
        create or replace table bronze.crm_customers as
        select *, current_timestamp as _loaded_at, 'crm_customers.csv' as _source_file
        from read_csv('{land}/crm_customers.csv', all_varchar=true, header=true)
    """)
    con.execute(f"""
        create or replace table bronze.campaign_spend as
        select *, current_timestamp as _loaded_at, 'campaign_spend.csv' as _source_file
        from read_csv('{land}/campaign_spend.csv', all_varchar=true, header=true)
    """)
    for t in ("ga_events", "crm_customers", "campaign_spend"):
        print(f"bronze.{t}: {con.execute(f'select count(*) from bronze.{t}').fetchone()[0]:,} rows")
    con.close()


if __name__ == "__main__":
    run()
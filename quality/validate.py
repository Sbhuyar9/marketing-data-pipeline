"""Great Expectations validation of silver/gold tables. Exits non-zero on failure
so the orchestrator (or CI/Airflow) halts before BI tools consume bad data.
Writes a metadata log (JSON lines) for audit trails."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
import duckdb
import great_expectations as gx
from great_expectations import expectations as gxe

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "warehouse" / "marketing.duckdb"
AUDIT_LOG = ROOT / "warehouse" / "quality_audit.jsonl"

SUITES = {
    "silver.stg_events": [
        gxe.ExpectColumnValuesToNotBeNull(column="event_id"),
        gxe.ExpectColumnValuesToBeUnique(column="event_id"),
        gxe.ExpectColumnValuesToBeInSet(column="event_type", value_set=["impression", "click", "purchase"]),
        gxe.ExpectColumnValuesToBeBetween(column="revenue_usd", min_value=0, max_value=1_000_000),
        gxe.ExpectColumnValuesToMatchRegex(column="customer_id", regex=r"^C-\d{5}$", mostly=0.95),
        gxe.ExpectColumnToExist(column="campaign_id"),
    ],
    "silver.stg_customers": [
        gxe.ExpectColumnValuesToBeUnique(column="customer_id"),
        gxe.ExpectColumnValuesToMatchRegex(column="email", regex=r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"),
        gxe.ExpectColumnValuesToBeInSet(column="region", value_set=["northeast", "south", "midwest", "west"]),
    ],
    "gold.fct_campaign_performance": [
        gxe.ExpectColumnValuesToNotBeNull(column="campaign_id"),
        gxe.ExpectColumnValuesToBeBetween(column="ctr", min_value=0, max_value=1),
        gxe.ExpectColumnValuesToBeBetween(column="spend_usd", min_value=0),
        gxe.ExpectTableRowCountToBeBetween(min_value=1),
    ],
    "gold.dim_customer_rfm": [
        gxe.ExpectColumnValuesToBeUnique(column="customer_id"),
        gxe.ExpectColumnValuesToBeBetween(column="r_score", min_value=1, max_value=5),
        gxe.ExpectColumnValuesToBeBetween(column="f_score", min_value=1, max_value=5),
        gxe.ExpectColumnValuesToBeBetween(column="m_score", min_value=1, max_value=5),
        gxe.ExpectColumnValuesToBeInSet(column="segment",
            value_set=["Champions", "Loyal", "Recent", "At Risk", "Cant Lose Them", "Hibernating", "Needs Attention"]),
    ],
}


def main() -> int:
    context = gx.get_context(mode="ephemeral")
    source = context.data_sources.add_pandas("warehouse")
    con = duckdb.connect(str(DB), read_only=True)
    run_ts = datetime.now(timezone.utc).isoformat()
    failures, records = 0, []

    for table, expectations in SUITES.items():
        df = con.execute(f"select * from {table}").df()
        asset = source.add_dataframe_asset(name=table)
        batch = asset.add_batch_definition_whole_dataframe("full").get_batch(batch_parameters={"dataframe": df})
        for exp in expectations:
            res = batch.validate(exp)
            ok = bool(res.success)
            failures += (not ok)
            records.append({"run_ts": run_ts, "table": table, "expectation": type(exp).__name__,
                            "column": getattr(exp, "column", None), "success": ok,
                            "unexpected_count": (res.result or {}).get("unexpected_count")})
            print(f"  [{'PASS' if ok else 'FAIL'}] {table:34s} {type(exp).__name__}({getattr(exp, 'column', '')})")

    with open(AUDIT_LOG, "a") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"\nGreat Expectations: {len(records) - failures}/{len(records)} passed  (audit -> {AUDIT_LOG.name})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

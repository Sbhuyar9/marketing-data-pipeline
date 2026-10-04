"""Quick console report from the gold layer."""
import duckdb
from pathlib import Path
con = duckdb.connect(str(Path(__file__).resolve().parents[1] / "warehouse" / "marketing.duckdb"), read_only=True)
print("\nTop channels by ROAS")
print(con.execute("""select channel, sum(impressions) impr, sum(clicks) clicks, sum(conversions) conv,
    round(sum(spend_usd)) spend, round(sum(revenue_usd)) revenue, round(sum(revenue_usd)/sum(spend_usd),2) roas
    from gold.fct_campaign_performance group by 1 order by roas desc""").df().to_string(index=False))
print("\nRFM segments"); print(con.execute("select * from gold.mart_segment_summary order by total_revenue_usd desc").df().to_string(index=False))

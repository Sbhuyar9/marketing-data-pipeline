"""Generate realistic, deliberately messy marketing data (GA-style events, CRM
customers, campaign spend) so the pipeline has something to clean."""
import json, random, csv
from datetime import datetime, timedelta, date
from pathlib import Path

CHANNELS = ["paid_search", "email", "social", "display", "affiliate"]
REGIONS = ["northeast", "south", "midwest", "west"]
PRODUCTS = ["ira", "401k_rollover", "annuity", "advisory"]


def generate(out_dir: Path, n_customers=1500, n_events=60000, days=90, seed=42):
    rnd = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    end = datetime(2026, 9, 1)
    start = end - timedelta(days=days)

    campaigns = [
        {"campaign_id": f"CMP-{i:03d}", "campaign_name": f"{rnd.choice(PRODUCTS)}_{rnd.choice(['spring','summer','q3'])}_{i}",
         "channel": CHANNELS[i % len(CHANNELS)]} for i in range(1, 16)
    ]

    # ---- CRM customers (with dupes + dirty casing/whitespace) ----
    rows = []
    for i in range(1, n_customers + 1):
        cid = f"C-{i:05d}"
        email = f"user{i}@example.com"
        signup = start - timedelta(days=rnd.randint(0, 900))
        rows.append({
            "customer_id": cid, "email": email, "first_name": f"First{i}", "last_name": f"Last{i}",
            "region": rnd.choice(REGIONS), "signup_date": signup.date().isoformat(),
            "updated_at": (signup + timedelta(days=rnd.randint(0, 30))).isoformat(),
        })
    dirty = []
    for r in rows:
        d = dict(r)
        if rnd.random() < 0.08:
            d["email"] = "  " + d["email"].upper() + " "
        if rnd.random() < 0.08:
            d["region"] = d["region"].capitalize()
        dirty.append(d)
        if rnd.random() < 0.05:  # stale duplicate row (older updated_at)
            old = dict(d)
            old["updated_at"] = (datetime.fromisoformat(d["updated_at"]) - timedelta(days=60)).isoformat()
            old["region"] = rnd.choice(REGIONS)
            dirty.append(old)
    with open(out_dir / "crm_customers.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(dirty)

    # ---- GA-style events (semi-structured JSONL) ----
    events = []
    for i in range(n_events):
        ts = start + timedelta(seconds=rnd.randint(0, days * 86400))
        camp = rnd.choice(campaigns)
        roll = rnd.random()
        etype = "impression" if roll < 0.82 else "click"
        cust = f"C-{rnd.randint(1, n_customers):05d}"
        if rnd.random() < 0.05: cust = cust.lower()          # dirty id
        if rnd.random() < 0.02: cust = None                  # anonymous
        ev = {
            "event_id": f"EV-{i:07d}",
            "event_timestamp": ts.isoformat(),
            "event_type": etype,
            "customer_id": cust,
            "campaign_id": camp["campaign_id"],
            "channel": camp["channel"],
            "device": {"category": rnd.choice(["mobile", "desktop", "tablet"]), "os": rnd.choice(["ios", "android", "windows", "macos"])},
            "page": {"path": rnd.choice(["/retirement", "/ira", "/advice", "/rollover"])},
        }
        if etype == "purchase":
            ev["revenue"] = round(rnd.lognormvariate(6.5, 0.8), 2)
        events.append(ev)
    # purchases are derived from clicks (same campaign/customer/day) so the funnel is coherent
    n = len(events)
    for ev in [e for e in events if e["event_type"] == "click" and rnd.random() < 0.09]:
        n += 1
        t = datetime.fromisoformat(ev["event_timestamp"])
        t2 = min(t + timedelta(minutes=rnd.randint(1, 30)), t.replace(hour=23, minute=59, second=59))
        p = dict(ev, event_id=f"EV-{n:07d}", event_timestamp=t2.isoformat(), event_type="purchase",
                 revenue=round(rnd.lognormvariate(6.5, 0.8), 2))
        events.append(p)
    # inject duplicates (at-least-once delivery) and a couple of bad rows
    events += rnd.sample(events, int(n_events * 0.01))
    with open(out_dir / "ga_events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    # ---- Campaign spend (daily) ----
    with open(out_dir / "campaign_spend.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["spend_date", "campaign_id", "spend_usd"])
        for d in range(days):
            day = (start + timedelta(days=d)).date().isoformat()
            for c in campaigns:
                w.writerow([day, c["campaign_id"], round(rnd.uniform(50, 900), 2)])
    return out_dir


if __name__ == "__main__":
    p = generate(Path(__file__).resolve().parents[1] / "data" / "landing")
    print(f"Generated raw files in {p}")

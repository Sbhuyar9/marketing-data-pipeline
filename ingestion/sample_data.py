"""Deterministic synthetic marketing + CRM data, with realistic mess for the Silver layer to clean:
duplicate rows, mixed casing / padding, null keys and a few negative amounts."""
from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

CHANNELS = ["GOOGLE_ADS", "META_ADS", "EMAIL", "LINKEDIN", "TIKTOK"]
CAMPAIGN_STATUSES = ["ACTIVE", "PAUSED", "COMPLETED"]
ORDER_STATUSES = ["COMPLETED", "REFUNDED", "CANCELLED", "PENDING"]
ORDER_STATUS_WEIGHTS = [80, 5, 8, 7]
COUNTRIES = ["US", "GB", "DE", "IN", "CA", "AU", "FR"]
FIRST = ["ava", "liam", "noah", "emma", "olivia", "arjun", "priya", "mia", "lucas", "zoe", "ravi", "ella"]
LAST = ["smith", "patel", "garcia", "khan", "brown", "singh", "lee", "martin", "clark", "evans"]


def _messy(rng: random.Random, value: str, p: float = 0.2, lower: bool = True) -> str:
    r = rng.random()
    if lower and r < p / 2:
        return value.lower()
    if r < p:
        return f" {value} "
    return value


def generate_dataset(seed: int = 42, n_campaigns: int = 12, n_customers: int = 500,
                     start: date = date(2025, 1, 1)) -> dict[str, list[dict[str, Any]]]:
    rng = random.Random(seed)

    # ---- campaigns ----
    campaigns: list[dict[str, Any]] = []
    for i in range(1, n_campaigns + 1):
        channel = CHANNELS[(i - 1) % len(CHANNELS)]
        c_start = start + timedelta(days=rng.randint(0, 30))
        campaigns.append({
            "campaign_id": f"CMP-{i:03d}",
            "campaign_name": f"{channel.title().replace('_', ' ')} Campaign {i}",
            "channel": _messy(rng, channel),
            "start_date": c_start.isoformat(),
            "end_date": (c_start + timedelta(days=44)).isoformat(),
            "budget": round(rng.uniform(20000, 90000), 2),
            "status": _messy(rng, rng.choice(CAMPAIGN_STATUSES)),
        })

    # ---- daily ad performance ----
    ad_performance: list[dict[str, Any]] = []
    for camp in campaigns:
        c_start = date.fromisoformat(camp["start_date"])
        for d in range(45):
            impressions = rng.randint(1000, 50000)
            clicks = int(impressions * rng.uniform(0.01, 0.06))
            row = {
                "campaign_id": camp["campaign_id"],
                "ad_date": (c_start + timedelta(days=d)).isoformat(),
                "impressions": impressions,
                "clicks": clicks,
                "spend": round(clicks * rng.uniform(0.3, 3.0), 2),
                "conversions": int(clicks * rng.uniform(0.02, 0.10)),
            }
            ad_performance.append(row)
            if rng.random() < 0.02:          # re-delivered row
                ad_performance.append(dict(row))

    # ---- customers ----
    customers: list[dict[str, Any]] = []
    for i in range(1, n_customers + 1):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        email = f"{first}.{last}.{i}@example.com"
        row = {
            "customer_id": f"C-{i:05d}",
            "email": email.upper() if rng.random() < 0.10 else _messy(rng, email, 0.1, lower=False),
            "first_name": first.upper() if rng.random() < 0.1 else first,
            "last_name": last,
            "country": _messy(rng, rng.choice(COUNTRIES), 0.2),
            "signup_date": (date(2024, 6, 1) + timedelta(days=rng.randint(0, 270))).isoformat(),
            "marketing_opt_in": rng.random() < 0.7,
        }
        customers.append(row)
        if rng.random() < 0.03:
            customers.append(dict(row))
    for k in range(5):                        # rows with a missing primary key
        customers.append({"customer_id": None, "email": f"nokey{k}@example.com", "first_name": "x",
                          "last_name": "y", "country": "US", "signup_date": "2024-07-01",
                          "marketing_opt_in": False})

    # ---- orders ----
    orders: list[dict[str, Any]] = []
    n = 0
    for i in range(1, n_customers + 1):
        for _ in range(rng.choices([0, 1, 2, 3, 4, 5, 6, 8], weights=[10, 20, 20, 15, 12, 10, 8, 5])[0]):
            n += 1
            amount = round(rng.uniform(10, 500), 2)
            if rng.random() < 0.005:          # bad data: negative amount
                amount = -amount
            row = {
                "order_id": f"O-{n:06d}",
                "customer_id": f"C-{i:05d}",
                "campaign_id": rng.choice(campaigns)["campaign_id"] if rng.random() < 0.6 else None,
                "order_date": (start + timedelta(days=rng.randint(0, 180))).isoformat(),
                "order_amount": amount,
                "status": _messy(rng, rng.choices(ORDER_STATUSES, weights=ORDER_STATUS_WEIGHTS)[0]),
            }
            orders.append(row)
            if rng.random() < 0.02:
                orders.append(dict(row))
    for k in range(5):                        # orders without a customer
        n += 1
        orders.append({"order_id": f"O-{n:06d}", "customer_id": None, "campaign_id": None,
                       "order_date": "2025-03-01", "order_amount": 50.0, "status": "COMPLETED"})

    return {"campaigns": campaigns, "ad_performance": ad_performance,
            "customers": customers, "orders": orders}

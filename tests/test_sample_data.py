from ingestion.sample_data import generate_dataset


def test_deterministic():
    assert generate_dataset(seed=7) == generate_dataset(seed=7)


def test_contains_realistic_mess_for_silver_to_clean():
    ds = generate_dataset()
    ids = [r["customer_id"] for r in ds["customers"] if r["customer_id"]]
    assert len(ids) > len(set(ids)), "expected duplicate customers"
    assert any(r["customer_id"] is None for r in ds["customers"])
    assert any(r["order_amount"] < 0 for r in ds["orders"])
    assert any(r["customer_id"] is None for r in ds["orders"])
    assert any(r["channel"] != r["channel"].strip().upper() for r in ds["campaigns"])


def test_all_sources_present_and_non_empty():
    ds = generate_dataset()
    assert set(ds) == {"campaigns", "ad_performance", "customers", "orders"}
    assert all(len(rows) > 0 for rows in ds.values())

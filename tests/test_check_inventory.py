from quality.count_checks import count_checks


def test_check_inventory_matches_documented_total():
    counts = count_checks()
    assert counts["total"] == 44
    assert counts["great_expectations"] == 6
    assert counts["dbt_total"] == 38

"""Inventory of automated data-quality checks: dbt generic + singular tests and Great Expectations."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DBT = ROOT / "dbt_project"


def _tests_in(node: dict) -> int:
    return len(node.get("data_tests", []) or []) + len(node.get("tests", []) or [])


def count_dbt_generic() -> int:
    total = 0
    for yml in (DBT / "models").rglob("*.yml"):
        for model in (yaml.safe_load(yml.read_text()) or {}).get("models", []) or []:
            total += _tests_in(model)
            total += sum(_tests_in(col) for col in model.get("columns", []) or [])
    return total


def count_dbt_singular() -> int:
    return len(list((DBT / "tests").glob("*.sql")))


def count_ge() -> int:
    suites = yaml.safe_load((ROOT / "quality" / "expectations.yml").read_text())["suites"]
    return sum(len(s["expectations"]) for s in suites)


def count_checks() -> dict[str, int]:
    generic, singular, ge = count_dbt_generic(), count_dbt_singular(), count_ge()
    return {"dbt_generic": generic, "dbt_singular": singular, "dbt_total": generic + singular,
            "great_expectations": ge, "total": generic + singular + ge}


if __name__ == "__main__":
    for name, value in count_checks().items():
        print(f"{name:>20}: {value}")

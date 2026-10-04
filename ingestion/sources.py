"""Catalogue of source endpoints. Adjust endpoints / ``rename`` maps to match your real APIs."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceSpec:
    name: str                      # raw table name and S3 folder
    system: str                    # "marketing" or "crm"
    endpoint: str
    rename: dict[str, str] = field(default_factory=dict)  # api_field -> raw column


SOURCES: list[SourceSpec] = [
    SourceSpec("campaigns", "marketing", "/v1/campaigns"),
    SourceSpec("ad_performance", "marketing", "/v1/ad-performance"),
    SourceSpec("customers", "crm", "/v1/contacts"),
    SourceSpec("orders", "crm", "/v1/orders"),
]

SOURCES_BY_NAME = {s.name: s for s in SOURCES}

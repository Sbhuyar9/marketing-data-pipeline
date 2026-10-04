"""Small REST client with retries, timeouts and page-based pagination."""
from __future__ import annotations

from typing import Any, Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ApiClient:
    """Expects list endpoints to return ``{"data": [...], "next_page": <int | null>}``."""

    def __init__(self, base_url: str, token: str | None = None, timeout: float = 30,
                 max_retries: int = 5, backoff: float = 0.5) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retry = Retry(
            total=max_retries,
            backoff_factor=backoff,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            respect_retry_after_header=True,
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.headers["Accept"] = "application/json"
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}{path}", params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def paginate(self, path: str, page_size: int = 500,
                 params: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
        page: int | None = 1
        while page:
            payload = self.get(path, {**(params or {}), "page": page, "per_page": page_size})
            yield from payload["data"]
            page = payload.get("next_page")

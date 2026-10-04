"""A tiny paginated REST API (stdlib only) serving the synthetic dataset.

Lets the real ingestion code path run end-to-end with no external accounts:
    python -m ingestion.mock_api --port 8000
"""
from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .sample_data import generate_dataset

ROUTES = {
    "/v1/campaigns": "campaigns",
    "/v1/ad-performance": "ad_performance",
    "/v1/contacts": "customers",
    "/v1/orders": "orders",
}


class _Handler(BaseHTTPRequestHandler):
    dataset: dict[str, list[dict[str, Any]]] = {}
    token: str | None = None

    def do_GET(self) -> None:  # noqa: N802
        if self.token and self.headers.get("Authorization") != f"Bearer {self.token}":
            return self._send(401, {"error": "unauthorized"})
        parsed = urlparse(self.path)
        key = ROUTES.get(parsed.path)
        if key is None:
            return self._send(404, {"error": "not found"})
        query = parse_qs(parsed.query)
        try:
            page = max(int(query.get("page", ["1"])[0]), 1)
            per_page = min(max(int(query.get("per_page", ["100"])[0]), 1), 1000)
        except ValueError:
            return self._send(400, {"error": "page and per_page must be integers"})
        rows = self.dataset[key]
        start = (page - 1) * per_page
        self._send(200, {
            "data": rows[start:start + per_page],
            "page": page,
            "next_page": page + 1 if start + per_page < len(rows) else None,
            "total": len(rows),
        })

    def _send(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args: Any) -> None:  # silence request logging
        pass


def make_server(dataset: dict[str, list[dict[str, Any]]], host: str = "127.0.0.1",
                port: int = 0, token: str | None = None) -> ThreadingHTTPServer:
    handler = type("Handler", (_Handler,), {"dataset": dataset, "token": token})
    return ThreadingHTTPServer((host, port), handler)


def start_in_thread(dataset: dict[str, list[dict[str, Any]]] | None = None,
                    token: str | None = None) -> tuple[ThreadingHTTPServer, str]:
    server = make_server(dataset or generate_dataset(), token=token)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address[:2]
    return server, f"http://{host}:{port}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    srv = make_server(generate_dataset(seed=args.seed), port=args.port)
    print(f"Mock API listening on http://127.0.0.1:{args.port}")
    srv.serve_forever()

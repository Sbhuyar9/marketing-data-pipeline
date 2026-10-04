from __future__ import annotations

from typing import Iterator

from .api_client import ApiClient
from .sources import SourceSpec


def extract(spec: SourceSpec, client: ApiClient) -> Iterator[dict]:
    """Stream every record of a source, applying the optional column renames."""
    for record in client.paginate(spec.endpoint):
        if spec.rename:
            record = {spec.rename.get(k, k): v for k, v in record.items()}
        yield record

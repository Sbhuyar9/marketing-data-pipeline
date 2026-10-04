from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterable


def write_ndjson(records: Iterable[dict], path: str | Path, compress: bool = False) -> int:
    """Write records as newline-delimited JSON. Returns the number of rows written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if compress else open
    count = 0
    with opener(path, "wt", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, default=str) + "\n")
            count += 1
    return count

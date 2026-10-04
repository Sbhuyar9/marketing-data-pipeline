import gzip
import json

from ingestion.writer import write_ndjson


def test_ndjson_roundtrip(tmp_path):
    rows = [{"a": 1, "b": None}, {"a": 2, "b": "x"}]
    path = tmp_path / "out" / "rows.ndjson"
    assert write_ndjson(rows, path) == 2
    assert [json.loads(line) for line in path.read_text().splitlines()] == rows


def test_gzip(tmp_path):
    path = tmp_path / "rows.ndjson.gz"
    write_ndjson([{"a": 1}], path, compress=True)
    with gzip.open(path, "rt") as fh:
        assert json.loads(fh.readline()) == {"a": 1}

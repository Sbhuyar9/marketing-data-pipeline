import pytest
import requests

from ingestion.api_client import ApiClient
from ingestion.extract import extract
from ingestion.mock_api import start_in_thread
from ingestion.sample_data import generate_dataset
from ingestion.sources import SOURCES, SourceSpec


@pytest.fixture(scope="module")
def mock_api():
    dataset = generate_dataset()
    server, url = start_in_thread(dataset, token="secret")
    yield dataset, url
    server.shutdown()


def test_paginates_every_record(mock_api):
    dataset, url = mock_api
    client = ApiClient(url, token="secret")
    for spec in SOURCES:
        rows = list(extract(spec, ApiClient(url, token="secret")))
        assert len(rows) == len(dataset[spec.name]), spec.name
    # small page size forces several round trips
    paged = list(client.paginate("/v1/orders", page_size=37))
    assert len(paged) == len(dataset["orders"])


def test_rejects_bad_token(mock_api):
    _, url = mock_api
    with pytest.raises(requests.HTTPError):
        ApiClient(url, token="wrong", max_retries=0).get("/v1/campaigns")


def test_rename_map(mock_api):
    _, url = mock_api
    spec = SourceSpec("campaigns", "marketing", "/v1/campaigns", rename={"campaign_id": "id"})
    first = next(iter(extract(spec, ApiClient(url, token="secret"))))
    assert "id" in first and "campaign_id" not in first

"""Tests for json_client/client.py"""

from manexp_web_lists.json_client.client import JsonClient
from manexp_web_lists.taxa.models.varieties import Varieties


def test_download(tmp_path):
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    file_path = tmp_path / "crops.json"

    client = JsonClient()
    client.download_file(url, file_path)

    assert file_path.exists()
    assert file_path.stat().st_size > 0


def test_load_file(tmp_path):
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    file_path = tmp_path / "crops.json"

    client = JsonClient()
    client.download_file(url, file_path)

    varieties = client.load_file(file_path, Varieties)

    assert varieties is not None
    assert len(varieties.varieties) > 0.0

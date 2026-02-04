from manexp_web_lists.crops.models.varieties import Varieties
from manexp_web_lists.json_client.client import JsonClient


def test_download(tmp_path):
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    file_path = tmp_path / "crops.json"

    client = JsonClient(url, file_path)
    client.download_file()

    assert file_path.exists()
    assert file_path.stat().st_size > 0


def test_load_file(tmp_path):
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    file_path = tmp_path / "crops.json"

    client = JsonClient(url, file_path)
    client.download_file()

    varieties = client.load_file(Varieties)

    assert varieties is not None
    assert len(varieties.varieties) > 0.0

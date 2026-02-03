from manexp_web_lists.client import DownloadJsonClient


def test_download(tmp_path):
    url = "https://raw.githubusercontent.com/blw-ofag-ufag/blw-ogd-data/refs/heads/main/data/plant_varieties_in_switzerland.json"
    file_path = tmp_path / "plant_varieties.json"

    client = DownloadJsonClient(url, file_path)
    client.download_file()

    assert file_path.exists()
    assert file_path.stat().st_size > 0

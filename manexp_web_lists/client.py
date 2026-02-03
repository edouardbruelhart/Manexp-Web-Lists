import json
from pathlib import Path

import requests


class DownloadJsonClient:
    """Client to download and validate JSON files."""

    def __init__(self, url: str, file_path: str | Path):
        self.url = url
        self.file_path = Path(file_path)

    def download_file(self) -> None:
        response = requests.get(self.url, timeout=30)
        response.raise_for_status()

        data = response.text
        self.file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

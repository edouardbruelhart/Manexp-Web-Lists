import json
from pathlib import Path

import requests

from manexp_web_lists.models import Variety


class JsonClient:
    """Client to manage JSON files."""

    def __init__(self, url: str, file_path: str | Path):
        self.url = url
        self.file_path = Path(file_path)

    def download_file(self) -> None:
        response = requests.get(self.url, timeout=30)
        response.raise_for_status()

        # Decode bytes and strip BOM if present
        text = response.content.decode("utf-8-sig")

        # Parse & re-serialize to guarantee valid JSON
        parsed = json.loads(text)

        self.file_path.write_text(
            json.dumps(parsed, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_file(self) -> Variety:
        if not self.file_path.exists():
            raise FileNotFoundError(self.file_path)

        with self.file_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        return Variety.model_validate(data.get("varieties")[0])

        # print(type(data))

        # VarietiesResponse.model_validate(data)

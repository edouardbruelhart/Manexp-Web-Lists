import json
from pathlib import Path

import requests
from pydantic import BaseModel, ValidationError

from manexp_web_lists.json_client.errors import InvalidJson, JsonNotFound
from manexp_web_lists.json_client.types import Structure


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

    def load_file(self, structure: Structure) -> BaseModel:
        if not self.file_path.exists():
            raise JsonNotFound(self.file_path)

        with self.file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        try:
            return structure.model_validate(data)
        except ValidationError:
            raise InvalidJson(self.file_path, structure) from None

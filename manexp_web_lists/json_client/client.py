import json
from pathlib import Path
from typing import TypeVar

import requests
from pydantic import BaseModel, ValidationError

from manexp_web_lists.exceptions.invalid_json_exception import InvalidJsonException
from manexp_web_lists.exceptions.json_not_found_exception import JsonNotFoundException

T = TypeVar("T", bound=BaseModel)


class JsonClient:
    """Client to manage JSON files."""

    def download_file(self, url: str, file_path: Path) -> None:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Decode bytes and strip BOM if present
        text = response.content.decode("utf-8-sig")

        # Parse & re-serialize to guarantee valid JSON
        parsed = json.loads(text)

        file_path.write_text(
            json.dumps(parsed, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_file(self, file_path: Path, structure: type[T]) -> T:
        if not file_path.exists():
            raise JsonNotFoundException(file_path)

        json_str = file_path.read_text(encoding="utf-8")

        # Safest: parse JSON string to dict first
        data = json.loads(json_str)

        # Then validate the dict
        try:
            return structure.model_validate(data)
        except ValidationError as e:
            raise InvalidJsonException(file_path, structure) from e

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
        """Download a json file from the internet."""
        # Create session
        session = requests.Session()

        # Request
        response = session.get(url)
        response.raise_for_status()

        # Decode bytes and strip BOM if present
        text = response.content.decode("utf-8-sig")

        # Parse & re-serialize to guarantee valid JSON
        parsed = json.loads(text)

        # Write file in storage
        file_path.write_text(
            json.dumps(parsed, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_file(self, file_path: Path, structure: type[T]) -> T:
        """Safely load json file from memory using given structure"""

        # Throws an exception if file doesn't exist
        if not file_path.exists():
            raise JsonNotFoundException(file_path)

        # Read file
        json_str = file_path.read_text(encoding="utf-8")

        # Parse JSON string to dict
        data = json.loads(json_str)

        # Validate the dict with given structure
        try:
            return structure.model_validate(data)
        except ValidationError as e:
            raise InvalidJsonException(file_path, structure) from e

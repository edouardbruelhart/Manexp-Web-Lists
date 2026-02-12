import json
import logging
from pathlib import Path
from typing import TypeVar

import requests
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Initialize logger
logger = logging.getLogger(__name__)


class JsonClient:
    """Client to manage JSON files."""

    def download_file(self, url: str, file_path: Path) -> None:
        """Download a json file from the internet."""

        # Request
        with requests.Session() as session:
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

        # Read file
        json_str = file_path.read_text(encoding="utf-8")

        # Parse JSON string to dict
        data = json.loads(json_str)

        # Validate the dict with given structure
        return structure.model_validate(data)

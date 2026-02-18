import json
import logging
from pathlib import Path
from typing import TypeVar

import requests
from pydantic import BaseModel

Structure = TypeVar("Structure", bound=BaseModel)

# Initialize logger
logger = logging.getLogger(__name__)


class JsonClient:
    """Client to manage JSON files"""

    def download_file(self, url: str, file_path: Path) -> None:
        """
        Download a json file from the internet.

        Args:
            url: The url of the JSON to download
            file_path: the path where to save the file
        """

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

    def load_file(self, file_path: Path, structure: type[Structure]) -> Structure:
        """
        Safely load json file from memory using given structure

        Args:
            file_path: The path where the file is stored
            structure: The pydantic structure that matches the file content

        Returns:
            Structure: An instance of the pydantic structure representing the file structure
        """

        # Read file
        json_str = file_path.read_text(encoding="utf-8")

        # Parse JSON string to dict
        data = json.loads(json_str)

        # Validate the dict with given structure
        return structure.model_validate(data)

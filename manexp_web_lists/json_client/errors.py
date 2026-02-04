from pathlib import Path

from pydantic import ValidationError

from manexp_web_lists.json_client.types import Structure


class JsonNotFound(FileNotFoundError):
    def __init__(self, path: Path):
        self.path = path
        super().__init__(path)

    def __str__(self) -> str:
        return f"Json not found at {self.path}"


class InvalidJson(ValidationError):
    def __init__(self, path: Path, structure: Structure):
        self.path = path
        self.structure = structure
        super().__init__(path)

    def __str__(self) -> str:
        return f"Json at {self.path} is not validated by {self.structure.__class__.__name__}. For more details, see the validation errors."

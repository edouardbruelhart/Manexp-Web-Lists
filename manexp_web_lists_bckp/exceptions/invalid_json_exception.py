from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class InvalidJsonException(Exception):
    def __init__(self, path: Path, structure: type[T]):
        self.path = path
        self.structure = structure
        super().__init__(path)

    def __str__(self) -> str:
        return f"Json at {self.path} is not validated by {self.structure.__name__} structure. For more details, see the validation errors."

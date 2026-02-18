from pathlib import Path


class JsonNotFoundException(FileNotFoundError):
    def __init__(self, path: Path):
        self.path = path
        super().__init__(path)

    def __str__(self) -> str:
        return f"Json not found at {self.path}"

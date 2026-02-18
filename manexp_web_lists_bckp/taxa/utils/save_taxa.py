from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def save_taxa(taxa: BaseModel, path: Path) -> None:
    path.write_text(
        taxa.model_dump_json(
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

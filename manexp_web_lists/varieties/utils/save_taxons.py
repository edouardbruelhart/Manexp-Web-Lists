from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def save_taxons(taxons: BaseModel, path: Path) -> None:
    path.write_text(
        taxons.model_dump_json(
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

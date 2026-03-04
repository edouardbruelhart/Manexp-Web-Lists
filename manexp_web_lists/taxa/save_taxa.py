import json
from pathlib import Path

from pydantic import BaseModel


def save_taxa(taxa: BaseModel, path: Path) -> None:
    """
    Save taxon list to JSON file.

    Args:
        taxa: Taxon list to save
        path: Path where to save the JSON file
    """

    data = taxa.model_dump()

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

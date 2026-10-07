from pathlib import Path

import polars as pl


def create_register_subtypes(seeds_path: Path) -> None:
    """
    Create register subtypes table.

    Args:
        seeds_path: The path to the register subtype file.
    """

    rows = []

    rows.append({
        "id": 1,
        "name": "Agricultural",
        "abbreviation": "AGR",
        "description": "Agricultural plant species register.",
    })

    rows.append({
        "id": 2,
        "name": "Vegetable",
        "abbreviation": "VEG",
        "description": "Vegetable species register.",
    })

    rows.append({
        "id": 3,
        "name": "Fruit",
        "abbreviation": "FRU",
        "description": "Fruit genera and species register.",
    })

    register_subtypes = pl.DataFrame(rows)

    register_subtypes.write_parquet(seeds_path)

import polars as pl
from polars import DataFrame


def create_register_subtypes() -> DataFrame:
    """
    Create register subtypes table.

    Returns:
        DataFrame: The registre subtypes dataframe
    """

    rows = []

    rows.append({
        "name": "Agricultural",
        "abbreviation": "AGR",
        "description": "Agricultural plant species register.",
    })

    rows.append({
        "name": "Vegetable",
        "abbreviation": "VEG",
        "description": "Vegetable species register.",
    })

    rows.append({
        "name": "Fruit",
        "abbreviation": "FRU",
        "description": "Fruit genera and species register.",
    })

    register_subtypes = pl.DataFrame(rows)

    return register_subtypes

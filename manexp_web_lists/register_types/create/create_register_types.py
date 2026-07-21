import polars as pl
from polars import DataFrame


def create_register_types() -> DataFrame:
    """
    Create register types table.

    Returns:
        DataFrame: The registre types dataframe
    """

    rows = []

    rows.append({
        "name": "National List",
        "abbreviation": "NLI",
        "description": "Varieties eligible for marketing over a certain territory.",
    })

    rows.append({
        "name": "Commercial Registers",
        "abbreviation": "COM",
        "description": "Varieties present in a register of commercialized varieties over a certain territory.",
    })

    rows.append({
        "name": "European Union trade Mark",
        "abbreviation": "EUTM",
        "description": "Varieties registered with the European union Intellectual Property Office (EUIPO).",
    })

    rows.append({
        "name": "Frumatis",
        "abbreviation": "FRU",
        "description": "Varieties registered in the Fruit Reproductive Material Information System (FRUMATIS).",
    })

    rows.append({
        "name": "Plant Breeder's Rights",
        "abbreviation": "PBR",
        "description": "Varieties protected by plant breeders' rights for a number of years over a certain territory.",
    })

    rows.append({
        "name": "Plant Patents",
        "abbreviation": "PLP",
        "description": "Varieties protected by a patent over a certain territory.",
    })

    rows.append({
        "name": "Other",
        "abbreviation": "ZZZ",
        "description": "Varieties not covered by the existing types of registers.",
    })

    register_types = pl.DataFrame(rows)

    return register_types

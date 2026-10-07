from pathlib import Path

import polars as pl


def create_register_types(register_types_path: Path) -> None:
    """
    Create register types table.

    Args:
        register_types_path: The path to the register type file.
    """

    rows = []

    rows.append({
        "id": 1,
        "name": "National List",
        "abbreviation": "NLI",
        "description": "Varieties eligible for marketing over a certain territory.",
    })

    rows.append({
        "id": 2,
        "name": "Commercial Registers",
        "abbreviation": "COM",
        "description": "Varieties present in a register of commercialized varieties over a certain territory.",
    })

    rows.append({
        "id": 3,
        "name": "European Union trade Mark",
        "abbreviation": "EUTM",
        "description": "Varieties registered with the European union Intellectual Property Office (EUIPO).",
    })

    rows.append({
        "id": 4,
        "name": "Frumatis",
        "abbreviation": "FRU",
        "description": "Varieties registered in the Fruit Reproductive Material Information System (FRUMATIS).",
    })

    rows.append({
        "id": 5,
        "name": "Plant Breeder's Rights",
        "abbreviation": "PBR",
        "description": "Varieties protected by plant breeders' rights for a number of years over a certain territory.",
    })

    rows.append({
        "id": 6,
        "name": "Plant Patents",
        "abbreviation": "PLP",
        "description": "Varieties protected by a patent over a certain territory.",
    })

    rows.append({
        "id": 7,
        "name": "Other",
        "abbreviation": "ZZZ",
        "description": "Varieties not covered by the existing types of registers.",
    })

    register_types = pl.DataFrame(rows)

    register_types.write_parquet(register_types_path)

from pathlib import Path

import polars as pl

from .parsers import indications_parser

RELATIONSHIP_COLUMNS = [
    "measure",
    "time_measure",
    "application_area",
    "application_comment",
    "culture",
    "culture_form",
    "pest",
    "obligation",
]


def clean_indications(phyto_path: Path) -> None:
    """
    Clean and split indications information, rename columns and write them as parquet files

    Args:
        phyto_path: The path to the folder containing the phyto lists
    """

    # Load data
    indications = indications_parser(phyto_path / "indications.xml")

    # Get indications direct children columns
    indication_columns = [col for col in indications.columns if col not in RELATIONSHIP_COLUMNS]

    # Create the indications children table
    indication_children = indications.select(indication_columns)

    indication_children.write_parquet(phyto_path / "indications.parquet")

    for relationship in RELATIONSHIP_COLUMNS:
        relation_table = (
            indications
            .select(
                pl.col("id").alias("indication"),
                pl.col(relationship),
            )
            .explode(relationship, empty_as_null=True)
            .drop_nulls(relationship)
        )

        if relationship == "culture":
            relation_table = relation_table.with_columns(
                pl.col(relationship).struct.field("id").alias("culture"),
                pl.col(relationship).struct.field("additional_text"),
            ).drop_nulls(relationship)

        elif relationship == "pest":
            relation_table = relation_table.with_columns(
                pl.col(relationship).struct.field("id").alias("pest"),
                pl.col(relationship).struct.field("additional_text"),
                pl.col(relationship).struct.field("type"),
            ).drop_nulls(relationship)

        relation_table = relation_table.unique()

        relation_table.write_parquet(phyto_path / f"indication_{relationship}.parquet")

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

    # Transform numeric strings into int and float
    indication_children = indication_children.with_columns(
        pl.col("dosage_from").cast(pl.Float64, strict=False),
        pl.col("dosage_to").cast(pl.Float64, strict=False),
        pl.col("waiting_period").cast(pl.Int64, strict=False),
        pl.col("expenditure_from").cast(pl.Float64, strict=False),
        pl.col("expenditure_to").cast(pl.Float64, strict=False),
    )

    indication_children.write_parquet(phyto_path / "indication.parquet")

    for relationship in RELATIONSHIP_COLUMNS:
        relationship_id = relationship + "_id"

        relation_table = (
            indications
            .select(
                pl.col("id").alias("indication_id"),
                pl.col(relationship).alias(relationship_id),
            )
            .explode(relationship_id, empty_as_null=True)
            .drop_nulls(relationship_id)
        )

        if relationship == "culture":
            relation_table = relation_table.with_columns(
                pl.col(relationship_id).struct.field("id").alias("culture_id"),
                pl.col(relationship_id).struct.field("additional_text").alias("culture_additional_text_id"),
            ).drop_nulls(relationship_id)

        elif relationship == "pest":
            relation_table = relation_table.with_columns(
                pl.col(relationship_id).struct.field("id").alias("pest_id"),
                pl.col(relationship_id).struct.field("additional_text").alias("pest_additional_text_id"),
                pl.col(relationship_id).struct.field("type"),
            ).drop_nulls(relationship_id)

        relation_table = relation_table.unique()

        relation_table.write_parquet(phyto_path / f"indication_{relationship}.parquet")

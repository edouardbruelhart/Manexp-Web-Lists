from pathlib import Path

import polars as pl

from .parsers import products_parser

RELATIONSHIP_COLUMNS = [
    "product_category",
    "formulation_code",
    "danger_symbol",
    "signal_word",
    "s_code",
    "r_code",
    "indication",
]


def clean_products(phyto_path: Path) -> None:
    """
    Clean and split products information, rename columns and write them as parquet files

    Args:
        phyto_path: The path to the folder containing the phyto lists
    """

    # Load data
    products = products_parser(phyto_path / "cleaned_products.xml")

    # Get products direct children columns
    product_columns = [col for col in products.columns if col not in RELATIONSHIP_COLUMNS]

    # Create the products children table
    product_children = products.select(product_columns)

    # Convert date strings to dates
    product_children = product_children.with_columns(
        pl
        .col("soldout_deadline")
        .str.to_datetime(
            format="%Y-%m-%d %H:%M:%S%.f",
            strict=False,
        )
        .dt.date()
        .alias("soldout_deadline"),
        pl
        .col("exhaustion_deadline")
        .str.to_datetime(
            format="%Y-%m-%d %H:%M:%S%.f",
            strict=False,
        )
        .dt.date(),
    )

    product_children.write_parquet(phyto_path / "products.parquet")

    for relationship in RELATIONSHIP_COLUMNS:
        relation_table = (
            products
            .select(
                pl.col("id").alias("product"),
                pl.col(relationship),
            )
            .explode(relationship, empty_as_null=True)
            .drop_nulls(relationship)
            .unique()
        )

        relation_table.write_parquet(phyto_path / f"product_{relationship}.parquet")

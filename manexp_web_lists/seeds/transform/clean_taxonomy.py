import polars as pl
from polars import DataFrame

from manexp_web_lists.clients.gbif_client import parse_with_gbif


def clean_taxonomy(taxonomy: DataFrame) -> DataFrame:
    """
    Clean the official UPOV taxonomy list.

    Args:
        taxonomy: The taxonomy list in polars dataframe

    Returns:
        DataFrame: The cleaned taxonomy list
    """

    cleaned_taxonomy = (
        taxonomy
        .with_columns(
            parsed=(
                pl.col("botanical_name").map_elements(
                    parse_with_gbif,
                    return_dtype=pl.Struct({
                        "focal_name": pl.String,
                        "genus": pl.String,
                        "rank": pl.String,
                        "parsed": pl.Boolean,
                    }),
                    skip_nulls=False,
                )
            )
        )
        .unnest("parsed")
        .drop("botanical_name")
    )

    return cleaned_taxonomy

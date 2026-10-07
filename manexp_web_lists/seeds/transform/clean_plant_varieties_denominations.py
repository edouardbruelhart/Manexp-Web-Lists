import polars as pl
from polars import DataFrame

from manexp_web_lists.core import parse_strings_to_list

NAME_COLUMNS = [
    "denomination",
    "conventional_denomination",
    "denomination_synonym",
    "trade_name",
]

DENOMINATION_FALLBACK_COLUMNS = NAME_COLUMNS.copy()
DENOMINATION_FALLBACK_COLUMNS.remove("denomination_synonym")


def aggregate_denominations(plant_varieties: DataFrame) -> DataFrame:
    """
    Clean and aggregate variety denominations in the official european plant varieties list.

    Args:
        plant_varieties: The plant varieties list in polars dataframe

    Returns:
        DataFrame: The plant varieties list with cleaned and aggregated denominations in polars dataframe
    """

    aggregated_denominations = (
        plant_varieties
        .with_columns(
            # Put alltogether
            pl
            .concat_list([pl.col(col) for col in NAME_COLUMNS])
            # Remove nulls
            .list.drop_nulls()
            # Clean each denomination
            .list.eval(pl.element().str.strip_chars().str.replace_all(r"\s+", " "))
            # Remove duplicates
            .list.unique(maintain_order=True)
            # Create a new column
            .alias("denomination_search")
        )
        # Create the synonyms column by removing the first denomination (the main one) from the list of denominations
        .with_columns(pl.col("denomination_search").list.slice(1).alias("synonyms"))
        # Drop the original denomination columns
        .drop([
            "conventional_denomination",
            "denomination_synonym",
            "trade_name",
        ])
    )

    return aggregated_denominations


def clean_plant_varieties_denominations(plant_varieties: DataFrame) -> DataFrame:
    """
    Clean and aggregate variety denominations in the official european seeds list.

    Args:
        plant_varieties: The plant varieties list in polars dataframe

    Returns:
        DataFrame: The plant varieties list with cleaned and aggregated denominations
    """

    cleaned_denominations = (
        plant_varieties
        .with_columns([pl.col(col).str.strip_chars().str.replace_all(r"\s+", " ").alias(col) for col in NAME_COLUMNS])
        .with_columns(denomination=pl.coalesce(*DENOMINATION_FALLBACK_COLUMNS))
        .drop_nulls("denomination")
    )

    parsed_synonyms = cleaned_denominations.with_columns(
        pl
        .col("denomination_synonym")
        .map_elements(
            parse_strings_to_list,
            return_dtype=pl.List(pl.String),
        )
        .fill_null(pl.lit([], dtype=pl.List(pl.String)))
    )

    return aggregate_denominations(parsed_synonyms)

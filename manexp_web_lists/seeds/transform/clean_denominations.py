import re

import polars as pl
from polars import DataFrame

NAME_COLUMNS = [
    "denomination",
    "conventional_denomination",
    "denomination_synonym",
    "trade_name",
]

DENOMINATION_FALLBACK_COLUMNS = NAME_COLUMNS.copy()
DENOMINATION_FALLBACK_COLUMNS.remove("denomination_synonym")

SEPARATORS = {
    "/",
    ",",
    "+",
}


def parse_synonyms(text: str | None) -> list[str] | None:
    """
    Parse synonyms from a string into a list of strings.

    Args:
        text: The string to parse

    Returns:
        list[str] | None: The list of synonyms
    """

    if not text:
        return None

    # Protect numeric slashes as these are not separators but part of the denomination
    text = re.sub(r"(\d)//(\d)", r"\1§DOUBLE_SLASH§\2", text)
    text = re.sub(r"(\d)/(\d)", r"\1§SLASH§\2", text)

    # Replace every separator by ';'
    for sep in SEPARATORS:
        text = text.replace(sep, ";")

    # Restore protected slashes
    text = text.replace("§DOUBLE_SLASH§", "//").replace("§SLASH§", "/")

    # Split into list
    result = []

    for name in text.split(";"):
        if name:
            result.append(name)

    return result


def aggregate_denominations(seeds: DataFrame) -> DataFrame:
    """
    Clean and aggregate variety denominations in the official european seeds list.

    Args:
        seeds: The seeds list in polars dataframe
    Returns:
        DataFrame: The seeds list with cleaned and aggregated denominations
    """

    aggregated_denominations = (
        seeds
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


def clean_denominations(seeds: DataFrame) -> DataFrame:
    """
    Clean and aggregate variety denominations in the official european seeds list.

    Args:
        seeds: The seeds list in polars dataframe

    Returns:
        DataFrame: The seeds list with cleaned and aggregated denominations
    """

    cleaned_denominations = (
        seeds
        .with_columns([pl.col(col).str.strip_chars().str.replace_all(r"\s+", " ").alias(col) for col in NAME_COLUMNS])
        .with_columns(denomination=pl.coalesce(*DENOMINATION_FALLBACK_COLUMNS))
        .drop_nulls("denomination")
    )

    parsed_synonyms = cleaned_denominations.with_columns(
        pl
        .col("denomination_synonym")
        .map_elements(
            parse_synonyms,
            return_dtype=pl.List(pl.String),
        )
        .fill_null(pl.lit([], dtype=pl.List(pl.String)))
    )

    return aggregate_denominations(parsed_synonyms)

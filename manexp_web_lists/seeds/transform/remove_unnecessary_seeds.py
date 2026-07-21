import polars as pl
from polars import DataFrame


def remove_unnecessary_seeds(seeds: DataFrame) -> DataFrame:
    """
    Remove withdrawn and rejected seeds from the list.

    Args:
        seeds: The seeds list in polars dataframe

    Returns:
        DataFrame: The filtered seeds list
    """

    removed_seeds = seeds.filter(~pl.col("status").is_in(["Withdrawn", "Rejected"]))

    return removed_seeds

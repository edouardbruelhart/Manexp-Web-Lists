import polars as pl
from polars import DataFrame

from manexp_web_lists.seeds.get_seeds import CLEAN_PARQUET_PATH as SEEDS_PARQUET_PATH


def filter_rows(taxonomy: DataFrame) -> DataFrame:
    """
    Remove unwanted rows from the official UPOV taxonomy list.

    Args:
        taxonomy: The taxonomy list in polars dataframe

    Returns:
        DataFrame: The filtered taxonomy list
    """

    # First load the seeds list
    seeds = pl.read_parquet(SEEDS_PARQUET_PATH)

    # Then get a list of used UPOV codes in the seeds list
    unique_codes = seeds.select(pl.col("upov_code").unique())

    # Finally filter the taxonomy list to keep only the used UPOV codes
    filtered_taxonomy = taxonomy.join(unique_codes, on="upov_code", how="right")

    return filtered_taxonomy

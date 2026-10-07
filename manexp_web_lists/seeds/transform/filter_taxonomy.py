from pathlib import Path

import polars as pl
from polars import DataFrame


def filter_taxonomy(taxonomy: pl.DataFrame, plant_varieties_path: Path) -> DataFrame:
    """
    Remove unwanted columns and fields from the official UPOV taxonomy list.

    Args:
        taxonomy: The taxonomy list in polars dataframe
        plant_varieties_path: Path to the plant varieties list

    Returns:
        DataFrame: The filtered taxonomy list
    """

    # Get only needed columns
    filtered_columns = taxonomy.select("upov_code", "botanical_name")

    # load plant varieties list
    plant_varieties_list = pl.read_parquet(plant_varieties_path)

    # Then get a list of used UPOV codes in the seeds list
    unique_codes = plant_varieties_list.select(pl.col("taxon_id").alias("upov_code").unique())

    # Finally filter the taxonomy list to keep only the used UPOV codes
    filtered_taxonomy = filtered_columns.join(unique_codes, on="upov_code", how="right")

    return filtered_taxonomy

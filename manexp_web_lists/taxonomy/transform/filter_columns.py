from polars import DataFrame


def filter_columns(taxonomy: DataFrame) -> DataFrame:
    """
    Remove unwanted fields from the official UPOV taxonomy list.

    Args:
        taxonomy: The taxonomy list in polars dataframe

    Returns:
        DataFrame: The filtered taxonomy list
    """
    filtered_taxonomy = taxonomy.drop(
        "upov_short_code",
    )

    return filtered_taxonomy

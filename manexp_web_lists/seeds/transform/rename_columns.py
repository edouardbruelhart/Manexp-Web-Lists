from polars import DataFrame

COLUMNS_TO_RENAME = {
    "Country / Org.": "country",
    "Register Type": "register_type",
    "Register Subtype": "register_subtype",
    "UPOV Species Code": "upov_code",
    "Variety Denomination": "denomination",
    "Variety Status": "status",
    "GMO": "is_gmo",
    "Variety Denomination Synonym(s)": "denomination_synonym",
    "Conventional Denomination": "conventional_denomination",
    "Variety Trade Name(s)": "trade_name",
    "Hybrid": "is_hybrid",
    "Organic": "is_organic",
    "UUID": "uuid",
}


def rename_columns(seeds: DataFrame) -> DataFrame:
    """
    Rename fields from the official european seeds list.

    Args:
        seeds: The seeds list in polars dataframe

    Returns:
        DataFrame: The seeds list with renamed columns
    """
    renamed_seeds = seeds.rename(COLUMNS_TO_RENAME)

    return renamed_seeds

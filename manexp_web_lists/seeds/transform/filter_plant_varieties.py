import polars as pl
from polars import DataFrame

COLUMNS = {
    "Country / Org.": "country",
    "Register Type": "register_type",
    "Register Subtype": "register_subtype",
    "UPOV Species Code": "taxon_id",
    "Variety Denomination": "denomination",
    "Variety Status": "status",
    "GMO": "is_gmo",
    "Variety Denomination Synonym(s)": "denomination_synonym",
    "Conventional Denomination": "conventional_denomination",
    "Variety Trade Name(s)": "trade_name",
    "Hybrid": "is_hybrid",
    "Organic": "is_organic",
    "UUID": "id",
}


def filter_plant_varieties(plant_varieties: DataFrame) -> DataFrame:
    """
    Filter the official european plant varieties list and rename columns.

    Args:
        plant_varieties: The plant varieties list in polars dataframe

    Returns:
        DataFrame: The filtered plant varieties list
    """

    # Get only the needed columns
    filtered_columns = plant_varieties.select(COLUMNS.keys())

    # Rename the columns
    renamed_columns = filtered_columns.rename(COLUMNS)

    # Remove useless plant varieties
    shortened_plant_varieties = renamed_columns.filter(~pl.col("status").is_in(["Withdrawn", "Rejected"]))

    return shortened_plant_varieties

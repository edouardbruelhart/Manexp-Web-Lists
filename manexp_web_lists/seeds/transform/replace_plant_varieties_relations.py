import polars as pl
from polars import DataFrame


def replace_plant_varieties_relations(
    plant_varieties: DataFrame, countries: DataFrame, register_types: DataFrame, register_subtypes: DataFrame
) -> DataFrame:
    """
    Replace countries, register types, and register subtypes references in the plant varieties list.

    Args:
        plant_varieties: DataFrame containing the phytosanitary products list.
        countries: DataFrame containing country information.
        register_types: DataFrame containing register type information.
        register_subtypes: DataFrame containing register subtype information.

    Returns:
        DataFrame: The plant varieties list with updated country, register type, and register subtype references.
    """

    # Replace alpha2 code by country id
    plant_varieties = plant_varieties.join(
        countries.select(
            pl.col("alpha2").alias("country"),
            pl.col("id").alias("country_id"),
        ),
        on="country",
        how="left",
    ).drop("country")

    # Replace abbreviation by register type id
    plant_varieties = plant_varieties.join(
        register_types.select(
            pl.col("abbreviation").alias("register_type"),
            pl.col("id").alias("register_type_id"),
        ),
        on="register_type",
        how="left",
    ).drop("register_type")

    # Replace abbreviation by register subtype id
    plant_varieties = plant_varieties.join(
        register_subtypes.select(
            pl.col("abbreviation").alias("register_subtype"),
            pl.col("id").alias("register_subtype_id"),
        ),
        on="register_subtype",
        how="left",
    ).drop("register_subtype")

    return plant_varieties

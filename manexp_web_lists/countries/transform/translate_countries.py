import polars as pl
from babel import Locale
from polars import DataFrame


def translate_countries(countries: DataFrame) -> DataFrame:
    """
    Add french, german and italian translations to countries list.

    Args:
        countries: The countries list in polars dataframe
    Returns:
        DataFrame: The countries list with translations
    """

    fr = Locale("fr")
    de = Locale("de")
    it = Locale("it")
    en = Locale("en")

    translated_countries = countries.with_columns(
        pl
        .col("alpha2")
        .map_elements(
            lambda code: fr.territories.get(code),
            return_dtype=pl.String,
        )
        .alias("french_name"),
        pl
        .col("alpha2")
        .map_elements(
            lambda code: de.territories.get(code),
            return_dtype=pl.String,
        )
        .alias("german_name"),
        pl
        .col("alpha2")
        .map_elements(
            lambda code: it.territories.get(code),
            return_dtype=pl.String,
        )
        .alias("italian_name"),
        pl
        .col("alpha2")
        .map_elements(
            lambda code: en.territories.get(code),
            return_dtype=pl.String,
        )
        .alias("english_name"),
    )

    return translated_countries

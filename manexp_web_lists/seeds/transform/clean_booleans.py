import polars as pl
from polars import DataFrame

from manexp_web_lists.exceptions import InvalidPseudoBoolError

BOOLEAN_COLUMNS = ["is_gmo", "is_hybrid", "is_organic"]

TRUE_VALUES = {"Y", "Yes"}

FALSE_VALUES = {"N", "No", ""}


def convert_pseudo_bool_to_bool(pseudo_bool: str) -> bool:
    """
    Transform pseudo booleans to booleans

    Args:
        pseudo_bool: The string to convert to boolean

    Returns:
        bool: The corresponding boolean

    Raises:
        InvalidPseudoBoolError: Raised whan the pseudo boolean is not supported by the function
    """

    # Make pipeline crash if a new, unhandled pseudo boolean is met
    if pseudo_bool not in TRUE_VALUES and pseudo_bool not in FALSE_VALUES:
        raise InvalidPseudoBoolError(pseudo_bool)

    return pseudo_bool in TRUE_VALUES


def clean_booleans(seeds: DataFrame) -> DataFrame:
    """
    Replace pseudo booleans by real booleans in the official european seeds list.

    Args:
        seeds: The seeds list in polars dataframe

    Returns:
        DataFrame: The seeds list with real booleans
    """

    boolean_seeds = seeds.with_columns([
        pl.col(col).map_elements(convert_pseudo_bool_to_bool, return_dtype=pl.Boolean) for col in BOOLEAN_COLUMNS
    ])

    return boolean_seeds

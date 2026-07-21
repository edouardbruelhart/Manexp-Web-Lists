import colorsys
import hashlib

import polars as pl
from polars import DataFrame


def color_taxonomy(taxonomy: DataFrame) -> DataFrame:
    """
    Add hexadecimal color code for each taxon to the official UPOV taxonomy list.

    Args:
        taxonomy: The taxonomy list in polars dataframe

    Returns:
        DataFrame: The colored taxonomy list
    """

    colored_taxonomy = taxonomy.with_columns(
        color=(pl.col("upov_code").map_elements(text_to_color, return_dtype=pl.String))
    )

    return colored_taxonomy


def text_to_color(text: str) -> str:
    """
    Returns always the same hexadecimal color for a given text

    Args:
        text: The text to convert to hexadecimal color

    Returns:
        str: Hexadecimal color
    """
    # Hash it
    digest = hashlib.sha256(text.encode()).digest()

    # Get hue from part of the hash
    hue = digest[0] / 255 * 360

    # Define saturation and lightness
    saturation = 0.55 + digest[1] / 255 * 0.30
    lightness = 0.40 + digest[2] / 255 * 0.20

    # Generate RGB
    r, g, b = colorsys.hls_to_rgb(hue / 360, lightness, saturation)

    # Convert RGB to hexadecimal
    hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    return hex_color

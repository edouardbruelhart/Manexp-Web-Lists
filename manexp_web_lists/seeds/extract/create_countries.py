from pathlib import Path

import polars as pl
import pycountry


def create_countries(file_path: Path) -> None:
    """
    Generate a countries parquet files from pycountry library.

    Args:
        file_path: the path where to save the file
    """

    countries = pl.DataFrame([
        {"id": c.numeric, "alpha2": c.alpha_2, "alpha3": c.alpha_3, "flag": c.flag} for c in pycountry.countries
    ]).sort("id")

    countries.write_csv(file_path)

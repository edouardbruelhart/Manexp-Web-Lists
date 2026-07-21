from pathlib import Path

import polars as pl
import pycountry


def download_countries(file_path: Path) -> None:
    """
    Download the official european seeds list as an Excel file from the internet.

    Args:
        file_path: the path where to save the file
    """

    countries = pl.DataFrame([
        {"alpha2": c.alpha_2, "alpha3": c.alpha_3, "numeric": c.numeric, "flag": c.flag} for c in pycountry.countries
    ]).sort("alpha2")

    countries.write_csv(file_path)

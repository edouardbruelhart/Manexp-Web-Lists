from pathlib import Path

import polars as pl

from .extract.download_countries import download_countries
from .transform.translate_countries import translate_countries

RAW_CSV_PATH = Path("./countries/lists/raw_countries.csv")
CLEAN_PARQUET_PATH = Path("./countries/lists/clean_countries.parquet")


def get_countries() -> None:
    """Function to fetch and enrich countries list."""

    # 1. Download raw excel
    download_countries(RAW_CSV_PATH)

    # 2. Load countries
    raw_countries = pl.read_csv(RAW_CSV_PATH)

    # 3. Add french, german and italian translations
    translated_countries = translate_countries(raw_countries)

    # 4. Save final table as parquet
    translated_countries.write_parquet(CLEAN_PARQUET_PATH)

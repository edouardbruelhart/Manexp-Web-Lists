from pathlib import Path

import polars as pl

from .extract.download_seeds import download_seeds
from .transform.clean_booleans import clean_booleans
from .transform.clean_denominations import clean_denominations
from .transform.filter_columns import filter_columns
from .transform.remove_unnecessary_seeds import remove_unnecessary_seeds
from .transform.rename_columns import rename_columns

PLANT_LIST_URL = "https://ec.europa.eu/food/plant-variety-portal/index.xhtml"
RAW_EXCEL_PATH = Path("./seeds/lists/raw_seeds.xlsx")
RAW_CSV_PATH = Path("./seeds/lists/raw_seeds.csv")
CLEAN_PARQUET_PATH = Path("./seeds/lists/cleaned_seeds.parquet")


def get_seeds() -> None:
    """Function to fetch, enrich and validate official european seeds list."""

    # 1. Download raw excel
    download_seeds(PLANT_LIST_URL, RAW_EXCEL_PATH)

    # 2. Load seeds as dataframe and save a csv version of it
    raw_seeds = pl.read_excel(RAW_EXCEL_PATH)
    raw_seeds.write_csv(RAW_CSV_PATH)

    # 3. Drop unnecessary columns
    filtered_seeds = filter_columns(raw_seeds)

    # 4. Rename columns
    renamed_seeds = rename_columns(filtered_seeds)

    # 5. Drop unnecessary seeds
    removed_seeds = remove_unnecessary_seeds(renamed_seeds)

    # 6. Replace pseudo booleans by real booleans
    boolean_seeds = clean_booleans(removed_seeds)

    # 7. Aggregate denominations
    aggregated_seeds = clean_denominations(boolean_seeds)

    # 8. Save final table as parquet
    aggregated_seeds.write_parquet(CLEAN_PARQUET_PATH)

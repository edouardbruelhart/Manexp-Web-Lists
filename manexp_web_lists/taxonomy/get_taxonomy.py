from pathlib import Path

import polars as pl

from .extract.download_taxonomy import download_taxonomy
from .transform.clean_taxonomy import clean_taxonomy
from .transform.color_taxonomy import color_taxonomy
from .transform.filter_columns import filter_columns
from .transform.filter_rows import filter_rows
from .transform.iconize_taxonomy import iconize_taxonomy

TAXONOMY_URL = "https://www.upov.int/genie/updates/upov_code.xhtml?lang=en"
RAW_CSV_PATH = Path("./taxonomy/lists/raw_taxonomy.csv")
CLEAN_PARQUET_PATH = Path("./taxonomy/lists/clean_taxonomy.csv")


def get_taxonomy() -> None:
    """Function to fetch, enrich and validate official UPOV taxonomy list."""

    # 1. Download raw taxonomy
    download_taxonomy(TAXONOMY_URL, RAW_CSV_PATH)

    # 2. Load taxonomy as dataframe
    raw_taxonomy = pl.read_csv(RAW_CSV_PATH)

    # 3. Drop unnecessary columns
    filtered_taxonomy = filter_columns(raw_taxonomy)

    # 4. Drop unnecessary rows
    shortened_taxonomy = filter_rows(filtered_taxonomy)

    # 5. Clean taxonomy
    cleaned_taxonomy = clean_taxonomy(shortened_taxonomy)

    # 6. Add icons to the taxonomy list
    iconized_taxonomy = iconize_taxonomy(cleaned_taxonomy)

    # 7. Add color to the taxon
    colored_taxonomy = color_taxonomy(iconized_taxonomy)

    # 8. Save final table as parquet
    colored_taxonomy.write_parquet(CLEAN_PARQUET_PATH)

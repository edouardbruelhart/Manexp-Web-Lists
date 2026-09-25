from pathlib import Path

import polars as pl

from .extract.download_taxonomy import download_taxonomy
from .transform.clean_taxonomy import clean_taxonomy
from .transform.color_taxonomy import color_taxonomy
from .transform.filter_columns import filter_columns
from .transform.filter_rows import filter_rows
from .transform.iconize_taxonomy import iconize_taxonomy
from .transform.merge_taxonomy import merge_taxonomy

TAXONOMY_URLS = [
    "https://www.upov.int/genie/reports/twp.xhtml?faces-redirect=true",
    "https://www.upov.int/genie/updates/upov_code.xhtml?lang=en",
]

LISTS_PATH = Path("./taxonomy/lists")
RAW_CSV_PATHS = [LISTS_PATH / "raw_taxonomy_reports.csv", LISTS_PATH / "raw_taxonomy_updates.csv"]
RAW_COLUMNS = [
    [
        "upov_code",
        "botanical_name",
        "english",
        "french",
        "german",
        "spanish",
        "agriculture",
        "fruit",
        "ornamental",
        "forest",
        "vegetable",
    ],
    [
        "upov_code",
        "botanical_name",
        "upov_short_code",
    ],
]
MERGED_CSV_PATH = LISTS_PATH / "merged_taxonomy.csv"
CLEAN_PARQUET_PATH = LISTS_PATH / "clean_taxonomy.parquet"


def get_taxonomy() -> None:
    """Function to fetch, enrich and validate official UPOV taxonomy list."""

    # Create lists path if it doesn't exist
    LISTS_PATH.mkdir(parents=True, exist_ok=True)

    # 1. Download raw taxonomy
    download_taxonomy(TAXONOMY_URLS, RAW_CSV_PATHS, RAW_COLUMNS)

    # 2. Fuse taxonomy
    merge_taxonomy(RAW_CSV_PATHS, MERGED_CSV_PATH)

    # 3. Load taxonomy as dataframe
    raw_taxonomy = pl.read_csv(MERGED_CSV_PATH)

    # 4. Drop unnecessary columns
    filtered_taxonomy = filter_columns(raw_taxonomy)

    # 5. Drop unnecessary rows
    shortened_taxonomy = filter_rows(filtered_taxonomy)

    # 6. Clean taxonomy
    cleaned_taxonomy = clean_taxonomy(shortened_taxonomy)

    # 7. Add icons to the taxonomy list
    iconized_taxonomy = iconize_taxonomy(cleaned_taxonomy)

    # 8. Add color to the taxon
    colored_taxonomy = color_taxonomy(iconized_taxonomy)

    # 9. Save final table as parquet
    colored_taxonomy.write_parquet(CLEAN_PARQUET_PATH)

from pathlib import Path

from .create.create_register_subtypes import create_register_subtypes

LISTS_PATH = Path("./register_subtypes/lists")
CLEAN_PARQUET_PATH = LISTS_PATH / "clean_register_subtypes.parquet"


def get_register_subtypes() -> None:
    """Function to generate register subtypes."""

    # Create lists path if it doesn't exist
    LISTS_PATH.mkdir(parents=True, exist_ok=True)

    # 1. Create register subtypes table
    register_subtypes = create_register_subtypes()

    # 2. Save final table as parquet
    register_subtypes.write_parquet(CLEAN_PARQUET_PATH)

from pathlib import Path

from .create.create_register_subtypes import create_register_subtypes

CLEAN_PARQUET_PATH = Path("./register_subtypes/lists/clean_register_subtypes.parquet")


def get_register_subtypes() -> None:
    """Function to generate register subtypes."""

    # 1. Create register subtypes table
    register_subtypes = create_register_subtypes()

    # 2. Save final table as parquet
    register_subtypes.write_parquet(CLEAN_PARQUET_PATH)

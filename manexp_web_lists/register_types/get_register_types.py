from pathlib import Path

from .create.create_register_types import create_register_types

LISTS_PATH = Path("./register_types/lists")
CLEAN_PARQUET_PATH = LISTS_PATH / "clean_register_types.parquet"


def get_register_types() -> None:
    """Function to generate register types."""

    # Create lists path if it doesn't exist
    LISTS_PATH.mkdir(parents=True, exist_ok=True)

    # 1. Create register types table
    register_types = create_register_types()

    # 2. Save final table as parquet
    register_types.write_parquet(CLEAN_PARQUET_PATH)

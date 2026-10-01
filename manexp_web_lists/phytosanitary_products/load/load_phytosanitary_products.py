import os
from pathlib import Path

from .apply_schema import apply_schema
from .generate_schema import generate_schema


def load_phytosanitary_products(lists_path: Path) -> None:
    """
    Load phytosanitary products in PostgreSQL from a list of Parquet files.

    Args:
        lists_path: The path to Parquet files folder
    """

    DATABASE_URL = (
        f"postgresql://"
        f"{os.getenv('POSTGRES_PIPELINE_USER')}:"
        f"{os.getenv('POSTGRES_PIPELINE_PASSWORD')}@"
        "127.0.0.1:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    schema_path = lists_path / "schema.sql"

    generate_schema(lists_path, schema_path)

    apply_schema(schema_path, DATABASE_URL)

from pathlib import Path

from manexp_web_lists.postgres_helpers import apply_schema, generate_schema, synchronize


def load_seeds(seeds_path: Path) -> None:
    """
    Load seeds in PostgreSQL from a list of Parquet files.

    Args:
        seeds_path: The path to Parquet files folder
    """

    schema_path = seeds_path / "schema.sql"

    generate_schema(seeds_path, schema_path)

    apply_schema(schema_path, "seeds")

    synchronize(seeds_path, "seeds")

from pathlib import Path

from manexp_web_lists.postgres_helpers import apply_schema, generate_schema, synchronize


def load_phytosanitary_products(phyto_path: Path) -> None:
    """
    Load phytosanitary products in PostgreSQL from a list of Parquet files.

    Args:
        phyto_path: The path to Parquet files folder
    """

    schema_path = phyto_path / "schema.sql"

    generate_schema(phyto_path, schema_path)

    apply_schema(schema_path, "products")

    synchronize(phyto_path, "products")

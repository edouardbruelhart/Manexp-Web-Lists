from pathlib import Path

import psycopg


def apply_schema(schema_path: Path, database_url: str) -> None:
    """
    Apply generated sql schema to the database

    Args:
        schema_path: path to the generated schema file
        database_url: url of the database to connect to
    """
    schema = schema_path.read_text()

    with psycopg.connect(database_url) as conn:
        conn.execute(schema)

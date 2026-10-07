from pathlib import Path

import psycopg
from psycopg import sql


def apply_schema(
    schema_path: Path,
    database_url: str,
    schema_name: str,
) -> None:
    """
    Apply generated SQL schema to the specified PostgreSQL schema.

    Args:
        schema_path: Path to the generated SQL schema file.
        database_url: URL of the PostgreSQL database.
        schema_name: Name of the PostgreSQL schema.
    """
    schema = schema_path.read_text()

    with psycopg.connect(database_url) as conn:
        conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema_name)))
        conn.execute(schema)

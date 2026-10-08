from pathlib import Path

from psycopg import sql

from manexp_web_lists.postgres_helpers.database_connection import psycopg_connection


def apply_schema(
    schema_path: Path,
    schema_name: str,
) -> None:
    """
    Apply generated SQL schema to the specified PostgreSQL schema.

    Args:
        schema_path: Path to the generated SQL schema file.
        schema_name: Name of the PostgreSQL schema.
    """
    schema = schema_path.read_text()

    with psycopg_connection() as conn:
        conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema_name)))
        conn.execute(schema)

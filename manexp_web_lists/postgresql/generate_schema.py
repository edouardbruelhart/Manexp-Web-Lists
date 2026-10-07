from pathlib import Path

import psycopg

from manexp_web_lists.postgresql import DATABASE_URL

from .generate_create_tables import generate_create_tables
from .generate_foreign_key_constraints import generate_foreign_key_constraints


def generate_schema(
    parquet_path: Path,
    output_file: Path,
) -> None:
    """
    Generate the SQL schema for a list of Parquet files.

    Args:
        parquet_path: the path to the directory containing the Parquet files
        output_file: the path where the generated SQL schema will be saved
    """

    files = {file.stem: file for file in parquet_path.iterdir() if file.suffix.lower() == ".parquet"}

    # Generate CREATE TABLE statements.
    tables = [generate_create_tables(file) for file in files.values()]

    # Generate FK statements.
    foreign_keys = generate_foreign_key_constraints(files)

    with psycopg.connect(DATABASE_URL) as pg_conn:
        foreign_key_sql = "\n\n".join(statement.as_string(pg_conn) for statement in foreign_keys)

    sql_parts = [
        "-- Generated automatically. Do not edit manually.",
        "",
        "-- Tables",
        "",
        "\n\n".join(tables),
        "",
        "",
        "-- Foreign keys",
        "",
        foreign_key_sql,
        "",
    ]

    output_file.write_text(
        "\n".join(sql_parts),
        encoding="utf-8",
    )

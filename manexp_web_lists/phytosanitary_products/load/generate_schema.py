from pathlib import Path

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
        "\n\n".join(foreign_keys),
        "",
    ]

    output_file.write_text(
        "\n".join(sql_parts),
        encoding="utf-8",
    )

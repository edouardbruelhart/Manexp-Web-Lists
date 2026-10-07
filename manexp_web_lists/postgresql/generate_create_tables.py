from pathlib import Path
from uuid import UUID

import pyarrow as pa
import pyarrow.parquet as pq

from manexp_web_lists.exceptions import UnsupportedTypeError


def generate_create_tables(file: Path) -> str:
    """
    Generate the SQL CREATE TABLE statement from a Parquet file

    Args:
        file: path to the Parquet file

    Returns:
        str: SQL CREATE TABLE statement
    """
    table_name = file.stem
    schema = pq.read_schema(file)

    columns = []

    for field in schema:
        sql_type = postgres_type(file, field)
        columns.append(f'    "{field.name}" {sql_type}')

    pk = primary_key(file, schema, table_name)

    columns.append("    PRIMARY KEY (" + ", ".join(f'"{name}"' for name in pk) + ")")

    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n' + ",\n".join(columns) + "\n);"

    add_columns = []

    for column in columns:
        stripped = column.strip()

        # Skip table constraints
        if stripped.upper().startswith((
            "PRIMARY KEY",
            "FOREIGN KEY",
            "UNIQUE",
            "CHECK",
            "CONSTRAINT",
        )):
            continue

        add_columns.append(f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS {stripped};')

    return create_sql + "\n\n" + "\n".join(add_columns) + "\n"


def primary_key(file: Path, schema: pa.Schema, table_name: str) -> list[str]:
    """
    Generate the primary key for a table from its schema

    Args:
        file: The path to the Parquet file
        schema: Parquet schema
        table_name: name of the table

    Returns:
        list[str]: primary key column(s)
    """
    if is_association_table(table_name):
        return [field.name for field in schema if field.name.endswith("_id") and not contain_null(file, field.name)]

    if "id" in schema.names:
        return ["id"]

    if "upov_code" in schema.names:
        return ["upov_code"]

    return ["id"]


def is_association_table(table_name: str) -> bool:
    """
    Check if a table is an association table

    Args:
        table_name: name of the table

    Returns:
        bool: True if the table is an association table, False otherwise
    """
    return (table_name.startswith("product_") or table_name.startswith("indication_")) and not table_name.startswith(
        "product_category"
    )


def postgres_type(file: Path, field: pa.Field) -> str:
    """
    Get the PostgreSQL data type for a field.

    Args:
        file: Path to the Parquet file
        field: pa.Field object

    Returns:
        str: The corresponding PostgreSQL data type

    Raises:
        UnsupportedTypeError: Raised when the type conversion is not supported
    """
    if is_uuid_column(file, field.name):
        return "UUID"

    dtype = field.type

    type_mappings = (
        (pa.types.is_string, "TEXT"),
        (pa.types.is_large_string, "TEXT"),
        (pa.types.is_boolean, "BOOLEAN"),
        (pa.types.is_int8, "SMALLINT"),
        (pa.types.is_int16, "SMALLINT"),
        (pa.types.is_int32, "INTEGER"),
        (pa.types.is_int64, "BIGINT"),
        (pa.types.is_float32, "REAL"),
        (pa.types.is_float64, "DOUBLE PRECISION"),
        (pa.types.is_date32, "DATE"),
        (pa.types.is_date64, "DATE"),
        (pa.types.is_timestamp, "TIMESTAMPTZ"),
    )

    for is_type, postgres_type in type_mappings:
        if is_type(dtype):
            return postgres_type

    if (pa.types.is_list(dtype) or pa.types.is_large_list(dtype)) and (
        pa.types.is_string(dtype.value_type) or pa.types.is_large_string(dtype.value_type)
    ):
        return "TEXT[]"

    raise UnsupportedTypeError(file.stem, field.name, dtype)


def is_uuid_column(file: Path, column_name: str) -> bool:
    """
    Check if a column in the Parquet file is a UUID column.

    Args:
        file: path to the Parquet file
        column_name: name of the column to check

    Returns:
        bool: True if the column is a UUID column, False otherwise
    """

    table = pq.read_table(file, columns=[column_name])

    values = table[column_name].to_pylist()

    has_value = False

    for value in values:
        if value is None or value == "":
            continue

        has_value = True

        try:
            UUID(value)
        except (ValueError, AttributeError, TypeError):
            return False

    return has_value


def contain_null(file: Path, column_name: str) -> bool:
    """
    Check if a column in the Parquet file contains null values.

    Args:
        file: path to the Parquet file
        column_name: name of the column to check

    Returns:
        bool: True if the column contains null, False otherwise
    """

    table = pq.read_table(file, columns=[column_name])

    values = table[column_name].to_pylist()

    if values is None or values == []:
        return True

    return any(value is None or value == "" for value in values)

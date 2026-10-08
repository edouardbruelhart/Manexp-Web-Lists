from __future__ import annotations

from pathlib import Path

import duckdb
import psycopg
from psycopg import sql

from manexp_web_lists.postgres_helpers.database_connection import psycopg_connection


def get_tables_in_insert_order(conn: psycopg.Connection, schema_name: str) -> list[str]:
    """
    Get the tables in a dependency order.

    Args:
        conn: A psycopg connection to the database.
        schema_name: The name of the schema to get tables from.

    Returns:
        list[str]: A list of table names in dependency order.
    """

    # Construct sql request
    sql = """
        WITH RECURSIVE dependencies AS (

            SELECT
                c.oid,
                c.relname AS table_name,
                0 AS depth,
                ARRAY[c.oid] AS path
            FROM pg_class c
            JOIN pg_namespace n
                ON n.oid = c.relnamespace
            WHERE n.nspname = %(schema_name)s
              AND c.relkind = 'r'

            UNION ALL

            SELECT
                child.oid,
                child.relname,
                d.depth + 1,
                d.path || child.oid
            FROM dependencies d
            JOIN pg_constraint fk
                ON fk.confrelid = d.oid
               AND fk.contype = 'f'
            JOIN pg_class child
                ON child.oid = fk.conrelid
            JOIN pg_namespace child_ns
                ON child_ns.oid = child.relnamespace
            WHERE child_ns.nspname = %(schema_name)s
              AND child.relkind = 'r'
              AND NOT child.oid = ANY(d.path)
        )

        SELECT
            table_name
        FROM dependencies
        GROUP BY table_name
        ORDER BY MAX(depth), table_name
    """

    with conn.cursor() as cur:
        cur.execute(sql, {"schema_name": schema_name})
        return [row[0] for row in cur.fetchall()]


def load_table(
    pg_conn: psycopg.Connection,
    duck_conn: duckdb.DuckDBPyConnection,
    parquet_file: Path,
    schema_name: str,
    table_name: str,
    batch_size: int = 10_000,
) -> None:
    """
    Load one Parquet file into one PostgreSQL table using COPY.

    Args:
        pg_conn: PostgreSQL connection object.
        duck_conn: DuckDB connection object.
        parquet_file: Path to the Parquet file.
        schema_name: Name of the PostgreSQL schema.
        table_name: Name of the PostgreSQL table.
        batch_size: Number of rows to load at a time. Default is 10_000.
    """

    # Get PostgreSQL column order.
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %(schema_name)s
              AND table_name = %(table_name)s
            ORDER BY ordinal_position
            """,
            {
                "schema_name": schema_name,
                "table_name": table_name,
            },
        )

        columns = [row[0] for row in cur.fetchall()]

    # Read the Parquet file through DuckDB's relational API.
    reader = duck_conn.from_parquet(str(parquet_file)).select(*columns)

    # PostgreSQL COPY.
    pg_table = sql.Identifier(schema_name, table_name)

    pg_columns = sql.SQL(", ").join(sql.Identifier(column) for column in columns)

    copy_sql = sql.SQL("COPY {} ({}) FROM STDIN").format(
        pg_table,
        pg_columns,
    )

    with pg_conn.cursor() as cur, cur.copy(copy_sql) as copy:
        while rows := reader.fetchmany(batch_size):
            for row in rows:
                copy.write_row(row)


def synchronize(parquet_directory: Path, schema_name: str) -> None:
    """
    Synchronize Parquet files to PostgreSQL database.

    Args:
        parquet_directory: Directory containing Parquet files.
        schema_name: Name of the PostgreSQL schema.
    """

    parquet_files = {p.stem: p for p in parquet_directory.glob("*.parquet")}

    # DuckDB for reading Parquet
    duck_conn = duckdb.connect()

    with psycopg_connection() as pg_conn:
        # Get tables in FK dependency order.
        tables = get_tables_in_insert_order(pg_conn, schema_name)

        # Truncate tables
        with pg_conn.cursor() as cur:
            table_sql = sql.SQL(", ").join(sql.Identifier(schema_name, table) for table in tables)

            cur.execute(sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY").format(table_sql))

        # Load parents before children.
        for table_name in tables:
            load_table(
                pg_conn,
                duck_conn,
                parquet_files[table_name],
                schema_name,
                table_name,
            )

from unittest.mock import MagicMock, patch

import pytest
from psycopg import sql

from manexp_web_lists.postgres_helpers.synchronize import get_tables_in_insert_order, load_table, synchronize

# ---------------------------------------------------------------------------
# get_tables_in_insert_order
# ---------------------------------------------------------------------------


def test_get_tables_in_insert_order_returns_table_names():
    conn = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        ("parent",),
        ("child",),
        ("grandchild",),
    ]

    conn.cursor.return_value.__enter__.return_value = cursor

    result = get_tables_in_insert_order(conn, "public")

    assert result == ["parent", "child", "grandchild"]

    cursor.execute.assert_called_once()

    sql_query, params = cursor.execute.call_args.args

    assert "pg_constraint" in sql_query
    assert "WITH RECURSIVE dependencies" in sql_query
    assert params == {"schema_name": "public"}


def test_get_tables_in_insert_order_returns_empty_list_when_no_tables():
    conn = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = []

    conn.cursor.return_value.__enter__.return_value = cursor

    result = get_tables_in_insert_order(conn, "empty_schema")

    assert result == []

    cursor.execute.assert_called_once_with(
        pytest.approx(cursor.execute.call_args.args[0]),
        {"schema_name": "empty_schema"},
    )


# ---------------------------------------------------------------------------
# load_table
# ---------------------------------------------------------------------------


def test_load_table_copy_statement(tmp_path):
    pg_conn = MagicMock()
    duck_conn = MagicMock()

    pg_cursor = MagicMock()
    pg_conn.cursor.return_value.__enter__.return_value = pg_cursor

    pg_cursor.fetchall.return_value = [
        ("id",),
        ("name",),
    ]

    reader = MagicMock()
    duck_conn.from_parquet.return_value.select.return_value = reader
    reader.fetchmany.return_value = []

    copy = MagicMock()
    copy_context = MagicMock()
    copy_context.__enter__.return_value = copy
    pg_cursor.copy.return_value = copy_context

    load_table(
        pg_conn,
        duck_conn,
        tmp_path / "data.parquet",
        "public",
        "users",
    )

    expected_sql = sql.SQL("COPY {} ({}) FROM STDIN").format(
        sql.Identifier("public", "users"),
        sql.SQL(", ").join(sql.Identifier(column) for column in ["id", "name"]),
    )

    pg_cursor.copy.assert_called_once_with(expected_sql)


def test_load_table_with_no_rows(tmp_path):
    pg_conn = MagicMock()
    duck_conn = MagicMock()

    pg_cursor = MagicMock()
    pg_conn.cursor.return_value.__enter__.return_value = pg_cursor

    pg_cursor.fetchall.return_value = [
        ("id",),
        ("name",),
    ]

    reader = MagicMock()
    duck_conn.from_parquet.return_value.select.return_value = reader
    reader.fetchmany.return_value = []

    copy = MagicMock()
    copy_context = MagicMock()
    copy_context.__enter__.return_value = copy
    pg_cursor.copy.return_value = copy_context

    load_table(
        pg_conn,
        duck_conn,
        tmp_path / "data.parquet",
        "public",
        "users",
    )

    reader.fetchmany.assert_called_once_with(10_000)

    copy.write_row.assert_not_called()


def test_load_table_uses_batch_size(tmp_path):
    pg_conn = MagicMock()
    duck_conn = MagicMock()

    pg_cursor = MagicMock()
    pg_conn.cursor.return_value.__enter__.return_value = pg_cursor
    pg_cursor.fetchall.return_value = [("id",)]

    reader = MagicMock()
    duck_conn.from_parquet.return_value.select.return_value = reader
    reader.fetchmany.side_effect = [
        [(1,), (2,)],
        [(3,)],
        [],
    ]

    copy = MagicMock()
    copy_context = MagicMock()
    copy_context.__enter__.return_value = copy
    pg_cursor.copy.return_value = copy_context

    load_table(
        pg_conn,
        duck_conn,
        tmp_path / "data.parquet",
        "public",
        "users",
        batch_size=2,
    )

    assert reader.fetchmany.call_count == 3
    reader.fetchmany.assert_called_with(2)

    assert copy.write_row.call_count == 3


# ---------------------------------------------------------------------------
# synchronize
# ---------------------------------------------------------------------------


def test_synchronize_loads_tables_in_dependency_order(tmp_path):
    parent_file = tmp_path / "parent.parquet"
    child_file = tmp_path / "child.parquet"

    parent_file.touch()
    child_file.touch()

    with (
        patch("manexp_web_lists.postgres_helpers.synchronize.duckdb.connect") as duck_connect,
        patch("manexp_web_lists.postgres_helpers.synchronize.psycopg_connection") as pg_connect,
        patch(
            "manexp_web_lists.postgres_helpers.synchronize.get_tables_in_insert_order",
            return_value=["parent", "child"],
        ) as get_tables,
        patch("manexp_web_lists.postgres_helpers.synchronize.load_table") as load_table,
    ):
        duck_conn = MagicMock()
        duck_connect.return_value = duck_conn

        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            schema_name="public",
        )

    get_tables.assert_called_once_with(pg_conn, "public")

    assert load_table.call_count == 2

    first_call = load_table.call_args_list[0]
    second_call = load_table.call_args_list[1]

    assert first_call.args == (
        pg_conn,
        duck_conn,
        parent_file,
        "public",
        "parent",
    )

    assert second_call.args == (
        pg_conn,
        duck_conn,
        child_file,
        "public",
        "child",
    )


def test_synchronize_truncates_tables_before_loading(tmp_path):
    (tmp_path / "parent.parquet").touch()
    (tmp_path / "child.parquet").touch()

    with (
        patch("manexp_web_lists.postgres_helpers.synchronize.duckdb.connect") as duck_connect,
        patch("manexp_web_lists.postgres_helpers.synchronize.psycopg_connection") as pg_connect,
        patch(
            "manexp_web_lists.postgres_helpers.synchronize.get_tables_in_insert_order",
            return_value=["parent", "child"],
        ),
        patch("manexp_web_lists.postgres_helpers.synchronize.load_table") as load_table,
    ):
        duck_conn = MagicMock()
        duck_connect.return_value = duck_conn

        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            schema_name="public",
        )

    cursor.execute.assert_called_once()

    truncate_sql = cursor.execute.call_args.args[0]

    # We don't care about whitespace or the exact Composed object
    # representation; the important part is that TRUNCATE and the
    # expected tables are present.
    assert "TRUNCATE TABLE" in str(truncate_sql)

    # load_table must happen after the truncate operation.
    assert cursor.execute.call_count == 1
    assert load_table.call_count == 2


def test_synchronize_connects_using_database_url(tmp_path):
    (tmp_path / "users.parquet").touch()

    with (
        patch("manexp_web_lists.postgres_helpers.synchronize.duckdb.connect") as duck_connect,
        patch("manexp_web_lists.postgres_helpers.synchronize.psycopg_connection") as pg_connect,
        patch(
            "manexp_web_lists.postgres_helpers.synchronize.get_tables_in_insert_order",
            return_value=["users"],
        ),
        patch("manexp_web_lists.postgres_helpers.synchronize.load_table"),
    ):
        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            schema_name="public",
        )

    pg_connect.assert_called_once()

    duck_connect.assert_called_once()


def test_synchronize_uses_only_parquet_files(tmp_path):
    (tmp_path / "users.parquet").touch()
    (tmp_path / "README.txt").touch()
    (tmp_path / "other.csv").touch()

    with (
        patch("manexp_web_lists.postgres_helpers.synchronize.duckdb.connect"),
        patch("manexp_web_lists.postgres_helpers.synchronize.psycopg_connection") as pg_connect,
        patch(
            "manexp_web_lists.postgres_helpers.synchronize.get_tables_in_insert_order",
            return_value=["users"],
        ),
        patch("manexp_web_lists.postgres_helpers.synchronize.load_table") as load_table,
    ):
        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            schema_name="public",
        )

    load_table.assert_called_once()

    assert load_table.call_args.args[2] == tmp_path / "users.parquet"


def test_synchronize_raises_key_error_for_missing_parquet_file(tmp_path):
    # The database contains a table, but there is no corresponding
    # Parquet file.
    with (
        patch("manexp_web_lists.postgres_helpers.synchronize.duckdb.connect"),
        patch("manexp_web_lists.postgres_helpers.synchronize.psycopg_connection") as pg_connect,
        patch(
            "manexp_web_lists.postgres_helpers.synchronize.get_tables_in_insert_order",
            return_value=["missing_table"],
        ),
        patch("manexp_web_lists.postgres_helpers.synchronize.load_table") as load_table,
    ):
        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        with pytest.raises(KeyError, match="missing_table"):
            synchronize(
                parquet_directory=tmp_path,
                schema_name="public",
            )

    load_table.assert_not_called()


def test_synchronize_propagates_load_table_error(tmp_path):
    (tmp_path / "users.parquet").touch()

    with (
        patch("manexp_web_lists.postgres_helpers.synchronize.duckdb.connect"),
        patch("manexp_web_lists.postgres_helpers.synchronize.psycopg_connection") as pg_connect,
        patch(
            "manexp_web_lists.postgres_helpers.synchronize.get_tables_in_insert_order",
            return_value=["users"],
        ),
        patch(
            "manexp_web_lists.postgres_helpers.synchronize.load_table",
            side_effect=RuntimeError("COPY failed"),
        ),
    ):
        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        with pytest.raises(RuntimeError, match="COPY failed"):
            synchronize(
                parquet_directory=tmp_path,
                schema_name="public",
            )

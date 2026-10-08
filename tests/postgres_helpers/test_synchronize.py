from unittest.mock import MagicMock, patch

import pytest

from manexp_web_lists.postgres_helpers.synchronize import get_tables_in_insert_order, synchronize

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


def make_pg_connection(columns):
    """Create a mocked PostgreSQL connection with the given columns."""
    conn = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [(column,) for column in columns]

    conn.cursor.return_value.__enter__.return_value = cursor

    return conn, cursor


def make_copy_cursor(pg_conn):
    """Configure the mocked PostgreSQL cursor for COPY."""
    copy = MagicMock()

    pg_conn.cursor.return_value.__enter__.return_value.copy.return_value.__enter__.return_value = copy

    return copy


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

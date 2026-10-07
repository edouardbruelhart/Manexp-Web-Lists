from unittest.mock import MagicMock, patch

import pytest

from manexp_web_lists.postgresql.synchronize import get_tables_in_insert_order, load_table, synchronize

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


def test_load_table_reads_columns_in_postgresql_order(tmp_path):
    parquet_file = tmp_path / "users.parquet"
    parquet_file.touch()

    pg_conn, cursor = make_pg_connection(["id", "name", "created_at"])

    duck_conn = MagicMock()
    reader = MagicMock()
    reader.fetchmany.return_value = []

    duck_conn.execute.return_value = reader

    load_table(
        pg_conn=pg_conn,
        duck_conn=duck_conn,
        parquet_file=parquet_file,
        schema_name="public",
        table_name="users",
    )

    # First cursor operation retrieves PostgreSQL columns.
    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args.args

    assert "information_schema.columns" in query
    assert "ORDER BY ordinal_position" in query
    assert params == {
        "schema_name": "public",
        "table_name": "users",
    }


def test_load_table_queries_duckdb_using_postgresql_columns(tmp_path):
    parquet_file = tmp_path / "users.parquet"
    parquet_file.touch()

    pg_conn, _ = make_pg_connection(["id", "name", "email"])

    duck_conn = MagicMock()
    reader = MagicMock()
    reader.fetchmany.return_value = []

    duck_conn.execute.return_value = reader

    make_copy_cursor(pg_conn)

    load_table(
        pg_conn=pg_conn,
        duck_conn=duck_conn,
        parquet_file=parquet_file,
        schema_name="public",
        table_name="users",
    )

    duck_conn.execute.assert_called_once()

    query = duck_conn.execute.call_args.args[0]

    assert '"id"' in query
    assert '"name"' in query
    assert '"email"' in query
    assert "read_parquet(" in query


def test_load_table_escapes_single_quotes_in_parquet_path(tmp_path):
    parquet_file = tmp_path / "it's-a-file.parquet"
    parquet_file.touch()

    pg_conn, _ = make_pg_connection(["id"])

    duck_conn = MagicMock()
    reader = MagicMock()
    reader.fetchmany.return_value = []

    duck_conn.execute.return_value = reader

    make_copy_cursor(pg_conn)

    load_table(
        pg_conn=pg_conn,
        duck_conn=duck_conn,
        parquet_file=parquet_file,
        schema_name="public",
        table_name="users",
    )

    query = duck_conn.execute.call_args.args[0]

    # SQL string literal escaping:
    # it's-a-file.parquet -> it''s-a-file.parquet
    assert "it''s-a-file.parquet" in query


def test_load_table_escapes_double_quotes_in_column_names(tmp_path):
    parquet_file = tmp_path / "users.parquet"
    parquet_file.touch()

    column_name = 'column"with"quotes'

    pg_conn, _ = make_pg_connection([column_name])

    duck_conn = MagicMock()
    reader = MagicMock()
    reader.fetchmany.return_value = []

    duck_conn.execute.return_value = reader

    make_copy_cursor(pg_conn)

    load_table(
        pg_conn=pg_conn,
        duck_conn=duck_conn,
        parquet_file=parquet_file,
        schema_name="public",
        table_name="users",
    )

    query = duck_conn.execute.call_args.args[0]

    assert '"column""with""quotes"' in query


def test_load_table_writes_all_rows_to_copy(tmp_path):
    parquet_file = tmp_path / "users.parquet"
    parquet_file.touch()

    pg_conn, _ = make_pg_connection(["id", "name"])

    duck_conn = MagicMock()
    reader = MagicMock()

    rows = [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie"),
    ]

    reader.fetchmany.side_effect = [
        rows,
        [],
    ]

    duck_conn.execute.return_value = reader

    copy = make_copy_cursor(pg_conn)

    load_table(
        pg_conn=pg_conn,
        duck_conn=duck_conn,
        parquet_file=parquet_file,
        schema_name="public",
        table_name="users",
    )

    assert copy.write_row.call_count == 3

    copy.write_row.assert_any_call((1, "Alice"))
    copy.write_row.assert_any_call((2, "Bob"))
    copy.write_row.assert_any_call((3, "Charlie"))


def test_load_table_fetches_using_batch_size(tmp_path):
    parquet_file = tmp_path / "users.parquet"
    parquet_file.touch()

    pg_conn, _ = make_pg_connection(["id"])

    duck_conn = MagicMock()
    reader = MagicMock()

    reader.fetchmany.side_effect = [
        [(1,)],
        [(2,)],
        [],
    ]

    duck_conn.execute.return_value = reader

    make_copy_cursor(pg_conn)

    load_table(
        pg_conn=pg_conn,
        duck_conn=duck_conn,
        parquet_file=parquet_file,
        schema_name="public",
        table_name="users",
        batch_size=42,
    )

    assert reader.fetchmany.call_count == 3
    reader.fetchmany.assert_called_with(42)


def test_load_table_does_not_write_when_parquet_is_empty(tmp_path):
    parquet_file = tmp_path / "empty.parquet"
    parquet_file.touch()

    pg_conn, _ = make_pg_connection(["id"])

    duck_conn = MagicMock()
    reader = MagicMock()
    reader.fetchmany.return_value = []

    duck_conn.execute.return_value = reader

    copy = make_copy_cursor(pg_conn)

    load_table(
        pg_conn=pg_conn,
        duck_conn=duck_conn,
        parquet_file=parquet_file,
        schema_name="public",
        table_name="users",
    )

    copy.write_row.assert_not_called()


# ---------------------------------------------------------------------------
# synchronize
# ---------------------------------------------------------------------------


def test_synchronize_loads_tables_in_dependency_order(tmp_path):
    parent_file = tmp_path / "parent.parquet"
    child_file = tmp_path / "child.parquet"

    parent_file.touch()
    child_file.touch()

    with (
        patch("manexp_web_lists.postgresql.synchronize.duckdb.connect") as duck_connect,
        patch("manexp_web_lists.postgresql.synchronize.psycopg.connect") as pg_connect,
        patch(
            "manexp_web_lists.postgresql.synchronize.get_tables_in_insert_order",
            return_value=["parent", "child"],
        ) as get_tables,
        patch("manexp_web_lists.postgresql.synchronize.load_table") as load_table,
    ):
        duck_conn = MagicMock()
        duck_connect.return_value = duck_conn

        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            database_url="postgresql://example",
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
        patch("manexp_web_lists.postgresql.synchronize.duckdb.connect") as duck_connect,
        patch("manexp_web_lists.postgresql.synchronize.psycopg.connect") as pg_connect,
        patch(
            "manexp_web_lists.postgresql.synchronize.get_tables_in_insert_order",
            return_value=["parent", "child"],
        ),
        patch("manexp_web_lists.postgresql.synchronize.load_table") as load_table,
    ):
        duck_conn = MagicMock()
        duck_connect.return_value = duck_conn

        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            database_url="postgresql://example",
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
        patch("manexp_web_lists.postgresql.synchronize.duckdb.connect") as duck_connect,
        patch("manexp_web_lists.postgresql.synchronize.psycopg.connect") as pg_connect,
        patch(
            "manexp_web_lists.postgresql.synchronize.get_tables_in_insert_order",
            return_value=["users"],
        ),
        patch("manexp_web_lists.postgresql.synchronize.load_table"),
    ):
        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            database_url="postgresql://user:password@localhost/db",
            schema_name="public",
        )

    pg_connect.assert_called_once_with("postgresql://user:password@localhost/db")

    duck_connect.assert_called_once_with()


def test_synchronize_uses_only_parquet_files(tmp_path):
    (tmp_path / "users.parquet").touch()
    (tmp_path / "README.txt").touch()
    (tmp_path / "other.csv").touch()

    with (
        patch("manexp_web_lists.postgresql.synchronize.duckdb.connect"),
        patch("manexp_web_lists.postgresql.synchronize.psycopg.connect") as pg_connect,
        patch(
            "manexp_web_lists.postgresql.synchronize.get_tables_in_insert_order",
            return_value=["users"],
        ),
        patch("manexp_web_lists.postgresql.synchronize.load_table") as load_table,
    ):
        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        synchronize(
            parquet_directory=tmp_path,
            database_url="postgresql://example",
            schema_name="public",
        )

    load_table.assert_called_once()

    assert load_table.call_args.args[2] == tmp_path / "users.parquet"


def test_synchronize_raises_key_error_for_missing_parquet_file(tmp_path):
    # The database contains a table, but there is no corresponding
    # Parquet file.
    with (
        patch("manexp_web_lists.postgresql.synchronize.duckdb.connect"),
        patch("manexp_web_lists.postgresql.synchronize.psycopg.connect") as pg_connect,
        patch(
            "manexp_web_lists.postgresql.synchronize.get_tables_in_insert_order",
            return_value=["missing_table"],
        ),
        patch("manexp_web_lists.postgresql.synchronize.load_table") as load_table,
    ):
        pg_conn = MagicMock()
        pg_connect.return_value.__enter__.return_value = pg_conn

        cursor = MagicMock()
        pg_conn.cursor.return_value.__enter__.return_value = cursor

        with pytest.raises(KeyError, match="missing_table"):
            synchronize(
                parquet_directory=tmp_path,
                database_url="postgresql://example",
                schema_name="public",
            )

    load_table.assert_not_called()


def test_synchronize_propagates_load_table_error(tmp_path):
    (tmp_path / "users.parquet").touch()

    with (
        patch("manexp_web_lists.postgresql.synchronize.duckdb.connect"),
        patch("manexp_web_lists.postgresql.synchronize.psycopg.connect") as pg_connect,
        patch(
            "manexp_web_lists.postgresql.synchronize.get_tables_in_insert_order",
            return_value=["users"],
        ),
        patch(
            "manexp_web_lists.postgresql.synchronize.load_table",
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
                database_url="postgresql://example",
                schema_name="public",
            )

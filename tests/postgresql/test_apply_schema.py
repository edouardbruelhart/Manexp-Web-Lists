from unittest.mock import MagicMock, patch

from manexp_web_lists.postgresql.apply_schema import apply_schema


def test_apply_schema(tmp_path):
    schema_path = tmp_path / "schema.sql"
    schema = "CREATE TABLE test (id INTEGER);"
    schema_path.write_text(schema)

    database_url = "postgresql://pipeline:secret@127.0.0.1:5432/mydb"

    mock_conn = MagicMock()

    with patch(
        "manexp_web_lists.postgresql.apply_schema.psycopg.connect",
    ) as mock_connect:
        mock_connect.return_value.__enter__.return_value = mock_conn

        apply_schema(
            schema_path,
            database_url,
            "products",
        )

    mock_connect.assert_called_once_with(database_url)

    assert mock_conn.execute.call_count == 2
    assert mock_conn.execute.call_args_list[1].args[0] == schema

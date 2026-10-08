from unittest.mock import MagicMock, patch

from manexp_web_lists.postgres_helpers.apply_schema import apply_schema


def test_apply_schema(tmp_path):
    schema_path = tmp_path / "schema.sql"
    schema = "CREATE TABLE test (id INTEGER);"
    schema_path.write_text(schema)

    mock_conn = MagicMock()

    with patch(
        "manexp_web_lists.postgres_helpers.apply_schema.psycopg_connection",
    ) as mock_connect:
        mock_connect.return_value.__enter__.return_value = mock_conn

        apply_schema(
            schema_path,
            "products",
        )

    mock_connect.assert_called_once()

    assert mock_conn.execute.call_count == 2
    assert mock_conn.execute.call_args_list[1].args[0] == schema

from pathlib import Path
from unittest.mock import MagicMock, patch

from manexp_web_lists.phytosanitary_products.load.apply_schema import apply_schema


def test_apply_schema():
    schema = """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY
    );
    """

    database_url = "postgresql://localhost/test"
    schema_path = Path("schema.sql")

    mock_conn = MagicMock()

    with (
        patch("manexp_web_lists.phytosanitary_products.load.apply_schema.psycopg.connect") as mock_connect,
        patch(
            "manexp_web_lists.phytosanitary_products.load.apply_schema.Path.read_text", return_value=schema
        ) as mock_read,
    ):
        mock_connect.return_value.__enter__.return_value = mock_conn

        apply_schema(schema_path, database_url)

    mock_read.assert_called_once_with()
    mock_connect.assert_called_once_with(database_url)
    mock_conn.execute.assert_called_once_with(schema)

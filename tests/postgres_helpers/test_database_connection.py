from unittest.mock import patch

from manexp_web_lists.postgres_helpers.database_connection import psycopg_connection


def test_psycopg_connection(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "test-db")
    monkeypatch.setenv("POSTGRES_USER", "test-user")

    with (
        patch(
            "manexp_web_lists.postgres_helpers.database_connection.Path.read_text",
            return_value="test-password\n",
        ),
        patch("manexp_web_lists.postgres_helpers.database_connection.connect") as mock_connect,
    ):
        psycopg_connection()

    mock_connect.assert_called_once_with(
        host="database",
        port=5432,
        dbname="test-db",
        user="test-user",
        password="test-password",  # noqa: S106 - password is a test example
    )

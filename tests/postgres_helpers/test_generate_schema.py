from unittest.mock import MagicMock, patch

from psycopg import sql

from manexp_web_lists.postgres_helpers.generate_schema import (
    generate_schema,
)


def test_generate_schema(tmp_path):
    parquet_path = tmp_path / "parquet"
    parquet_path.mkdir()

    products = parquet_path / "products.parquet"
    ingredients = parquet_path / "ingredients.parquet"
    readme = parquet_path / "README.txt"

    products.touch()
    ingredients.touch()
    readme.touch()

    output_file = tmp_path / "schema.sql"

    table_sql = {
        products: 'CREATE TABLE "products" (...);',
        ingredients: 'CREATE TABLE "ingredients" (...);',
    }

    foreign_key_sql = [
        sql.SQL('ALTER TABLE "products" ADD FOREIGN KEY ("ingredient_id") REFERENCES "ingredients" ("id");'),
    ]

    with (
        patch(
            "manexp_web_lists.postgres_helpers.generate_schema.generate_create_tables",
            side_effect=lambda file: table_sql[file],
        ) as mock_create_tables,
        patch(
            "manexp_web_lists.postgres_helpers.generate_schema.generate_foreign_key_constraints",
            return_value=foreign_key_sql,
        ) as mock_foreign_keys,
        patch(
            "manexp_web_lists.postgres_helpers.generate_schema.psycopg_connection",
        ) as mock_conn,
    ):
        generate_schema(parquet_path, output_file)

    assert mock_create_tables.call_count == 2
    mock_create_tables.assert_any_call(products)
    mock_create_tables.assert_any_call(ingredients)

    mock_foreign_keys.assert_called_once_with({
        "products": products,
        "ingredients": ingredients,
    })

    pg_conn = MagicMock()
    mock_conn.return_value.__enter__.return_value = pg_conn

    result = output_file.read_text(encoding="utf-8")

    assert "-- Generated automatically. Do not edit manually." in result
    assert "-- Tables" in result
    assert 'CREATE TABLE "products" (...);' in result
    assert 'CREATE TABLE "ingredients" (...);' in result
    assert "-- Foreign keys" in result
    assert ('ALTER TABLE "products" ADD FOREIGN KEY ("ingredient_id") REFERENCES "ingredients" ("id");') in result

    assert "README.txt" not in result

from unittest.mock import patch

from manexp_web_lists.postgresql.generate_schema import (
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
        'ALTER TABLE "products" ADD FOREIGN KEY ("ingredient_id") REFERENCES "ingredients" ("id");',
    ]

    with (
        patch(
            "manexp_web_lists.postgresql.generate_schema.generate_create_tables",
            side_effect=lambda file: table_sql[file],
        ) as mock_create_tables,
        patch(
            "manexp_web_lists.postgresql.generate_schema.generate_foreign_key_constraints",
            return_value=foreign_key_sql,
        ) as mock_foreign_keys,
    ):
        generate_schema(parquet_path, output_file)

    assert mock_create_tables.call_count == 2
    mock_create_tables.assert_any_call(products)
    mock_create_tables.assert_any_call(ingredients)

    mock_foreign_keys.assert_called_once_with({
        "products": products,
        "ingredients": ingredients,
    })

    result = output_file.read_text(encoding="utf-8")

    assert "-- Generated automatically. Do not edit manually." in result
    assert "-- Tables" in result
    assert 'CREATE TABLE "products" (...);' in result
    assert 'CREATE TABLE "ingredients" (...);' in result
    assert "-- Foreign keys" in result
    assert ('ALTER TABLE "products" ADD FOREIGN KEY ("ingredient_id") REFERENCES "ingredients" ("id");') in result

    assert "README.txt" not in result

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from manexp_web_lists.postgresql.generate_foreign_key_constraints import (
    foreign_key_target,
    generate_foreign_key_constraints,
)


def write_parquet(tmp_path, table_name, columns):
    file = tmp_path / f"{table_name}.parquet"

    table = pa.table(columns)
    pq.write_table(table, file)

    return file


def test_generate_foreign_key_constraints(tmp_path):
    products = write_parquet(
        tmp_path,
        "products",
        {
            "id": [1, 2],
            "category_id": [10, 20],
            "name": ["foo", "bar"],
        },
    )

    category = write_parquet(
        tmp_path,
        "category",
        {
            "id": [10, 20],
            "name": ["A", "B"],
        },
    )

    files = {
        "products": products,
        "category": category,
    }

    result = generate_foreign_key_constraints(files)

    assert result == [
        "DO $$\n"
        "BEGIN\n"
        "   IF NOT EXISTS (\n"
        "       SELECT 1\n"
        "       FROM pg_constraint\n"
        "       WHERE pg_constraint.conname = 'fk_products_category'\n"
        "   ) THEN\n"
        '       ALTER TABLE "products"\n'
        '       ADD CONSTRAINT "fk_products_category"\n'
        '       FOREIGN KEY ("category_id")\n'
        '       REFERENCES "category" ("id");\n'
        "   END IF;\n"
        "END\n"
        "$$;"
    ]


@pytest.mark.parametrize(
    ("table_name", "column_name", "expected"),
    [
        (
            "products",
            "parent_id",
            ("products", "id"),
        ),
        (
            "products",
            "category_id",
            ("category", "id"),
        ),
        (
            "products",
            "ingredient_id",
            ("ingredient", "id"),
        ),
        (
            "products",
            "id",
            None,
        ),
        (
            "products",
            "name",
            None,
        ),
        (
            "products",
            "created_at",
            None,
        ),
    ],
)
def test_foreign_key_target(table_name, column_name, expected):
    assert foreign_key_target(table_name, column_name) == expected

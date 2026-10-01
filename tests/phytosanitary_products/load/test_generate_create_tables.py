from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from manexp_web_lists.exceptions import UnsupportedTypeError
from manexp_web_lists.phytosanitary_products.load.generate_create_tables import (
    contain_null,
    generate_create_tables,
    is_association_table,
    is_uuid_column,
    postgres_type,
    primary_key,
)


def test_generate_create_tables_excludes_nullable_pk_column(tmp_path):
    file = tmp_path / "product_ingredients.parquet"

    table = pa.table({
        "product_id": [1, 2, None],
        "ingredient_id": [10, 20, 30],
        "amount": [1.0, 2.0, 3.0],
    })

    pq.write_table(table, file)

    result = generate_create_tables(file)

    expected = dedent("""\
        CREATE TABLE IF NOT EXISTS "product_ingredients" (
            "product_id" BIGINT,
            "ingredient_id" BIGINT,
            "amount" DOUBLE PRECISION,
            PRIMARY KEY ("ingredient_id")
        );
    """)

    assert result == expected


def write_parquet(tmp_path, data):
    file = tmp_path / "test.parquet"
    table = pa.table(data)
    pq.write_table(table, file)
    return file


def test_primary_key_for_normal_table(tmp_path):
    file = write_parquet(
        tmp_path,
        {
            "id": [1, 2, 3],
            "name": ["foo", "bar", "baz"],
        },
    )

    schema = pq.read_schema(file)

    assert primary_key(file, schema, "products") == ["id"]


def test_primary_key_for_association_table(tmp_path):
    file = write_parquet(
        tmp_path,
        {
            "product_id": [1, 2, 3],
            "ingredient_id": [10, 20, 30],
            "amount": [1.0, 2.0, 3.0],
        },
    )

    schema = pq.read_schema(file)

    assert primary_key(
        file,
        schema,
        "product_ingredients",
    ) == ["product_id", "ingredient_id"]


def test_primary_key_excludes_nullable_id_columns(tmp_path):
    file = write_parquet(
        tmp_path,
        {
            "product_id": [1, 2, None],
            "ingredient_id": [10, 20, 30],
        },
    )

    schema = pq.read_schema(file)

    assert primary_key(
        file,
        schema,
        "product_ingredients",
    ) == ["ingredient_id"]


def test_primary_key_excludes_empty_id_columns(tmp_path):
    file = write_parquet(
        tmp_path,
        {
            "product_id": ["1", "", "3"],
            "ingredient_id": [10, 20, 30],
        },
    )

    schema = pq.read_schema(file)

    assert primary_key(
        file,
        schema,
        "product_ingredients",
    ) == ["ingredient_id"]


def test_primary_key_with_all_nullable_id_columns(tmp_path):
    file = write_parquet(
        tmp_path,
        {
            "product_id": [1, None, 3],
            "ingredient_id": [10, 20, None],
        },
    )

    schema = pq.read_schema(file)

    assert (
        primary_key(
            file,
            schema,
            "product_ingredients",
        )
        == []
    )


@pytest.mark.parametrize(
    ("table_name", "expected"),
    [
        ("product_indication", True),
        ("product_category", False),
        ("indication_product", True),
        ("indication_something", True),
        ("products", False),
        ("ingredients", False),
    ],
)
def test_is_association_table(table_name, expected):
    assert is_association_table(table_name) is expected


@pytest.mark.parametrize(
    ("arrow_type", "expected"),
    [
        (pa.string(), "TEXT"),
        (pa.large_string(), "TEXT"),
        (pa.bool_(), "BOOLEAN"),
        (pa.int8(), "SMALLINT"),
        (pa.int16(), "SMALLINT"),
        (pa.int32(), "INTEGER"),
        (pa.int64(), "BIGINT"),
        (pa.float32(), "REAL"),
        (pa.float64(), "DOUBLE PRECISION"),
        (pa.date32(), "DATE"),
        (pa.date64(), "DATE"),
        (pa.timestamp("s"), "TIMESTAMPTZ"),
        (pa.timestamp("ms"), "TIMESTAMPTZ"),
        (pa.timestamp("us"), "TIMESTAMPTZ"),
        (pa.timestamp("ns"), "TIMESTAMPTZ"),
        (pa.list_(pa.string()), "TEXT[]"),
        (pa.large_list(pa.string()), "TEXT[]"),
        (pa.list_(pa.large_string()), "TEXT[]"),
        (pa.large_list(pa.large_string()), "TEXT[]"),
    ],
)
def test_postgres_type(arrow_type, expected):
    field = pa.field("column", arrow_type)

    with patch(
        "manexp_web_lists.phytosanitary_products.load.generate_create_tables.is_uuid_column",
        return_value=False,
    ):
        result = postgres_type(Path("products.parquet"), field)

    assert result == expected


@pytest.mark.parametrize(
    "arrow_type",
    [
        pa.binary(),
        pa.large_binary(),
        pa.list_(pa.int64()),
        pa.struct([
            pa.field("foo", pa.string()),
        ]),
    ],
)
def test_postgres_type_unsupported(arrow_type):
    field = pa.field("column", arrow_type)
    file = Path("products.parquet")

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.load.generate_create_tables.is_uuid_column",
            return_value=False,
        ),
        pytest.raises(UnsupportedTypeError),
    ):
        postgres_type(file, field)


def test_postgres_type_uuid():
    field = pa.field("id", pa.string())

    with patch(
        "manexp_web_lists.phytosanitary_products.load.generate_create_tables.is_uuid_column",
        return_value=True,
    ):
        assert postgres_type(Path("products.parquet"), field) == "UUID"


def test_is_uuid_column_with_valid_uuids(tmp_path):
    file = write_parquet(
        tmp_path,
        {
            "id": [
                "550e8400-e29b-41d4-a716-446655440000",
                "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            ]
        },
    )

    assert is_uuid_column(file, "id") is True


def test_is_uuid_column_with_invalid_uuid(tmp_path):
    file = write_parquet(tmp_path, {"id": ["not-an-id"]})

    assert is_uuid_column(file, "id") is False


def test_is_uuid_column_with_null_values(tmp_path):
    file = write_parquet(tmp_path, {"id": [None, "550e8400-e29b-41d4-a716-446655440000"]})

    assert is_uuid_column(file, "id") is True


def test_is_uuid_column_with_empty_values(tmp_path):
    file = write_parquet(tmp_path, {"id": ["", "550e8400-e29b-41d4-a716-446655440000"]})

    assert is_uuid_column(file, "id") is True


def test_is_uuid_column_with_only_empty_or_null_values(tmp_path):
    file = write_parquet(tmp_path, {"id": [None, ""]})

    assert is_uuid_column(file, "id") is False


def test_contain_null_returns_true_for_null(tmp_path):
    file = write_parquet(tmp_path, {"column": [1, None, 3]})

    assert contain_null(file, "column") is True


def test_contain_null_returns_true_for_empty_string(tmp_path):
    file = write_parquet(tmp_path, {"column": ["foo", "", "bar"]})

    assert contain_null(file, "column") is True


def test_contain_null_returns_false_when_no_null(tmp_path):
    file = write_parquet(tmp_path, {"column": [1, 2, 3]})

    assert contain_null(file, "column") is False


def test_contain_null_returns_true_for_empty_column(tmp_path):
    file = write_parquet(tmp_path, {"column": []})

    assert contain_null(file, "column") is True

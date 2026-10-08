import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from psycopg import sql

from manexp_web_lists.exceptions import UnresolvedForeignKeyError
from manexp_web_lists.postgres_helpers.generate_foreign_key_constraints import (
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
        },
    )

    files = {
        "products": products,
        "category": category,
    }

    result = generate_foreign_key_constraints(files)

    assert len(result) == 1
    assert isinstance(result[0], sql.Composed)


def test_generate_foreign_key_constraints_no_target_table(tmp_path):
    products = write_parquet(
        tmp_path,
        "products",
        {
            "id": [1, 2],
            "non_existing_table_id": [10, 20],
            "name": ["foo", "bar"],
        },
    )

    category = write_parquet(
        tmp_path,
        "category",
        {
            "id": [10, 20],
        },
    )

    files = {
        "products": products,
        "category": category,
    }

    with pytest.raises(UnresolvedForeignKeyError):
        generate_foreign_key_constraints(files)


def test_foreign_key_target():
    assert foreign_key_target("table", "parent_id") == ("table", "id")
    assert foreign_key_target("table", "taxon_id") == ("taxon", "upov_code")

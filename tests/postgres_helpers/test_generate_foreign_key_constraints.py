import pyarrow as pa
import pyarrow.parquet as pq
from psycopg import sql

from manexp_web_lists.postgres_helpers.generate_foreign_key_constraints import (
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

"""Tests for seeds/transform/filter_columns.py"""

import polars as pl

from manexp_web_lists.seeds.transform.filter_columns import (
    COLUMNS_TO_DROP,
    filter_columns,
)


def test_filter_columns() -> None:
    data = {column: [None] for column in COLUMNS_TO_DROP}
    data["Keep me"] = ["value"]

    result = filter_columns(pl.DataFrame(data))

    assert result.columns == ["Keep me"]

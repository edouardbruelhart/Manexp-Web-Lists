"""Tests for seeds/transform/rename_columns.py"""

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.seeds.transform.rename_columns import (
    COLUMNS_TO_RENAME,
    rename_columns,
)


def test_rename_columns() -> None:
    data = {column: [None] for column in COLUMNS_TO_RENAME}
    data["Keep me"] = ["value"]

    seeds = pl.DataFrame(data)

    expected = pl.DataFrame({
        **{new: [None] for new in COLUMNS_TO_RENAME.values()},
        "Keep me": ["value"],
    })

    result = rename_columns(seeds)

    assert_frame_equal(result, expected)

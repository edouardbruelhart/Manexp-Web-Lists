"""Tests for taxonomy/transform/filter_columns.py"""

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.taxonomy.transform.filter_columns import filter_columns


def test_filter_columns() -> None:
    taxonomy = pl.DataFrame({
        "crop_code": ["TOMAT"],
        "upov_short_code": ["TOM"],
        "crop_name": ["Tomato"],
    })

    expected = pl.DataFrame({
        "crop_code": ["TOMAT"],
        "crop_name": ["Tomato"],
    })

    result = filter_columns(taxonomy)

    assert_frame_equal(result, expected)

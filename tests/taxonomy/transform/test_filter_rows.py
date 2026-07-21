"""Tests for taxonomy/transform/filter_rows.py"""

from unittest.mock import patch

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.taxonomy.transform.filter_rows import filter_rows


def test_filter_rows() -> None:
    fake_seeds = pl.DataFrame({"upov_code": ["Test", "Test", "Test2", "Test3", "Test4"]})

    taxonomy = pl.DataFrame({"upov_code": ["Test", "Test2", "Test3", "Test5"]})

    with patch(
        "manexp_web_lists.taxonomy.transform.filter_rows.pl.read_parquet",
        return_value=fake_seeds,
    ):
        result = filter_rows(taxonomy)

    expected = pl.DataFrame({"upov_code": ["Test", "Test2", "Test3", "Test4"]})

    assert_frame_equal(result.sort(by="upov_code"), expected.sort(by="upov_code"))

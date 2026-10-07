from pathlib import Path
from unittest.mock import patch

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.seeds.transform.filter_taxonomy import filter_taxonomy


def test_filter_taxonomy() -> None:
    fake_seeds = pl.DataFrame({"taxon_id": ["Test", "Test", "Test2", "Test3", "Test4"]})

    taxonomy = pl.DataFrame({
        "upov_code": ["Test", "Test2", "Test3", "Test5"],
        "botanical_name": ["Test Plant", "Test Plant 2", "Test Plant 3", "Test Plant 5"],
        "column_to_drop": ["drop", "drop2", "drop3", "drop5"],
    })

    with patch(
        "manexp_web_lists.seeds.transform.filter_taxonomy.pl.read_parquet",
        return_value=fake_seeds,
    ):
        result = filter_taxonomy(taxonomy, Path("path/to/seed.parquet"))

    expected = pl.DataFrame({
        "botanical_name": ["Test Plant", "Test Plant 2", "Test Plant 3", None],
        "upov_code": ["Test", "Test2", "Test3", "Test4"],
    })

    assert_frame_equal(result.sort(by="upov_code"), expected.sort(by="upov_code"))

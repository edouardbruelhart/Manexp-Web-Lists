"""Tests for seeds/transform/remove_unnecessary_seeds.py"""

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.seeds.transform.remove_unnecessary_seeds import remove_unnecessary_seeds


def test_remove_unnecessary_seeds() -> None:

    seeds = seeds = pl.DataFrame([
        {"status": "Withdrawn", "value": "test"},
        {"status": "Rejected", "value": "test2"},
        {"status": "Surrendered", "value": "test3"},
        {"status": "Registered", "value": "test4"},
    ])

    expected = pl.DataFrame([{"status": "Surrendered", "value": "test3"}, {"status": "Registered", "value": "test4"}])

    result = remove_unnecessary_seeds(seeds)

    assert_frame_equal(result, expected)

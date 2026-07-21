"""Tests for taxonomy/transform/color_taxonomy.py"""

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.taxonomy.transform.color_taxonomy import color_taxonomy, text_to_color


def test_text_to_color():
    color = text_to_color("Test")
    assert color == "#46cf40"


def test_color_taxonomy() -> None:
    taxonomy = pl.DataFrame({"upov_code": "Test"})

    expected = pl.DataFrame({"upov_code": "Test", "color": "#46cf40"})

    result = color_taxonomy(taxonomy)

    assert_frame_equal(result, expected)

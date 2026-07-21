"""Tests for taxonomy/transform/iconize_taxonomy.py"""

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.taxonomy.transform.iconize_taxonomy import iconize_taxonomy


def test_iconize_taxonomy() -> None:

    taxonomy = pl.DataFrame({"genus": ["Quercus", "Triticum", "Zea", "Fragaria"]})

    result = iconize_taxonomy(taxonomy)

    expected = pl.DataFrame({"genus": ["Quercus", "Triticum", "Zea", "Fragaria"], "icon": ["🌳", "🌾", "🌽", "🍓"]})

    assert_frame_equal(result, expected)

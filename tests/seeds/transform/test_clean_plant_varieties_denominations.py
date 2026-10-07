import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.seeds.transform.clean_plant_varieties_denominations import (
    aggregate_denominations,
    clean_plant_varieties_denominations,
)


def test_aggregate_denominations() -> None:
    seeds = pl.DataFrame({
        "denomination": ["Alpha"],
        "conventional_denomination": ["  Alpha  "],
        "denomination_synonym": ["Beta"],
        "trade_name": ["Alpha"],  # duplicate
    })

    expected = pl.DataFrame({
        "denomination": ["Alpha"],
        "denomination_search": [["Alpha", "Beta"]],
        "synonyms": [["Beta"]],
    })

    result = aggregate_denominations(seeds)

    assert_frame_equal(result, expected)


def test_clean_plant_varieties_denominations() -> None:

    seeds = seeds = pl.DataFrame({
        "denomination": [" Alpha"],
        "conventional_denomination": ["  Alpha  "],
        "denomination_synonym": ["Beta ,Gamma / Delta"],
        "trade_name": ["Alpha"],  # duplicate
    })

    expected = pl.DataFrame({
        "denomination": ["Alpha"],
        "denomination_search": [["Alpha", "Beta", "Gamma", "Delta"]],
        "synonyms": [["Beta", "Gamma", "Delta"]],
    })

    result = clean_plant_varieties_denominations(seeds)

    assert_frame_equal(result, expected)

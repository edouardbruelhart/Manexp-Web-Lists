"""Tests for seeds/transform/clean_denominations.py"""

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.seeds.transform.clean_denominations import (
    aggregate_denominations,
    clean_denominations,
    parse_synonyms,
)


def test_parse_synonyms_success():
    result = parse_synonyms("test/test2,test3+test4")

    assert result == ["test", "test2", "test3", "test4"]


def test_parse_synonyms_none():
    result = parse_synonyms(None)

    assert result is None


def test_parse_synonyms_null():
    result = parse_synonyms(",")

    assert not result


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


def test_clean_denomination() -> None:

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

    result = clean_denominations(seeds)

    assert_frame_equal(result, expected)

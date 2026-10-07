import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.seeds.transform.translate_countries import translate_countries


def test_translate_countries() -> None:
    countries = pl.DataFrame({
        "alpha2": ["CH"],
    })

    expected = pl.DataFrame({
        "alpha2": ["CH"],
        "french": ["Suisse"],
        "german": ["Schweiz"],
        "italian": ["Svizzera"],
        "english": ["Switzerland"],
    })

    result = translate_countries(countries)

    assert_frame_equal(result, expected)

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.seeds.transform.filter_plant_varieties import filter_plant_varieties


def test_filter_plant_varieties() -> None:

    seeds = seeds = pl.DataFrame([
        {
            "Country / Org.": "CH",
            "Register Type": "NLI",
            "Register Subtype": "FRU",
            "UPOV Species Code": "TEST_TEST",
            "Variety Denomination": "test",
            "Variety Status": "Withdrawn",
            "GMO": "N",
            "Variety Denomination Synonym(s)": "synonym",
            "Conventional Denomination": "conventional",
            "Variety Trade Name(s)": "trade name",
            "Hybrid": "N",
            "Organic": "N",
            "UUID": "TEST_TEST/conventional/trade name",
        },
        {
            "Country / Org.": "CH",
            "Register Type": "NLI",
            "Register Subtype": "FRU",
            "UPOV Species Code": "TEST_TEST",
            "Variety Denomination": "test2",
            "Variety Status": "Rejected",
            "GMO": "N",
            "Variety Denomination Synonym(s)": "synonym",
            "Conventional Denomination": "conventional",
            "Variety Trade Name(s)": "trade name",
            "Hybrid": "N",
            "Organic": "N",
            "UUID": "TEST_TEST/conventional/trade name",
        },
        {
            "Country / Org.": "CH",
            "Register Type": "NLI",
            "Register Subtype": "FRU",
            "UPOV Species Code": "TEST_TEST",
            "Variety Denomination": "test3",
            "Variety Status": "Registered",
            "GMO": "N",
            "Variety Denomination Synonym(s)": "synonym",
            "Conventional Denomination": "conventional",
            "Variety Trade Name(s)": "trade name",
            "Hybrid": "N",
            "Organic": "N",
            "UUID": "TEST_TEST/conventional/trade name",
        },
        {
            "Country / Org.": "CH",
            "Register Type": "NLI",
            "Register Subtype": "FRU",
            "UPOV Species Code": "TEST_TEST",
            "Variety Denomination": "test4",
            "Variety Status": "Surrendered",
            "GMO": "N",
            "Variety Denomination Synonym(s)": "synonym",
            "Conventional Denomination": "conventional",
            "Variety Trade Name(s)": "trade name",
            "Hybrid": "N",
            "Organic": "N",
            "UUID": "TEST_TEST/conventional/trade name",
        },
    ])

    expected = pl.DataFrame([
        {
            "country": "CH",
            "register_type": "NLI",
            "register_subtype": "FRU",
            "taxon_id": "TEST_TEST",
            "denomination": "test3",
            "status": "Registered",
            "is_gmo": "N",
            "denomination_synonym": "synonym",
            "conventional_denomination": "conventional",
            "trade_name": "trade name",
            "is_hybrid": "N",
            "is_organic": "N",
            "id": "TEST_TEST/conventional/trade name",
        },
        {
            "country": "CH",
            "register_type": "NLI",
            "register_subtype": "FRU",
            "taxon_id": "TEST_TEST",
            "denomination": "test4",
            "status": "Surrendered",
            "is_gmo": "N",
            "denomination_synonym": "synonym",
            "conventional_denomination": "conventional",
            "trade_name": "trade name",
            "is_hybrid": "N",
            "is_organic": "N",
            "id": "TEST_TEST/conventional/trade name",
        },
    ])

    result = filter_plant_varieties(seeds)

    assert_frame_equal(result, expected)

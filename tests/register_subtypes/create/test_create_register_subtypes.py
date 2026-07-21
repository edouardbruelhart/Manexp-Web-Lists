import polars as pl

from manexp_web_lists.register_subtypes.create.create_register_subtypes import create_register_subtypes


def test_create_register_subtypes() -> None:

    register_subtypes = create_register_subtypes()

    assert len(register_subtypes) == 3
    assert set(register_subtypes.columns) == {
        "name",
        "abbreviation",
        "description",
    }

    # Spot checks
    fruit = register_subtypes.filter(pl.col("name") == "Fruit").row(0, named=True)
    assert fruit["name"] == "Fruit"
    assert fruit["abbreviation"] == "FRU"
    assert fruit["description"] == "Fruit genera and species register."

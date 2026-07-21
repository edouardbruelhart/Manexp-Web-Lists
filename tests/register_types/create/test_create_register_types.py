import polars as pl

from manexp_web_lists.register_types.create.create_register_types import create_register_types


def test_create_register_types() -> None:

    register_types = create_register_types()

    assert len(register_types) == 7
    assert set(register_types.columns) == {
        "name",
        "abbreviation",
        "description",
    }

    # Spot checks
    fruit = register_types.filter(pl.col("name") == "Frumatis").row(0, named=True)
    assert fruit["name"] == "Frumatis"
    assert fruit["abbreviation"] == "FRU"
    assert (
        fruit["description"] == "Varieties registered in the Fruit Reproductive Material Information System (FRUMATIS)."
    )

import polars as pl

from manexp_web_lists.seeds.transform.replace_plant_varieties_relations import (
    replace_plant_varieties_relations,
)


def test_replace_plant_varieties_relations() -> None:
    plant_varieties = pl.DataFrame({
        "name": ["Apple", "Pear", "Cherry"],
        "country": ["FR", "DE", "XX"],
        "register_type": ["AGR", "VEG", "XXX"],
        "register_subtype": ["FRU", "ORN", "XXX"],
    })

    countries = pl.DataFrame({
        "id": [1, 2],
        "alpha2": ["FR", "DE"],
        "name": ["France", "Germany"],
    })

    register_types = pl.DataFrame({
        "id": [10, 20],
        "abbreviation": ["AGR", "VEG"],
        "name": ["Agricultural", "Vegetable"],
    })

    register_subtypes = pl.DataFrame({
        "id": [100, 200],
        "abbreviation": ["FRU", "ORN"],
        "name": ["Fruit", "Ornamental"],
    })

    result = replace_plant_varieties_relations(
        plant_varieties,
        countries,
        register_types,
        register_subtypes,
    )

    expected = pl.DataFrame({
        "name": ["Apple", "Pear", "Cherry"],
        "country_id": [1, 2, None],
        "register_type_id": [10, 20, None],
        "register_subtype_id": [100, 200, None],
    })

    assert result.equals(expected)

import polars as pl

from manexp_web_lists.seeds.extract.create_register_subtypes import (
    create_register_subtypes,
)


def test_create_register_subtypes(tmp_path) -> None:
    seeds_path = tmp_path / "register_subtype.parquet"

    create_register_subtypes(seeds_path)

    # Verify that the Parquet file was created.
    assert seeds_path.exists()

    # Read the generated Parquet file.
    register_subtypes = pl.read_parquet(seeds_path)

    assert len(register_subtypes) == 3
    assert set(register_subtypes.columns) == {
        "id",
        "name",
        "abbreviation",
        "description",
    }

    # Spot checks
    fruit = register_subtypes.filter(pl.col("name") == "Fruit").row(0, named=True)

    assert fruit["id"] == 3
    assert fruit["name"] == "Fruit"
    assert fruit["abbreviation"] == "FRU"
    assert fruit["description"] == "Fruit genera and species register."

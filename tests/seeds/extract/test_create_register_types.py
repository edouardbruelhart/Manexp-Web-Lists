import polars as pl

from manexp_web_lists.seeds.extract.create_register_types import (
    create_register_types,
)


def test_create_register_types(tmp_path) -> None:
    seeds_path = tmp_path / "register_type.parquet"

    create_register_types(seeds_path)

    # Verify that the Parquet file was created.
    assert seeds_path.exists()

    # Read the generated Parquet file.
    register_types = pl.read_parquet(seeds_path)

    assert len(register_types) == 7
    assert set(register_types.columns) == {
        "id",
        "name",
        "abbreviation",
        "description",
    }

    # Spot checks
    frumatis = register_types.filter(pl.col("name") == "Frumatis").row(0, named=True)

    assert frumatis["id"] == 4
    assert frumatis["name"] == "Frumatis"
    assert frumatis["abbreviation"] == "FRU"
    assert (
        frumatis["description"]
        == "Varieties registered in the Fruit Reproductive Material Information System (FRUMATIS)."
    )

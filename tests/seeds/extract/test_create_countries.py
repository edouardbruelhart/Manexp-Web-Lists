import polars as pl

from manexp_web_lists.seeds.extract.create_countries import (
    create_countries,
)


def test_create_countries(tmp_path) -> None:
    seeds_path = tmp_path / "country.csv"

    create_countries(seeds_path)

    # Verify that the Parquet file was created.
    assert seeds_path.exists()

    # Read the generated Parquet file.
    countries = pl.read_csv(seeds_path)

    assert set(countries.columns) == {
        "id",
        "alpha2",
        "alpha3",
        "flag",
    }

    # Spot checks
    andorre = countries.filter(pl.col("alpha2") == "AD").row(0, named=True)

    assert andorre["id"] == 20

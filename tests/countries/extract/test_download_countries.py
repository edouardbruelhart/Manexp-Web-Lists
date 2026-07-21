from pathlib import Path

import polars as pl

from manexp_web_lists.countries.extract.download_countries import download_countries


def test_download_countries(tmp_path: Path) -> None:
    output = tmp_path / "countries.csv"

    download_countries(output)

    assert output.exists()

    df = pl.read_csv(output)

    assert len(df) > 200
    assert set(df.columns) == {
        "alpha2",
        "alpha3",
        "numeric",
        "flag",
    }

    # Spot checks
    ch = df.filter(pl.col("alpha2") == "CH").row(0, named=True)
    assert ch["alpha3"] == "CHE"
    assert ch["numeric"] == 756
    assert ch["flag"] == "🇨🇭"

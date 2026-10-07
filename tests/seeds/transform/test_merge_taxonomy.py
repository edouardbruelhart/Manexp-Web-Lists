from pathlib import Path
from unittest.mock import patch

import polars as pl

from manexp_web_lists.seeds.transform.merge_taxonomy import merge_taxonomy


def test_merge_taxonomy(tmp_path: Path) -> None:
    first_csv = tmp_path / "first.csv"
    second_csv = tmp_path / "second.csv"
    output_file = tmp_path / "merged.csv"

    first_csv.write_text(
        """upov_code,name
A01,Apple
A02,Pear
"""
    )

    second_csv.write_text(
        """upov_code,name
A01,Apple updated
A02,Pear updated
A03,Cherry
"""
    )
    with (
        patch("manexp_web_lists.seeds.transform.merge_taxonomy.FILES", new=[first_csv, second_csv]),
    ):
        merge_taxonomy(tmp_path, output_file)

    result = pl.read_csv(output_file)

    print(result)

    expected = pl.DataFrame({
        "upov_code": ["A01", "A02", "A03"],
        "name": ["Apple", "Pear", "Cherry"],
    })

    print(expected)

    assert result.equals(expected)

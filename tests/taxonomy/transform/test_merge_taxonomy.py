from pathlib import Path

import polars as pl

from manexp_web_lists.taxonomy.transform.merge_taxonomy import merge_taxonomy


def test_merge_taxonomy(tmp_path: Path) -> None:
    first_csv = tmp_path / "first.csv"
    second_csv = tmp_path / "second.csv"
    output_csv = tmp_path / "merged.csv"

    first_csv.write_text(
        """upov_code,name,category
A01,Apple,Fruit
A02,Pear,Fruit
"""
    )

    second_csv.write_text(
        """upov_code,name,status
A01,Apple updated,active
A02,Pear updated,inactive
"""
    )

    merge_taxonomy(
        file_paths=[first_csv, second_csv],
        output_path=output_csv,
    )

    result = pl.read_csv(output_csv)

    expected = pl.DataFrame({
        "upov_code": ["A01", "A02"],
        "name": ["Apple", "Pear"],
        "category": ["Fruit", "Fruit"],
        "status": ["active", "inactive"],
    })

    assert result.equals(expected)

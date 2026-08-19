from pathlib import Path

import polars as pl


def merge_taxonomy(file_paths: list[Path], output_path: Path) -> None:
    """
    Merge the taxonomy CSVs

    Args:
        file_paths: The list of file paths
        output_path: The output path where to store the merged CSV
    """

    # The key column
    merge_key = "upov_code"

    # Use the first CSV as authoritative in case of overlaps
    result = pl.read_csv(file_paths[0])

    # Loop over the rest of the files
    for path in file_paths[1:]:
        other = pl.read_csv(path)

        # Extract columns that are not in the authoritative CSV and the upov_code column
        new_columns = [column for column in other.columns if column == merge_key or column not in result.columns]

        # Filter the columns
        other = other.select(new_columns)

        result = result.join(
            other,
            on=merge_key,
            how="left",
        )

    result.write_csv(output_path)

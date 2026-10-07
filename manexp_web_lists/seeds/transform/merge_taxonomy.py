from pathlib import Path

import polars as pl

from ..extract.download_taxonomy import FILES


def merge_taxonomy(seeds_path: Path, output_file: Path) -> None:
    """
    Merge the taxonomy CSVs.

    The first CSV is authoritative in case of duplicate upov_codes.
    New upov_codes from subsequent CSVs are added.

    Args:
        seeds_path: The path to seeds files folder.
        output_file: The path to output file.
    """

    merge_key = "upov_code"

    result = pl.read_csv(seeds_path / FILES[0])

    for file in FILES[1:]:
        other = pl.read_csv(seeds_path / file)

        new_rows = other.join(
            result.select(merge_key),
            on=merge_key,
            how="anti",
        )

        result = pl.concat(
            [result, new_rows],
            how="diagonal_relaxed",
        )

    result.write_csv(output_file)

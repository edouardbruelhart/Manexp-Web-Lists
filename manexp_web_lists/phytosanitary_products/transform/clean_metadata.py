from pathlib import Path

import polars as pl

from manexp_web_lists.clients import translate
from manexp_web_lists.core import parse_strings_to_list

from .parsers import metadata_parser

METADATA_TO_CLEAN = [
    "application_area.xml",
    "application_comment.xml",
    "code_r.xml",
    "code_s.xml",
    "culture_additional_text.xml",
    "culture_form.xml",
    "culture.xml",
    "danger_symbol.xml",
    "formulation_code.xml",
    "measure.xml",
    "obligation.xml",
    "pest_additional_text.xml",
    "pest.xml",
    "product_category.xml",
    "signal_words.xml",
    "time_measure.xml",
]


def clean_metadata(phyto_path: Path) -> None:
    """
    Clean metadata, rename columns and write them as parquet files

    Args:
        phyto_path: The path to the metadata files folder
    """

    for file in METADATA_TO_CLEAN:
        # Load data
        metadata = metadata_parser(phyto_path / file)

        # Rename columns
        renamed_metadata = metadata.rename({
            "primaryKey": "id",
            "fr": "french",
            "de": "german",
            "it": "italian",
            "en": "english",
        })

        # Get english translation when lacking
        translated_metadata = renamed_metadata.with_columns(
            pl
            .when(pl.col("english").is_null() | (pl.col("english") == "") | (pl.col("english") == " "))
            .then(
                pl.col("french").map_elements(
                    lambda french: translate(
                        french,
                        src_lang="fr",
                        dest_lang="en",
                    ),
                    return_dtype=pl.String,
                )
            )
            .otherwise(pl.col("english"))
            .alias("english")
        )

        # Parse codes into list of strings instead of strings
        if file == "code_r.xml" or file == "code_s.xml":
            parsed_metadata = translated_metadata.with_columns(
                pl
                .col("code")
                .map_elements(
                    parse_strings_to_list,
                    return_dtype=pl.List(pl.String),
                )
                .fill_null(pl.lit([], dtype=pl.List(pl.String)))
            )

            # Rename files and write parquet
            filename = "r_code.parquet" if file == "code_r.xml" else "s_code.parquet"
            parsed_metadata.write_parquet(phyto_path / filename)

        else:
            # Write parquet
            translated_metadata.write_parquet(phyto_path / file.replace(".xml", ".parquet"))

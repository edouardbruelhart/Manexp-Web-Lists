from pathlib import Path
from unittest.mock import patch

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.phytosanitary_products.transform.clean_metadata import (
    METADATA_TO_CLEAN,
    clean_metadata,
)


def test_clean_metadata(tmp_path: Path) -> None:
    metadata = pl.DataFrame({
        "primaryKey": ["metadata-1", "metadata-2"],
        "fr": ["Texte français 1", "Texte français 2"],
        "de": ["Deutscher Text 1", "Deutscher Text 2"],
        "it": ["Testo italiano 1", "Testo italiano 2"],
        "en": ["English text 1", ""],
    })

    code_metadata = pl.DataFrame({
        "primaryKey": ["code-1", "code-2"],
        "fr": ["Texte français 1", "Texte français 2"],
        "de": ["Deutscher Text 1", "Deutscher Text 2"],
        "it": ["Testo italiano 1", "Testo italiano 2"],
        "en": ["English text 1", ""],
        "code": ["R1/R2", "S1+S2"],
    })

    def mock_metadata_parser(filename: Path) -> pl.DataFrame:
        if filename.name in {"code_r.xml", "code_s.xml"}:
            return code_metadata

        return metadata

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.transform.clean_metadata.metadata_parser",
            side_effect=mock_metadata_parser,
        ) as mock_parser,
        patch(
            "manexp_web_lists.phytosanitary_products.transform.clean_metadata.translate",
            return_value="Translated English text",
        ) as mock_translate,
    ):
        clean_metadata(tmp_path)

    assert mock_parser.call_count == len(METADATA_TO_CLEAN)

    expected_parser_calls = [(tmp_path / filename,) for filename in METADATA_TO_CLEAN]

    actual_parser_calls = [call.args for call in mock_parser.call_args_list]

    assert actual_parser_calls == expected_parser_calls

    mock_translate.assert_any_call(
        "Texte français 2",
        src_lang="fr",
        dest_lang="en",
    )

    expected_metadata = pl.DataFrame({
        "id": ["metadata-1", "metadata-2"],
        "french": ["Texte français 1", "Texte français 2"],
        "german": ["Deutscher Text 1", "Deutscher Text 2"],
        "italian": ["Testo italiano 1", "Testo italiano 2"],
        "english": [
            "English text 1",
            "Translated English text",
        ],
    })

    for filename in METADATA_TO_CLEAN:
        if filename in {"code_r.xml", "code_s.xml"}:
            continue

        output_filename = filename.replace(".xml", ".parquet")

        result = pl.read_parquet(tmp_path / output_filename)

        assert_frame_equal(
            result,
            expected_metadata,
            check_row_order=False,
        )

    expected_r_code = pl.DataFrame({
        "id": ["code-1", "code-2"],
        "french": ["Texte français 1", "Texte français 2"],
        "german": ["Deutscher Text 1", "Deutscher Text 2"],
        "italian": ["Testo italiano 1", "Testo italiano 2"],
        "english": [
            "English text 1",
            "Translated English text",
        ],
        "code": [
            ["R1", "R2"],
            ["S1", "S2"],
        ],
    })

    result_r_code = pl.read_parquet(tmp_path / "r_code.parquet")

    assert_frame_equal(
        result_r_code,
        expected_r_code,
        check_row_order=False,
    )

    result_s_code = pl.read_parquet(tmp_path / "s_code.parquet")

    assert_frame_equal(
        result_s_code,
        expected_r_code,
        check_row_order=False,
    )

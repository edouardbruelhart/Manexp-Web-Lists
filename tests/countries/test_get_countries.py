"""Tests for countries/get_countries.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.countries.get_countries import get_countries


def test_get_countries() -> None:
    raw_df = MagicMock()
    translated_df = MagicMock()

    with (
        patch("manexp_web_lists.countries.get_countries.download_countries") as mock_download,
        patch(
            "manexp_web_lists.countries.get_countries.pl.read_csv",
            return_value=raw_df,
        ) as mock_read_csv,
        patch(
            "manexp_web_lists.countries.get_countries.translate_countries",
            return_value=translated_df,
        ) as mock_translate,
    ):
        get_countries()

    mock_download.assert_called_once()
    mock_read_csv.assert_called_once()
    mock_translate.assert_called_once_with(raw_df)
    translated_df.write_parquet.assert_called_once()

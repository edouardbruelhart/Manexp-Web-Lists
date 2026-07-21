from pathlib import Path
from unittest.mock import MagicMock, patch

from manexp_web_lists.taxonomy.get_taxonomy import get_taxonomy


def test_get_taxonomy() -> None:
    raw_df = MagicMock()
    filtered_columns_df = MagicMock()
    filtered_rows_df = MagicMock()
    cleaned_df = MagicMock()
    iconized_df = MagicMock()
    colored_df = MagicMock()

    with (
        patch("manexp_web_lists.taxonomy.get_taxonomy.download_taxonomy") as mock_download,
        patch(
            "manexp_web_lists.countries.get_countries.pl.read_csv",
            return_value=raw_df,
        ) as mock_read_csv,
        patch(
            "manexp_web_lists.taxonomy.get_taxonomy.filter_columns", return_value=filtered_columns_df
        ) as mock_filter_columns,
        patch("manexp_web_lists.taxonomy.get_taxonomy.filter_rows", return_value=filtered_rows_df) as mock_filter_rows,
        patch("manexp_web_lists.taxonomy.get_taxonomy.clean_taxonomy", return_value=cleaned_df) as mock_clean,
        patch("manexp_web_lists.taxonomy.get_taxonomy.iconize_taxonomy", return_value=iconized_df) as mock_iconize,
        patch("manexp_web_lists.taxonomy.get_taxonomy.color_taxonomy", return_value=colored_df) as mock_color,
    ):
        # Call the get_taxonomy function
        get_taxonomy()

    # Assert that each function was called
    mock_download.assert_called_once_with(
        "https://www.upov.int/genie/updates/upov_code.xhtml?lang=en", Path("./taxonomy/lists/raw_taxonomy.csv")
    )
    mock_read_csv.assert_called_once()
    mock_filter_columns.assert_called_once()
    mock_filter_rows.assert_called_once()
    mock_clean.assert_called_once()
    mock_color.assert_called_once()
    mock_iconize.assert_called_once()

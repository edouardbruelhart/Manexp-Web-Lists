from unittest.mock import MagicMock, patch

from manexp_web_lists.seeds.get_seeds import get_seeds


def test_get_seeds() -> None:
    raw_df = MagicMock()
    filtered_df = MagicMock()
    renamed_df = MagicMock()
    removed_df = MagicMock()
    boolean_df = MagicMock()
    aggregated_df = MagicMock()

    with (
        patch("manexp_web_lists.seeds.get_seeds.download_seeds") as mock_download,
        patch(
            "manexp_web_lists.seeds.get_seeds.pl.read_excel",
            return_value=raw_df,
        ) as mock_read_excel,
        patch(
            "manexp_web_lists.seeds.get_seeds.filter_columns",
            return_value=filtered_df,
        ) as mock_filter,
        patch(
            "manexp_web_lists.seeds.get_seeds.rename_columns",
            return_value=renamed_df,
        ) as mock_rename,
        patch(
            "manexp_web_lists.seeds.get_seeds.remove_unnecessary_seeds",
            return_value=removed_df,
        ) as mock_remove,
        patch(
            "manexp_web_lists.seeds.get_seeds.clean_booleans",
            return_value=boolean_df,
        ) as mock_boolean,
        patch(
            "manexp_web_lists.seeds.get_seeds.clean_denominations",
            return_value=aggregated_df,
        ) as mock_aggregate,
    ):
        get_seeds()

    mock_download.assert_called_once()
    mock_read_excel.assert_called_once()
    mock_filter.assert_called_once_with(raw_df)
    mock_rename.assert_called_once_with(filtered_df)
    mock_remove.assert_called_once_with(renamed_df)
    mock_boolean.assert_called_once_with(removed_df)
    mock_aggregate.assert_called_once_with(boolean_df)
    aggregated_df.write_parquet.assert_called_once()

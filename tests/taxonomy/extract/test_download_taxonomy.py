from pathlib import Path
from unittest.mock import MagicMock, patch

from manexp_web_lists.taxonomy.extract.download_taxonomy import download_taxonomy


def test_download_taxonomy() -> None:
    with (
        patch("manexp_web_lists.taxonomy.extract.download_taxonomy.sync_playwright") as mock_sync,
        patch("polars.DataFrame", autospec=True) as mock_df,
    ):
        # Context manager
        playwright = MagicMock()
        mock_sync.return_value.__enter__.return_value = playwright

        browser = MagicMock()
        context = MagicMock()
        page = MagicMock()
        locator = MagicMock()

        playwright.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page
        page.locator.return_value = locator
        mock_df.return_value.write_csv = MagicMock()

        # Mock the evaluate_all method to return the expected records
        records = [["UP01", "Botanical Name 1", "UP01"], ["UP02", "Botanical Name 2", "UP02"]]
        locator.evaluate_all.return_value = records

        download_taxonomy(["https://example.com"], [Path("file.csv")], ["upov_code", "botanical_name"])

        page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="domcontentloaded",
        )

        mock_df.assert_called_once()

        mock_df.return_value.write_csv.assert_called_once()

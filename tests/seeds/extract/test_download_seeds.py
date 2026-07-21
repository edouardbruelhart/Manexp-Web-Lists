from pathlib import Path
from unittest.mock import MagicMock, patch

from manexp_web_lists.seeds.extract.download_seeds import download_seeds


def test_download_seeds() -> None:
    with (
        patch("manexp_web_lists.seeds.extract.download_seeds.sync_playwright") as mock_sync,
        patch("manexp_web_lists.seeds.extract.download_seeds.expect"),
    ):
        # Context manager
        playwright = MagicMock()
        mock_sync.return_value.__enter__.return_value = playwright

        browser = MagicMock()
        context = MagicMock()
        page = MagicMock()
        locator = MagicMock()
        download = MagicMock()

        playwright.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page
        page.locator.return_value = locator

        download_ctx = MagicMock()
        download_ctx.__enter__.return_value = download_ctx
        download_ctx.value = download
        page.expect_download.return_value = download_ctx

        download_seeds("https://example.com", Path("file.xlsx"))

        page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="domcontentloaded",
        )

        page.locator.assert_called_once()
        locator.click.assert_called_once()
        download.save_as.assert_called_once_with(Path("file.xlsx"))
        context.close.assert_called_once()
        browser.close.assert_called_once()

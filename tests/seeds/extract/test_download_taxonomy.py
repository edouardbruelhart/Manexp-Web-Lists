from unittest.mock import MagicMock, patch

from manexp_web_lists.seeds.extract.download_taxonomy import (
    COLUMNS,
    FILES,
    URLS,
    download_taxonomy,
)


def test_download_taxonomy(tmp_path) -> None:
    with (
        patch("manexp_web_lists.seeds.extract.download_taxonomy.sync_playwright") as mock_sync,
        patch("manexp_web_lists.seeds.extract.download_taxonomy.pl.DataFrame") as mock_dataframe,
    ):
        playwright = MagicMock()
        mock_sync.return_value.__enter__.return_value = playwright

        browsers = []
        pages = []

        for index, schema in enumerate(COLUMNS):
            browser = MagicMock()
            context = MagicMock()
            page = MagicMock()

            browser.new_context.return_value = context
            context.new_page.return_value = page

            page.locator.return_value.evaluate_all.return_value = [[f"value-{index}-{column}" for column in schema]]

            browsers.append(browser)
            pages.append(page)

        # Each call to chromium.launch() returns the next browser.
        playwright.chromium.launch.side_effect = browsers

        taxonomies = [MagicMock() for _ in URLS]
        mock_dataframe.side_effect = taxonomies

        download_taxonomy(tmp_path)

    # One Playwright session and browser per URL.
    assert mock_sync.call_count == len(URLS)
    assert playwright.chromium.launch.call_count == len(URLS)

    # Verify every configured source.
    for index, (url, schema, filename) in enumerate(zip(URLS, COLUMNS, FILES, strict=True)):
        browser = browsers[index]
        context = browser.new_context.return_value
        page = pages[index]
        taxonomy = taxonomies[index]

        browser.new_context.assert_called_once_with(
            viewport={"width": 1920, "height": 1080},
        )

        context.new_page.assert_called_once_with()

        page.goto.assert_called_once_with(
            url,
            wait_until="domcontentloaded",
        )

        page.locator.assert_called_once_with(
            "table tbody tr",
        )

        page.locator.return_value.evaluate_all.assert_called_once()

        mock_dataframe.assert_any_call(
            [[f"value-{index}-{column}" for column in schema]],
            schema=schema,
            orient="row",
        )

        taxonomy.write_csv.assert_called_once_with(
            tmp_path / filename,
        )

        context.close.assert_called_once_with()
        browser.close.assert_called_once_with()

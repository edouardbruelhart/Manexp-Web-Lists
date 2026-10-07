from unittest.mock import MagicMock, patch

from manexp_web_lists.seeds.extract.download_plant_varieties import (
    download_plant_varieties,
)


def test_download_plant_varieties(tmp_path) -> None:
    output_path = tmp_path / "plant_varieties.csv"

    with (
        patch("manexp_web_lists.seeds.extract.download_plant_varieties.sync_playwright") as mock_sync,
        patch("manexp_web_lists.seeds.extract.download_plant_varieties.expect") as mock_expect,
        patch("manexp_web_lists.seeds.extract.download_plant_varieties.pl.read_excel") as mock_read_excel,
    ):
        playwright = MagicMock()
        browser = MagicMock()
        context = MagicMock()
        page = MagicMock()

        mock_sync.return_value.__enter__.return_value = playwright
        playwright.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page

        # Locator chain
        result_table = MagicMock()
        export_locator = MagicMock()
        export_btn = MagicMock()

        page.locator.return_value = result_table
        result_table.locator.return_value = export_locator
        export_locator.filter.return_value = export_btn

        # Download
        download = MagicMock()
        download.path.return_value = tmp_path / "download.xlsx"

        download_info = MagicMock()
        download_info.value = download

        page.expect_download.return_value = download_info

        # Polars
        plant_varieties = MagicMock()
        mock_read_excel.return_value = plant_varieties

        download_plant_varieties(output_path)

    playwright.chromium.launch.assert_called_once_with()

    browser.new_context.assert_called_once_with(
        viewport={"width": 1920, "height": 1080},
    )

    context.new_page.assert_called_once_with()

    page.goto.assert_called_once_with(
        "https://ec.europa.eu/food/plant-variety-portal/index.xhtml",
        wait_until="domcontentloaded",
    )

    page.locator.assert_called_once_with(
        "#searchForm\\:result_datatable",
    )

    result_table.locator.assert_called_once_with(
        "a.btn.btn-success",
    )

    export_locator.filter.assert_called_once_with(
        has_text="EU Variety List",
    )

    mock_expect.assert_called_once_with(export_btn)
    mock_expect.return_value.to_be_visible.assert_called_once_with(
        timeout=60000,
    )

    page.expect_download.assert_called_once_with(
        timeout=90000,
    )

    export_btn.click.assert_called_once()

    mock_read_excel.assert_called_once()

    plant_varieties.write_csv.assert_called_once_with(
        output_path,
    )

    context.close.assert_called_once_with()
    browser.close.assert_called_once_with()

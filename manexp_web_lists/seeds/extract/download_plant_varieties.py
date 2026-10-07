from pathlib import Path

import polars as pl
from playwright.sync_api import expect, sync_playwright

URL = "https://ec.europa.eu/food/plant-variety-portal/index.xhtml"


def download_plant_varieties(raw_plant_varieties_path: Path) -> None:
    """
    Download the official european plant varieties list as a CSV file from the internet.

    Args:
        raw_plant_varieties_path: the path where to save the file
    """
    with sync_playwright() as p:
        # Open browser session
        browser = p.chromium.launch()

        try:
            # Create context with a large enough screen to not mask any element
            context = browser.new_context(viewport={"width": 1920, "height": 1080})

            # Open a new page
            page = context.new_page()

            # 1. Navigate
            page.goto(URL, wait_until="domcontentloaded")

            # 2. Identify export button
            result_table = page.locator("#searchForm\\:result_datatable")

            export_btn = result_table.locator(
                "a.btn.btn-success",
            ).filter(
                has_text="EU Variety List",
            )

            # 3. Handle Download
            expect(export_btn).to_be_visible(timeout=60000)  # Check that button is visible
            with page.expect_download(timeout=90000) as download_info:
                export_btn.click()

            # 4. Convert excel to CSV and save file
            download = download_info.value
            plant_varieties = pl.read_excel(download.path())
            plant_varieties.write_csv(raw_plant_varieties_path)

            # Close context
            context.close()
        finally:
            # Close browser
            browser.close()

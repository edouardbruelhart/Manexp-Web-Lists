from pathlib import Path

import polars as pl
from playwright.sync_api import sync_playwright


def download_taxonomy(url: str, file_path: Path) -> None:
    """
    Download the official UPOV taxonomy from the internet.

    Args:
        url: The url of the page to download
        file_path: the path where to save the file
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
            page.goto(url, wait_until="domcontentloaded")

            # 2. Get information
            records = page.locator("table tbody tr").evaluate_all("""
            rows => rows.map(row =>
                [...row.querySelectorAll("td")].map(td => td.innerText)
            )
            """)

            taxonomy = pl.DataFrame(
                records,
                schema=[
                    "upov_code",
                    "botanical_name",
                    "upov_short_code",
                ],
                orient="row",
            )

            taxonomy.write_csv(file_path)

            # Close context
            context.close()
        finally:
            # Close browser
            browser.close()

from pathlib import Path

import polars as pl
from playwright.sync_api import sync_playwright


def download_taxonomy(urls: list[str], file_paths: list[Path], columns: list[list[str]]) -> None:
    """
    Download the official UPOV taxonomy from the internet.

    Args:
        urls: The urls of the page to download
        file_paths: the paths where to save the file
        columns: the columns corresponding to the different CSVs
    """

    for index, url in enumerate(urls):
        schema = columns[index]

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

                # Remove rows that don't match the schema
                records = [row for row in records if len(row) == len(schema)]

                taxonomy = pl.DataFrame(
                    records,
                    schema=schema,
                    orient="row",
                )

                taxonomy.write_csv(file_paths[index])

                # Close context
                context.close()
            finally:
                # Close browser
                browser.close()

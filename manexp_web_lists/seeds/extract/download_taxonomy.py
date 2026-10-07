from pathlib import Path

import polars as pl
from playwright.sync_api import sync_playwright

# The first source is autoritative in case of duplicates
URLS = [
    "https://www.upov.int/genie/reports/twp.xhtml?faces-redirect=true",
    "https://www.upov.int/genie/updates/upov_code.xhtml?lang=en",
]

FILES = ["raw_taxonomy_reports.csv", "raw_taxonomy_updates.csv"]

COLUMNS = [
    [
        "upov_code",
        "botanical_name",
        "english",
        "french",
        "german",
        "spanish",
        "agriculture",
        "fruit",
        "ornamental",
        "forest",
        "vegetable",
    ],
    [
        "upov_code",
        "botanical_name",
        "upov_short_code",
    ],
]


def download_taxonomy(seeds_path: Path) -> None:
    """
    Download the official UPOV taxonomy from the internet.

    Args:
        seeds_path: the path where to save the files
    """

    for index, url in enumerate(URLS):
        schema = COLUMNS[index]

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

                taxonomy.write_csv(seeds_path / FILES[index])

                # Close context
                context.close()
            finally:
                # Close browser
                browser.close()

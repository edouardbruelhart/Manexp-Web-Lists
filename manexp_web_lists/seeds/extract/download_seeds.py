from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def download_seeds(url: str, file_path: Path) -> None:
    """
    Download the official european seeds list as an Excel file from the internet.

    Args:
        url: The url of the Excel to download
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

            # 2. Define Locator
            export_btn = page.locator("#searchForm\\:result_datatable\\:j_idt117")

            # 3. Handle Download
            expect(export_btn).to_be_visible(timeout=60000)  # Check that button is visible
            with page.expect_download(timeout=90000) as download_info:
                export_btn.click()

            # 4. Save File
            download = download_info.value
            download.save_as(file_path)

            # Close context
            context.close()
        finally:
            # Close browser
            browser.close()

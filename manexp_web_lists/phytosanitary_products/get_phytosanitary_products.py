from pathlib import Path

from .extract.download_phytosanitary_products import download_phytosanitary_products

PHYTO_URL = "https://www.blv.admin.ch/dam/fr/sd-web/He9bAfs8CmFT/daten-pflanzenschutzmittelverzeichnis-fr.zip"
PHYTO_PATH = Path("./phytosanitary_products/lists")


def get_phytosanitary_products() -> None:
    """Function to fetch, enrich and validate official swiss phytosanitary products list."""

    download_phytosanitary_products(PHYTO_URL, PHYTO_PATH)

from pathlib import Path

from .extract.download_phytosanitary_products import download_phytosanitary_products
from .transform.extract_indications import extract_indications
from .transform.merge_phyto import merge_phyto

PHYTO_URL = "https://www.blv.admin.ch/dam/fr/sd-web/He9bAfs8CmFT/daten-pflanzenschutzmittelverzeichnis-fr.zip"
PHYTO_PATH = Path("./phytosanitary_products/lists")


def get_phytosanitary_products() -> None:
    """Function to fetch, enrich and validate official swiss phytosanitary products list."""

    # Download phytosanitary products and split the xml in multiple ones
    download_phytosanitary_products(PHYTO_URL, PHYTO_PATH)

    # Merge products and parallel imports
    merge_phyto(PHYTO_PATH)

    # Extract indications from products
    extract_indications(PHYTO_PATH)

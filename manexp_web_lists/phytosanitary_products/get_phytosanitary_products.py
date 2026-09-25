from pathlib import Path

from .extract.download_phytosanitary_products import download_phytosanitary_products
from .extract.extract_indications import extract_indications
from .transform.clean_indications import clean_indications
from .transform.clean_metadata import clean_metadata
from .transform.clean_products import clean_products
from .transform.merge_phyto import merge_phyto

PHYTO_URL = "https://www.blv.admin.ch/dam/fr/sd-web/He9bAfs8CmFT/daten-pflanzenschutzmittelverzeichnis-fr.zip"
LISTS_PATH = Path("./phytosanitary_products/lists")


def get_phytosanitary_products() -> None:
    """Function to fetch, enrich and validate official swiss phytosanitary products list."""

    # Create lists path if it doesn't exist
    LISTS_PATH.mkdir(parents=True, exist_ok=True)

    # Download phytosanitary products and split the xml in multiple ones
    download_phytosanitary_products(PHYTO_URL, LISTS_PATH)

    # Merge products and parallel imports
    merge_phyto(LISTS_PATH)

    # Extract indications from products
    extract_indications(LISTS_PATH)

    # Clean and build metadata tables
    clean_metadata(LISTS_PATH)

    # Clean and build products tables
    clean_products(LISTS_PATH)

    # Clean and build indications tables
    clean_indications(LISTS_PATH)

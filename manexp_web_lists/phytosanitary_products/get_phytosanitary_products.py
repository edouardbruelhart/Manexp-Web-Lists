from pathlib import Path

from .extract.download_phytosanitary_products import download_phytosanitary_products
from .extract.extract_indications import extract_indications
from .load.load_phytosanitary_products import load_phytosanitary_products
from .transform.clean_indications import clean_indications
from .transform.clean_metadata import clean_metadata
from .transform.clean_products import clean_products
from .transform.merge_phyto import merge_phyto

PHYTO_URL = "https://www.blv.admin.ch/dam/fr/sd-web/He9bAfs8CmFT/daten-pflanzenschutzmittelverzeichnis-fr.zip"
FILES_PATH = Path("./phytosanitary_products/files")


def get_phytosanitary_products() -> None:
    """Function to fetch, enrich, validate and load official swiss phytosanitary products lists."""

    # Create lists path if it doesn't exist
    FILES_PATH.mkdir(parents=True, exist_ok=True)

    # Download phytosanitary products and split the xml in multiple ones
    download_phytosanitary_products(PHYTO_URL, FILES_PATH)

    # Merge products and parallel imports
    merge_phyto(FILES_PATH)

    # Extract indications from products
    extract_indications(FILES_PATH)

    # Clean and build metadata tables
    clean_metadata(FILES_PATH)

    # Clean and build products tables
    clean_products(FILES_PATH)

    # Clean and build indications tables
    clean_indications(FILES_PATH)

    # Load data into PostgreSQL
    load_phytosanitary_products(FILES_PATH)

    # Clean files folder
    for item in FILES_PATH.iterdir():
        item.unlink()

import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import requests
from defusedxml.ElementTree import parse

from manexp_web_lists.exceptions import InvalidXMLError

FILES_TO_DOWNLOAD = {
    0: "phytosanitary_products.xml",
    1: "parallel_import_phytosanitary_products.xml",
    2: "countries.xml",
    3: "culture_additionals.xml",
    4: "culture_forms.xml",
    5: "ingredient_additionals.xml",
    6: "application_areas.xml",
    7: "pest_additionals.xml",
    8: "substances.xml",
    9: "pests.xml",
    10: "cities.xml",
    11: "r_codes.xml",
    12: "formulation_codes.xml",
    13: "product_categories.xml",
    14: "signal_words.xml",
    15: "s_codes.xml",
    16: "danger_symbols.xml",
    17: "units.xml",
    18: "application_comments.xml",
    19: "periods.xml",
    20: "cultures.xml",
    21: "obligations.xml",
    22: "permission_holders.xml",
}


def download_zip(url: str) -> io.BytesIO:
    """section = root[index]

    tree = ET.ElementTree(section)

    tree.write(
        output_dir / filename,
        encoding="utf-8",
        xml_declaration=True,
    Download zip folder.

    Args:
        url: The url of the zip to download

    Returns:
        io.BytesIO: The downloaded zip
    """

    # Request
    with requests.Session() as session:
        response = session.get(url)
    response.raise_for_status()

    return io.BytesIO(response.content)


def extract_zip(byte: io.BytesIO) -> dict[str, io.BytesIO]:
    """
    Extract zip folder.

    Args:
        byte: The zip to extract

    Returns:
        dict[str, io.BytesIO]: The extracted content of the zip
    """
    with zipfile.ZipFile(byte) as archive:
        return {name: io.BytesIO(archive.read(name)) for name in archive.namelist()}


def download_phytosanitary_products(url: str, path: Path) -> None:
    """
    Download the official swiss phytosanitary products list from the internet.

    Args:
        url: The url of the phytosanitary products list
        path: The path where to store phyto lists

    Raises:
        InvalidXMLError: When empty xml is met
    """
    # Download zip
    byte = download_zip(url)

    # Extract files
    files = extract_zip(byte)

    # Get interesting data
    data = files["PublicationData.xml"]

    tree = parse(data)
    root = tree.getroot()

    # Check that xml is not empty
    if root is None:
        raise InvalidXMLError

    for index, filename in FILES_TO_DOWNLOAD.items():
        wrapper = ET.Element("Data")
        wrapper.append(root[index])

        ET.ElementTree(wrapper).write(
            path / filename,
            encoding="utf-8",
            xml_declaration=True,
        )

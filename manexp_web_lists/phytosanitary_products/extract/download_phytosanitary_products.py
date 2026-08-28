import io
import re
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree.ElementTree import ElementTree

import requests

from manexp_web_lists.exceptions import InvalidXMLError

from ..transform.parsers import parse_xml_root


def download_zip(url: str) -> io.BytesIO:
    """
    Download a zip file from a url

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

    root = parse_xml_root(data)

    # Iterate through each section of the xmla
    for section in root:
        # Make a copy so the original XML tree is not modified
        section = deepcopy(section)

        # Basic section name
        name = section.tag

        if section.tag == "MetaData" and "name" in section.attrib:
            name = section.attrib["name"]

            # Change MetaData into <ApplicationArea>
            section.tag = name

            # Remove metadata-specific attributes
            section.attrib.pop("name", None)
            section.attrib.pop("numberOfRows", None)

        else:
            # Normal sections:
            # <Products numberOfProducts="1710">
            name = section.tag

            # Remove section-specific count attributes
            section.attrib.pop("numberOfProducts", None)
            section.attrib.pop("numberOfParallelimports", None)

        # Convert CamelCase to snake_case
        filename = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower() + ".xml"

        # Create a new XML document with this section as the root
        new_tree = ElementTree(section)

        try:
            new_tree.write(path / filename, encoding="utf-8", xml_declaration=True)
        except IndexError as exc:
            raise InvalidXMLError() from exc

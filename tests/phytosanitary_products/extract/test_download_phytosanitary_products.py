import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from defusedxml.ElementTree import parse

from manexp_web_lists.exceptions import InvalidXMLError
from manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products import (
    download_phytosanitary_products,
    download_zip,
    extract_zip,
)


def test_download_zip_success():
    data = b"PK\x03\x04fake zip content"

    mock_response = MagicMock()
    mock_response.content = data

    session = MagicMock()
    session.get.return_value = mock_response

    session_factory = MagicMock()
    session_factory.__enter__.return_value = session
    session_factory.__exit__.return_value = None

    with patch(
        "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.requests.Session",
        return_value=session_factory,
    ):
        result = download_zip("https://example.com/archive.zip")

    assert isinstance(result, io.BytesIO)
    assert result.getvalue() == data
    session.get.assert_called_once_with("https://example.com/archive.zip")
    mock_response.raise_for_status.assert_called_once()


def test_download_zip_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")

    session = MagicMock()
    session.get.return_value = mock_response

    session_factory = MagicMock()
    session_factory.__enter__.return_value = session
    session_factory.__exit__.return_value = None

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.requests.Session",
            return_value=session_factory,
        ),
        pytest.raises(requests.HTTPError),
    ):
        download_zip("https://example.com/archive.zip")


def test_extract_zip():
    # Create an in-memory ZIP archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as archive:
        archive.writestr("file1.txt", "Hello")
        archive.writestr("folder/file2.txt", "World")

    # Rewind the buffer before reading it
    zip_buffer.seek(0)

    result = extract_zip(zip_buffer)

    assert set(result.keys()) == {
        "file1.txt",
        "folder/file2.txt",
    }

    assert isinstance(result["file1.txt"], io.BytesIO)
    assert result["file1.txt"].getvalue() == b"Hello"

    assert isinstance(result["folder/file2.txt"], io.BytesIO)
    assert result["folder/file2.txt"].getvalue() == b"World"


def test_download_phytosanitary_products_success(
    tmp_path: Path,
) -> None:
    """Download and extract all relevant phytosanitary XML sections."""
    root = ET.Element("PublicationData")

    # Normal Products section.
    products = ET.SubElement(
        root,
        "Products",
        {
            "numberOfProducts": "1710",
            "someOtherAttribute": "keep-me",
        },
    )

    ET.SubElement(
        products,
        "Product",
        {"id": "8132"},
    )

    # Normal Parallelimports section.
    parallelimports = ET.SubElement(
        root,
        "Parallelimports",
        {
            "numberOfParallelimports": "42",
        },
    )

    ET.SubElement(
        parallelimports,
        "Parallelimport",
        {"id": "F-6697"},
    )

    # Metadata section.
    metadata = ET.SubElement(
        root,
        "MetaData",
        {
            "name": "ApplicationArea",
            "numberOfRows": "123",
        },
    )

    ET.SubElement(
        metadata,
        "Detail",
        {"primaryKey": "area-1"},
    )

    # Section that should be preserved with no special handling.
    measures = ET.SubElement(
        root,
        "Measures",
    )

    ET.SubElement(
        measures,
        "Measure",
        {"primaryKey": "measure-1"},
    )

    xml_buffer = io.BytesIO()

    ET.ElementTree(root).write(
        xml_buffer,
        encoding="utf-8",
        xml_declaration=True,
    )
    xml_buffer.seek(0)

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.download_zip",
            return_value=io.BytesIO(b"dummy zip"),
        ),
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.extract_zip",
            return_value={
                "PublicationData.xml": xml_buffer,
            },
        ),
    ):
        download_phytosanitary_products(
            "https://example.com/data.zip",
            tmp_path,
        )

    # ---------------------------------------------------------
    # Products
    # ---------------------------------------------------------

    products_file = tmp_path / "products.xml"

    assert products_file.exists()

    products_tree = parse(products_file)
    products_root = products_tree.getroot()

    assert products_root.tag == "Products"
    assert products_root.get("numberOfProducts") is None
    assert products_root.get("someOtherAttribute") == "keep-me"

    product = products_root.find("Product")

    assert product is not None
    assert product.get("id") == "8132"

    # ---------------------------------------------------------
    # Parallelimports
    # ---------------------------------------------------------

    parallelimports_file = tmp_path / "parallelimports.xml"

    assert parallelimports_file.exists()

    parallelimports_tree = parse(parallelimports_file)
    parallelimports_root = parallelimports_tree.getroot()

    assert parallelimports_root.tag == "Parallelimports"
    assert parallelimports_root.get("numberOfParallelimports") is None

    parallelimport = parallelimports_root.find("Parallelimport")

    assert parallelimport is not None
    assert parallelimport.get("id") == "F-6697"

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    application_area_file = tmp_path / "application_area.xml"

    assert application_area_file.exists()

    application_area_tree = parse(application_area_file)
    application_area_root = application_area_tree.getroot()

    assert application_area_root.tag == "ApplicationArea"

    assert application_area_root.get("name") is None
    assert application_area_root.get("numberOfRows") is None

    detail = application_area_root.find("Detail")

    assert detail is not None
    assert detail.get("primaryKey") == "area-1"

    # ---------------------------------------------------------
    # Other sections
    # ---------------------------------------------------------

    measures_file = tmp_path / "measures.xml"

    assert measures_file.exists()

    measures_tree = parse(measures_file)
    measures_root = measures_tree.getroot()

    assert measures_root.tag == "Measures"

    measure = measures_root.find("Measure")

    assert measure is not None
    assert measure.get("primaryKey") == "measure-1"


def test_download_phytosanitary_products_does_not_modify_input(
    tmp_path: Path,
) -> None:
    """Do not modify sections from the downloaded XML tree."""
    root = ET.Element("PublicationData")

    products = ET.SubElement(
        root,
        "Products",
        {"numberOfProducts": "10"},
    )

    ET.SubElement(
        products,
        "Product",
        {"id": "1"},
    )

    original_xml = ET.tostring(root)

    xml_buffer = io.BytesIO()

    ET.ElementTree(root).write(
        xml_buffer,
        encoding="utf-8",
        xml_declaration=True,
    )
    xml_buffer.seek(0)

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.download_zip",
            return_value=io.BytesIO(b"dummy zip"),
        ),
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.extract_zip",
            return_value={
                "PublicationData.xml": xml_buffer,
            },
        ),
    ):
        download_phytosanitary_products(
            "https://example.com/data.zip",
            tmp_path,
        )

    assert ET.tostring(root) == original_xml


def test_download_phytosanitary_products_metadata(
    tmp_path: Path,
) -> None:
    """Convert MetaData sections into named XML sections."""
    root = ET.Element("PublicationData")

    metadata = ET.SubElement(
        root,
        "MetaData",
        {
            "name": "ApplicationArea",
            "numberOfRows": "100",
        },
    )

    ET.SubElement(
        metadata,
        "Detail",
        {"primaryKey": "area-1"},
    )

    xml_buffer = io.BytesIO()

    ET.ElementTree(root).write(
        xml_buffer,
        encoding="utf-8",
        xml_declaration=True,
    )
    xml_buffer.seek(0)

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.download_zip",
            return_value=io.BytesIO(b"dummy zip"),
        ),
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.extract_zip",
            return_value={
                "PublicationData.xml": xml_buffer,
            },
        ),
    ):
        download_phytosanitary_products(
            "https://example.com/data.zip",
            tmp_path,
        )

    output = tmp_path / "application_area.xml"

    assert output.exists()

    tree = parse(output)
    result = tree.getroot()

    assert result.tag == "ApplicationArea"
    assert result.attrib == {}

    assert result.find("Detail") is not None


def test_download_phytosanitary_products_write_error(
    tmp_path: Path,
) -> None:
    """Convert an IndexError during XML writing to InvalidXMLError."""
    root = ET.Element("PublicationData")

    ET.SubElement(
        root,
        "Products",
    )

    xml_buffer = io.BytesIO()

    ET.ElementTree(root).write(
        xml_buffer,
        encoding="utf-8",
        xml_declaration=True,
    )
    xml_buffer.seek(0)

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.download_zip",
            return_value=io.BytesIO(b"dummy zip"),
        ),
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.extract_zip",
            return_value={
                "PublicationData.xml": xml_buffer,
            },
        ),
        patch(
            "manexp_web_lists.phytosanitary_products.extract.download_phytosanitary_products.ElementTree.write",
            side_effect=IndexError,
        ),
        pytest.raises(InvalidXMLError),
    ):
        download_phytosanitary_products(
            "https://example.com/data.zip",
            tmp_path,
        )

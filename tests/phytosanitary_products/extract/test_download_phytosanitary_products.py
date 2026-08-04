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
    FILES_TO_DOWNLOAD,
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


def test_download_phytosanitary_products_success(tmp_path: Path) -> None:
    # Build a minimal XML document with one element for each index
    root = ET.Element("Root")

    max_index = max(FILES_TO_DOWNLOAD.keys())
    for i in range(max_index + 1):
        child = ET.SubElement(root, f"Section{i}")
        child.text = f"value-{i}"

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
        download_phytosanitary_products("https://example.com/data.zip", tmp_path)

        for index, filename in FILES_TO_DOWNLOAD.items():
            file = tmp_path / filename

            assert file.exists()

            tree = parse(file)
            root = tree.getroot()

            assert root.tag == "Data"
            assert len(root) == 1
            assert root[0].tag == f"Section{index}"
            assert root[0].text == f"value-{index}"


def test_download_phytosanitary_products_empty_xml(tmp_path: Path) -> None:
    # Build a minimal XML document with one element for each index
    root = ET.Element("Root")

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
        pytest.raises(InvalidXMLError),
    ):
        download_phytosanitary_products("https://example.com/data.zip", tmp_path)


def test_download_phytosanitary_products_incomplete_xml(tmp_path: Path) -> None:
    # Build a minimal XML document with one element for each index
    root = ET.Element("Root")

    max_index = max(FILES_TO_DOWNLOAD.keys())
    for i in range(max_index):
        child = ET.SubElement(root, f"Section{i}")
        child.text = f"value-{i}"

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
        pytest.raises(InvalidXMLError),
    ):
        download_phytosanitary_products("https://example.com/data.zip", tmp_path)

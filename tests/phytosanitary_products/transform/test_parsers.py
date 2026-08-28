from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from manexp_web_lists.exceptions import InvalidXMLError
from manexp_web_lists.phytosanitary_products.transform.parsers import (
    indications_parser,
    metadata_parser,
    parse_xml_root,
    products_parser,
)


def test_parse_xml_root_returns_root(tmp_path: Path) -> None:
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(
        """<?xml version="1.0"?>
        <root>
            <child>value</child>
        </root>
        """
    )

    root = parse_xml_root(xml_file)

    assert root.tag == "root"
    assert root.find("child").text == "value"


def test_parse_xml_root_accepts_bytesio() -> None:
    xml = BytesIO(b"<root><child>value</child></root>")

    root = parse_xml_root(xml)

    assert root.tag == "root"
    assert root.find("child").text == "value"


def test_parse_xml_root_raises_if_no_root() -> None:
    mock_tree = MagicMock(spec=ET.ElementTree)
    mock_tree.getroot.return_value = None

    with (
        patch("manexp_web_lists.phytosanitary_products.transform.parsers.parse", return_value=mock_tree),
        pytest.raises(InvalidXMLError),
    ):
        parse_xml_root(Path("dummy.xml"))


def test_metadata_parser(tmp_path: Path) -> None:
    """Parse metadata details into a Polars DataFrame."""
    root = ET.Element("MetaData")

    detail_1 = ET.SubElement(
        root,
        "Detail",
        {"primaryKey": "key-1"},
    )

    ET.SubElement(
        detail_1,
        "Description",
        {
            "language": "de",
            "value": "Beschreibung 1",
        },
    )

    ET.SubElement(
        detail_1,
        "Description",
        {
            "language": "fr",
            "value": "Description 1",
        },
    )

    detail_2 = ET.SubElement(
        root,
        "Detail",
        {"primaryKey": "key-2"},
    )

    ET.SubElement(
        detail_2,
        "Description",
        {
            "language": "de",
            "value": "Beschreibung 2",
        },
    )

    ET.SubElement(
        detail_2,
        "Description",
        {
            "language": "fr",
        },
    )

    filename = tmp_path / "metadata.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = metadata_parser(filename)

    expected = pl.DataFrame({
        "primaryKey": ["key-1", "key-2"],
        "de": ["Beschreibung 1", "Beschreibung 2"],
        "fr": ["Description 1", None],
    })

    assert_frame_equal(result, expected)


def test_metadata_parser_empty(tmp_path: Path) -> None:
    """Return an empty DataFrame when no details are present."""
    root = ET.Element("MetaData")

    filename = tmp_path / "metadata.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = metadata_parser(filename)

    assert result.is_empty()
    assert result.columns == []


def test_products_parser(tmp_path: Path) -> None:
    """Parse product information into a Polars DataFrame."""
    root = ET.Element("Products")

    product = ET.SubElement(
        root,
        "Product",
        {
            "id": "8132",
            "soldoutDeadline": "2026-12-31",
            "exhaustionDeadline": "2027-12-31",
            "wNbr": "6823",
            "name": "Gesal",
        },
    )

    product_info = ET.SubElement(
        product,
        "ProductInformation",
    )

    ET.SubElement(
        product_info,
        "ProductCategory",
        {"primaryKey": "category-1"},
    )
    ET.SubElement(
        product_info,
        "ProductCategory",
        {"primaryKey": "category-2"},
    )

    ET.SubElement(
        product_info,
        "FormulationCode",
        {"primaryKey": "formulation-1"},
    )

    ET.SubElement(
        product_info,
        "DangerSymbol",
        {"primaryKey": "danger-1"},
    )
    ET.SubElement(
        product_info,
        "DangerSymbol",
        {"primaryKey": "danger-2"},
    )

    ET.SubElement(
        product_info,
        "SignalWords",
        {"primaryKey": "signal-1"},
    )

    ET.SubElement(
        product_info,
        "CodeS",
        {"primaryKey": "code-s-1"},
    )
    ET.SubElement(
        product_info,
        "CodeS",
        {"primaryKey": "code-s-2"},
    )

    ET.SubElement(
        product_info,
        "CodeR",
        {"primaryKey": "code-r-1"},
    )

    ET.SubElement(
        product_info,
        "Indication",
        {"primaryKey": "indication-1"},
    )
    ET.SubElement(
        product_info,
        "Indication",
        {"primaryKey": "indication-2"},
    )

    filename = tmp_path / "products.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = products_parser(filename)

    expected = pl.DataFrame({
        "id": ["8132"],
        "soldoutDeadline": ["2026-12-31"],
        "exhaustionDeadline": ["2027-12-31"],
        "wNbr": ["6823"],
        "name": ["Gesal"],
        "ProductCategory": [["category-1", "category-2"]],
        "FormulationCode": [["formulation-1"]],
        "DangerSymbol": [["danger-1", "danger-2"]],
        "SignalWords": [["signal-1"]],
        "CodeS": [["code-s-1", "code-s-2"]],
        "CodeR": [["code-r-1"]],
        "Indication": [["indication-1", "indication-2"]],
    })

    assert_frame_equal(result, expected)


def test_products_parser_without_product_information(
    tmp_path: Path,
) -> None:
    """Parse a product without ProductInformation."""
    root = ET.Element("Products")

    ET.SubElement(
        root,
        "Product",
        {
            "id": "8132",
            "soldoutDeadline": "",
            "exhaustionDeadline": "",
            "wNbr": "6823",
            "name": "Gesal",
        },
    )

    filename = tmp_path / "products.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = products_parser(filename)

    expected = pl.DataFrame({
        "id": ["8132"],
        "soldoutDeadline": [""],
        "exhaustionDeadline": [""],
        "wNbr": ["6823"],
        "name": ["Gesal"],
        "ProductCategory": [[]],
        "FormulationCode": [[]],
        "DangerSymbol": [[]],
        "SignalWords": [[]],
        "CodeS": [[]],
        "CodeR": [[]],
        "Indication": [[]],
    })

    assert_frame_equal(result, expected)


def test_products_parser_multiple_products(tmp_path: Path) -> None:
    """Parse multiple products into separate rows."""
    root = ET.Element("Products")

    product_1 = ET.SubElement(
        root,
        "Product",
        {
            "id": "1",
            "soldoutDeadline": "",
            "exhaustionDeadline": "",
            "wNbr": "100",
            "name": "Product 1",
        },
    )

    product_1_info = ET.SubElement(
        product_1,
        "ProductInformation",
    )

    ET.SubElement(
        product_1_info,
        "Indication",
        {"primaryKey": "indication-1"},
    )

    product_2 = ET.SubElement(
        root,
        "Product",
        {
            "id": "2",
            "soldoutDeadline": "",
            "exhaustionDeadline": "",
            "wNbr": "200",
            "name": "Product 2",
        },
    )

    product_2_info = ET.SubElement(
        product_2,
        "ProductInformation",
    )

    ET.SubElement(
        product_2_info,
        "Indication",
        {"primaryKey": "indication-2"},
    )

    filename = tmp_path / "products.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = products_parser(filename)

    assert result.height == 2

    assert result["id"].to_list() == ["1", "2"]

    assert result["Indication"].to_list() == [
        ["indication-1"],
        ["indication-2"],
    ]


def test_indications_parser(tmp_path: Path) -> None:
    """Parse indications into a Polars DataFrame."""
    root = ET.Element("Indications")

    indication = ET.SubElement(
        root,
        "Indication",
        {
            "id": "indication-1",
            "dosageFrom": "1",
            "dosageTo": "2",
            "waitingPeriod": "3",
            "expenditureForm": "13.000000",
            "expenditureTo": "4",
        },
    )

    ET.SubElement(
        indication,
        "Measure",
        {"primaryKey": "measure-1"},
    )

    ET.SubElement(
        indication,
        "TimeMeasure",
        {"primaryKey": "time-measure-1"},
    )

    ET.SubElement(
        indication,
        "ApplicationArea",
        {"primaryKey": "application-area-1"},
    )

    ET.SubElement(
        indication,
        "ApplicationComment",
        {"primaryKey": "comment-1"},
    )
    ET.SubElement(
        indication,
        "ApplicationComment",
        {"primaryKey": "comment-2"},
    )

    ET.SubElement(
        indication,
        "Culture",
        {"primaryKey": "culture-1"},
    )
    ET.SubElement(
        indication,
        "Culture",
        {"primaryKey": "culture-2"},
    )

    ET.SubElement(
        indication,
        "Pest",
        {"primaryKey": "pest-1"},
    )
    ET.SubElement(
        indication,
        "Pest",
        {"primaryKey": "pest-2"},
    )

    ET.SubElement(
        indication,
        "Obligation",
        {"primaryKey": "obligation-1"},
    )
    ET.SubElement(
        indication,
        "Obligation",
        {"primaryKey": "obligation-2"},
    )

    filename = tmp_path / "indications.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = indications_parser(filename)

    expected = pl.DataFrame({
        "dosageFrom": ["1"],
        "dosageTo": ["2"],
        "waitingPeriod": ["3"],
        "expenditureFrom": ["13.000000"],
        "expenditureTo": ["4"],
        "id": ["indication-1"],
        "Measure": ["measure-1"],
        "TimeMeasure": ["time-measure-1"],
        "ApplicationArea": ["application-area-1"],
        "ApplicationComment": [["comment-1", "comment-2"]],
        "Culture": [["culture-1", "culture-2"]],
        "Pest": [["pest-1", "pest-2"]],
        "Obligation": [["obligation-1", "obligation-2"]],
    })

    assert_frame_equal(result, expected)


def test_indications_parser_with_missing_elements(
    tmp_path: Path,
) -> None:
    """Parse an indication with missing optional elements."""
    root = ET.Element("Indications")

    ET.SubElement(
        root,
        "Indication",
        {
            "id": "indication-1",
            "dosageFrom": "",
            "dosageTo": "",
            "waitingPeriod": "",
            "expenditureForm": "",
            "expenditureTo": "",
        },
    )

    filename = tmp_path / "indications.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = indications_parser(filename)

    expected = pl.DataFrame({
        "dosageFrom": [""],
        "dosageTo": [""],
        "waitingPeriod": [""],
        "expenditureFrom": [""],
        "expenditureTo": [""],
        "id": ["indication-1"],
        "Measure": [None],
        "TimeMeasure": [None],
        "ApplicationArea": [None],
        "ApplicationComment": [[]],
        "Culture": [[]],
        "Pest": [[]],
        "Obligation": [[]],
    })

    assert_frame_equal(result, expected)


def test_indications_parser_multiple_indications(
    tmp_path: Path,
) -> None:
    """Parse multiple indications into separate rows."""
    root = ET.Element("Indications")

    indication_1 = ET.SubElement(
        root,
        "Indication",
        {
            "id": "indication-1",
            "expenditureForm": "13.000000",
        },
    )

    ET.SubElement(
        indication_1,
        "Measure",
        {"primaryKey": "measure-1"},
    )

    indication_2 = ET.SubElement(
        root,
        "Indication",
        {
            "id": "indication-2",
            "expenditureForm": "9.000000",
        },
    )

    ET.SubElement(
        indication_2,
        "Measure",
        {"primaryKey": "measure-2"},
    )

    filename = tmp_path / "indications.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = indications_parser(filename)

    assert result.height == 2
    assert result["id"].to_list() == [
        "indication-1",
        "indication-2",
    ]
    assert result["Measure"].to_list() == [
        "measure-1",
        "measure-2",
    ]
    assert result["expenditureFrom"].to_list() == [
        "13.000000",
        "9.000000",
    ]


def test_indications_parser_empty(tmp_path: Path) -> None:
    """Return an empty DataFrame when no indications are present."""
    root = ET.Element("Indications")

    filename = tmp_path / "indications.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = indications_parser(filename)

    assert result.is_empty()

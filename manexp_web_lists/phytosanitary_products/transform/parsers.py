from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import polars as pl
from defusedxml.ElementTree import parse

from manexp_web_lists.exceptions import InvalidXMLError


def parse_xml_root(filename: Path | BytesIO) -> ET.Element:
    """Parse an XML file and return its root element.

    Args:
        filename: The XML file to parse.

    Returns:
        ET.Element: The root element of the XML document.

    Raises:
        InvalidXMLError: If the XML document has no root element.
    """
    tree = parse(filename)
    root = tree.getroot()

    if root is None:
        raise InvalidXMLError()

    return root


def metadata_parser(filename: Path) -> pl.DataFrame:
    """
    Parse a metadata file to polars dataframe

    Args:
        filename: The filename of the file to parse

    Returns:
        pl.DataFrame: The polars dataframe corresponding to the given file
    """
    root = parse_xml_root(filename)

    rows = []

    for detail in root.findall(".//Detail"):
        row: dict[str, str | None] = {
            "primaryKey": detail.attrib["primaryKey"],
        }

        for description in detail.findall("Description"):
            language = description.attrib["language"]
            row[language] = description.attrib.get("value")

        rows.append(row)

    return pl.DataFrame(rows)


def products_parser(filename: Path) -> pl.DataFrame:
    """
    Parse a products file to polars dataframe

    Args:
        filename: The filename of the file to parse

    Returns:
        pl.DataFrame: The polars dataframe corresponding to the given file
    """

    root = parse_xml_root(filename)

    rows = []

    section = ".//Product"

    for product in root.findall(section):
        row: dict = {
            # Product attributes
            "id": product.attrib.get("id"),
            "soldoutDeadline": product.attrib.get("soldoutDeadline"),
            "exhaustionDeadline": product.attrib.get("exhaustionDeadline"),
            "wNbr": product.attrib.get("wNbr"),
            "name": product.attrib.get("name"),
            # ProductInformation
            "ProductCategory": [],
            "FormulationCode": [],
            "DangerSymbol": [],
            "SignalWords": [],
            "CodeS": [],
            "CodeR": [],
            "Indication": [],
        }

        product_info = product.find("ProductInformation")

        if product_info is not None:
            row["ProductCategory"] = [
                element.attrib.get("primaryKey") for element in product_info.findall("ProductCategory")
            ]

            row["FormulationCode"] = [
                element.attrib.get("primaryKey") for element in product_info.findall("FormulationCode")
            ]

            row["DangerSymbol"] = [element.attrib.get("primaryKey") for element in product_info.findall("DangerSymbol")]

            row["SignalWords"] = [element.attrib.get("primaryKey") for element in product_info.findall("SignalWords")]

            row["CodeS"] = [element.attrib.get("primaryKey") for element in product_info.findall("CodeS")]

            row["CodeR"] = [element.attrib.get("primaryKey") for element in product_info.findall("CodeR")]

            row["Indication"] = [element.attrib.get("primaryKey") for element in product_info.findall("Indication")]

        rows.append(row)

    return pl.DataFrame(rows)


def indications_parser(filename: Path) -> pl.DataFrame:
    """
    Parse an indications file to polars dataframe

    Args:
        filename: The filename of the file to parse

    Returns:
        pl.DataFrame: The polars dataframe corresponding to the given file
    """

    root = parse_xml_root(filename)

    rows = []

    section = ".//Indication"

    for indication in root.findall(section):
        row: dict = {
            # Indication attributes
            "dosageFrom": indication.attrib.get("dosageFrom"),
            "dosageTo": indication.attrib.get("dosageTo"),
            "waitingPeriod": indication.attrib.get("waitingPeriod"),
            "expenditureFrom": indication.attrib.get("expenditureForm"),
            "expenditureTo": indication.attrib.get("expenditureTo"),
            "id": indication.attrib.get("id"),
            # Indication elements
            "Measure": None,
            "TimeMeasure": None,
            "ApplicationArea": None,
            "ApplicationComment": [],
            "Culture": [],
            "Pest": [],
            "Obligation": [],
        }

        for field in [
            "Measure",
            "TimeMeasure",
            "ApplicationArea",
        ]:
            element = indication.find(field)

            if element is not None:
                row[field] = element.attrib.get("primaryKey")

        row["ApplicationComment"] = [
            element.attrib.get("primaryKey") for element in indication.findall("ApplicationComment")
        ]

        row["Culture"] = [element.attrib.get("primaryKey") for element in indication.findall("Culture")]

        row["Pest"] = [element.attrib.get("primaryKey") for element in indication.findall("Pest")]

        row["Obligation"] = [element.attrib.get("primaryKey") for element in indication.findall("Obligation")]

        rows.append(row)

    return pl.DataFrame(rows)

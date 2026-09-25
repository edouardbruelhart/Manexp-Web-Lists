from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import polars as pl
from defusedxml.ElementTree import parse

from manexp_web_lists.exceptions import (
    CodeMismatchError,
    InvalidXMLError,
    UnexpectedXMLChildError,
    UnexpectedXMLLanguageError,
)


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


LANGUAGES = {
    "fr": "french",
    "de": "german",
    "it": "italian",
    "en": "english",
}


def _parse_description(
    description: ET.Element,
    row: dict[str, str | None],
) -> None:
    """
    Parse a Description element and update the row.

    Args:
        description: The description XML element
        row: The row where to store the description elements

    Raises:
        UnexpectedXMLLanguageError: Raised when the language met is not intended
        CodeMismatchError: Raised when the universal code differs between languages
    """

    language = description.attrib.get("language")

    if language not in LANGUAGES:
        raise UnexpectedXMLLanguageError(language)

    row[language] = description.attrib.get("value")

    for child in description:
        value = child.attrib.get("value")

        if value is None:
            continue

        column = child.tag[0].lower() + child.tag[1:]

        if column not in row:
            row[column] = value
        elif row[column] != value:
            raise CodeMismatchError(column, row[column], value)


def _parse_detail(
    detail: ET.Element,
) -> dict[str, str | None]:
    """
    Parse a single Detail element.

    Args:
        detail: The detail element to parse

    Raises:
        UnexpectedXMLChildError: Raised when an unexpected child element is met

    Returns:
        dict[str, str | None]: The parsed detail
    """

    row: dict[str, str | None] = dict(detail.attrib)

    for child in detail:
        if child.tag == "Parent":
            parent = child.attrib.get("primaryKey")

            if parent is not None:
                row["parent"] = parent

        elif child.tag == "Description":
            _parse_description(child, row)

        else:
            raise UnexpectedXMLChildError(child.tag)

    return row


def metadata_parser(filename: Path) -> pl.DataFrame:
    """
    Parse a metadata file to polars dataframe.

    Args:
        filename: The filename of the file to parse

    Returns:
        pl.DataFrame: The polars dataframe corresponding to the given file.
    """
    root = parse_xml_root(filename)

    rows = [_parse_detail(detail) for detail in root.findall(".//Detail")]

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
            "soldout_deadline": product.attrib.get("soldoutDeadline"),
            "exhaustion_deadline": product.attrib.get("exhaustionDeadline"),
            "id": product.attrib.get("wNbr"),
            "name": product.attrib.get("name"),
            # ProductInformation
            "product_category": [],
            "formulation_code": [],
            "danger_symbol": [],
            "signal_word": [],
            "s_code": [],
            "r_code": [],
            "indication": [],
        }

        product_info = product.find("ProductInformation")

        if product_info is not None:
            row["product_category"] = [
                element.attrib.get("primaryKey") for element in product_info.findall("ProductCategory")
            ]

            row["formulation_code"] = [
                element.attrib.get("primaryKey") for element in product_info.findall("FormulationCode")
            ]

            row["danger_symbol"] = [
                element.attrib.get("primaryKey") for element in product_info.findall("DangerSymbol")
            ]

            row["signal_word"] = [element.attrib.get("primaryKey") for element in product_info.findall("SignalWords")]

            row["s_code"] = [element.attrib.get("primaryKey") for element in product_info.findall("CodeS")]

            row["r_code"] = [element.attrib.get("primaryKey") for element in product_info.findall("CodeR")]

            row["indication"] = [element.attrib.get("primaryKey") for element in product_info.findall("Indication")]

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
            "dosage_from": indication.attrib.get("dosageFrom"),
            "dosage_to": indication.attrib.get("dosageTo"),
            "waiting_period": indication.attrib.get("waitingPeriod"),
            "expenditure_from": indication.attrib.get("expenditureForm"),
            "expenditure_to": indication.attrib.get("expenditureTo"),
            "id": indication.attrib.get("id"),
            # Indication elements
            "measure": [],
            "time_measure": [],
            "application_area": [],
            "application_comment": [],
            "culture": [],
            "culture_form": [],
            "pest": [],
            "obligation": [],
        }

        row["measure"] = [element.attrib.get("primaryKey") for element in indication.findall("Measure")]

        row["time_measure"] = [element.attrib.get("primaryKey") for element in indication.findall("TimeMeasure")]

        row["application_area"] = [
            element.attrib.get("primaryKey") for element in indication.findall("ApplicationArea")
        ]

        row["application_comment"] = [
            element.attrib.get("primaryKey") for element in indication.findall("ApplicationComment")
        ]

        row["culture"] = [
            {"id": element.attrib.get("primaryKey"), "additional_text": element.attrib.get("additionalTextPrimaryKey")}
            for element in indication.findall("Culture")
        ]

        row["culture_form"] = [element.attrib.get("primaryKey") for element in indication.findall("CultureForm")]

        row["pest"] = [
            {
                "id": element.attrib.get("primaryKey"),
                "additional_text": element.attrib.get("additionalTextPrimaryKey"),
                "type": element.attrib.get("type"),
            }
            for element in indication.findall("Pest")
        ]

        row["obligation"] = [element.attrib.get("primaryKey") for element in indication.findall("Obligation")]

        rows.append(row)

    return pl.DataFrame(rows)

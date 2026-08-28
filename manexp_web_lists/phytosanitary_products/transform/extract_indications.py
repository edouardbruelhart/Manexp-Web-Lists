import hashlib
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from defusedxml.ElementTree import fromstring, parse

from manexp_web_lists.exceptions import InvalidXMLError, UnexpectedIndicationError


def extract_indications(phyto_path: Path) -> None:
    """
    Extract indications from products.xml

    Args:
        phyto_path: The path to the phyto lists folder

    Raises:
        InvalidXMLError: Raised when the input xml is not valid
    """

    # Construct paths
    products_file = phyto_path / "merged_products.xml"
    output_products_file = phyto_path / "cleaned_products.xml"
    indications_file = phyto_path / "indications.xml"

    # Load merged products
    tree = parse(products_file)
    products_root = tree.getroot()

    if products_root is None:
        raise InvalidXMLError()

    # key -> indication XML element
    indications = {}

    for product in products_root.findall("Product"):
        product_information = product.find("ProductInformation")

        # Ignore entries without product information
        if product_information is None:
            continue

        # We make a list because we modify product_information
        # while iterating over the indications.
        for indication in list(product_information.findall("Indication")):
            # Create deterministic key
            key = indication_hash(indication)

            # Keep first occurrence of each unique indication
            if key not in indications:
                indications[key] = indication

            # Find original position
            children = list(product_information)
            index = children.index(indication)

            # Remove original indication
            product_information.remove(indication)

            # Replace it with a reference
            ref = ET.Element(
                "Indication",
                {"primaryKey": key},
            )

            # Keep the original position
            product_information.insert(index, ref)

    # ---------------------------------------------------------
    # Write products.xml
    # ---------------------------------------------------------

    ET.indent(tree, space="    ")

    tree.write(
        output_products_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    # ---------------------------------------------------------
    # Construct indications.xml
    # ---------------------------------------------------------

    indications_root = ET.Element("Indications")

    for indication_id, indication in indications.items():
        # Make a copy because the original element belongs to
        # the products XML tree.
        indication_copy = fromstring(
            ET.tostring(
                indication,
                encoding="unicode",
            )
        )

        indication_copy.set("id", indication_id)

        indications_root.append(indication_copy)

    indications_tree = ET.ElementTree(indications_root)

    ET.indent(indications_tree, space="    ")

    indications_tree.write(
        indications_file,
        encoding="utf-8",
        xml_declaration=True,
    )


def canonicalize_indication(indication: ET.Element) -> dict:
    """
    Convert an <Indication> XML element into a canonical,
    order-independent representation.

    Args:
        indication: The indication to canonicalize

    Returns:
        dict: The canonicalized indication

    Raises:
        UnexpectedIndicationError: Raised when an element in indication is not managed by the code
    """

    result: dict[str, Any] = {
        "attributes": {key: indication.get(key, "") for key in sorted(indication.attrib)},
        "Measure": [],
        "TimeMeasure": [],
        "ApplicationArea": [],
        "ApplicationComment": [],
        "Culture": [],
        "CultureForm": [],
        "Pest": [],
        "Obligation": [],
    }

    unordered_elements = {
        "Measure",
        "TimeMeasure",
        "ApplicationArea",
        "ApplicationComment",
        "Culture",
        "CultureForm",
        "Pest",
        "Obligation",
    }

    for child in indication:
        if child.tag not in unordered_elements:
            raise UnexpectedIndicationError(child.tag)

        child_data = {"attributes": {key: child.get(key, "") for key in sorted(child.attrib)}}

        result[child.tag].append(child_data)

    # These elements represent sets/lists where XML order
    # has no semantic meaning.
    for tag in unordered_elements:
        result[tag].sort(
            key=lambda x: json.dumps(
                x,
                sort_keys=True,
                separators=(",", ":"),
            )
        )

    return result


def indication_hash(indication: ET.Element) -> str:
    """
    Hash the indication to get a static identifier

    Args:
        indication: The indication to hash

    Returns:
        str: The hash corresponding to the indication
    """
    canonical = canonicalize_indication(indication)

    serialized = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(serialized).hexdigest()

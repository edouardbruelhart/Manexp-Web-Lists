from pathlib import Path
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET

import pytest
from defusedxml.ElementTree import fromstring, parse

from manexp_web_lists.exceptions import InvalidXMLError, UnexpectedIndicationError
from manexp_web_lists.phytosanitary_products.transform.extract_indications import (
    canonicalize_indication,
    extract_indications,
    indication_hash,
)


def test_extract_indications(tmp_path: Path) -> None:
    """Extract and deduplicate indications from products."""
    merged_products = ET.Element("Products")

    # Product with two identical indications and one different indication.
    product_1 = ET.SubElement(
        merged_products,
        "Product",
        {"id": "product-1"},
    )
    product_1_info = ET.SubElement(product_1, "ProductInformation")

    ET.SubElement(
        product_1_info,
        "ProductCategory",
        {"primaryKey": "category-1"},
    )

    indication_1 = ET.SubElement(
        product_1_info,
        "Indication",
        {"expenditureForm": "13.000000"},
    )
    ET.SubElement(indication_1, "Measure", {"primaryKey": "measure-1"})
    ET.SubElement(indication_1, "Culture", {"primaryKey": "culture-1"})

    indication_2 = ET.SubElement(
        product_1_info,
        "Indication",
        {"expenditureForm": "13.000000"},
    )
    ET.SubElement(indication_2, "Culture", {"primaryKey": "culture-1"})
    ET.SubElement(indication_2, "Measure", {"primaryKey": "measure-1"})

    indication_3 = ET.SubElement(
        product_1_info,
        "Indication",
        {"expenditureForm": "9.000000"},
    )
    ET.SubElement(indication_3, "Measure", {"primaryKey": "measure-2"})

    # Product with no ProductInformation.
    ET.SubElement(
        merged_products,
        "Product",
        {"id": "product-2"},
    )

    # Product with the same indication as product 1.
    product_3 = ET.SubElement(
        merged_products,
        "Product",
        {"id": "product-3"},
    )
    product_3_info = ET.SubElement(
        product_3,
        "ProductInformation",
    )

    indication_4 = ET.SubElement(
        product_3_info,
        "Indication",
        {"expenditureForm": "13.000000"},
    )
    ET.SubElement(indication_4, "Measure", {"primaryKey": "measure-1"})
    ET.SubElement(indication_4, "Culture", {"primaryKey": "culture-1"})

    # Write input XML.
    input_file = tmp_path / "merged_products.xml"
    ET.ElementTree(merged_products).write(
        input_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    # Run transformation.
    extract_indications(tmp_path)

    # Check output files exist.
    cleaned_products_file = tmp_path / "cleaned_products.xml"
    indications_file = tmp_path / "indications.xml"

    assert cleaned_products_file.exists()
    assert indications_file.exists()

    # ---------------------------------------------------------
    # Check cleaned_products.xml
    # ---------------------------------------------------------

    cleaned_tree = parse(cleaned_products_file)
    cleaned_root = cleaned_tree.getroot()

    assert cleaned_root is not None

    product_1 = cleaned_root.find("./Product[@id='product-1']")
    assert product_1 is not None

    product_1_info = product_1.find("ProductInformation")
    assert product_1_info is not None

    # ProductCategory remains in its original position.
    assert product_1_info[0].tag == "ProductCategory"

    # All three indications have been replaced by references.
    indication_refs = product_1_info.findall("Indication")

    assert len(indication_refs) == 3

    # Identical indications should have identical keys.
    assert indication_refs[0].get("primaryKey") == indication_refs[1].get("primaryKey")

    # Different indication should have a different key.
    assert indication_refs[0].get("primaryKey") != indication_refs[2].get("primaryKey")

    # Product without ProductInformation is preserved.
    product_2 = cleaned_root.find("./Product[@id='product-2']")
    assert product_2 is not None
    assert product_2.find("ProductInformation") is None

    # Product 3 should reference the same indication key as product 1.
    product_3 = cleaned_root.find("./Product[@id='product-3']")
    assert product_3 is not None

    product_3_info = product_3.find("ProductInformation")
    assert product_3_info is not None

    product_3_ref = product_3_info.find("Indication")

    assert product_3_ref is not None
    assert product_3_ref.get("primaryKey") == indication_refs[0].get("primaryKey")

    # ---------------------------------------------------------
    # Check indications.xml
    # ---------------------------------------------------------

    indications_tree = parse(indications_file)
    indications_root = indications_tree.getroot()

    assert indications_root is not None
    assert indications_root.tag == "Indications"

    # Three occurrences represent only two unique indications.
    indications = indications_root.findall("Indication")

    assert len(indications) == 2

    indication_ids = {indication.get("id") for indication in indications}

    assert None not in indication_ids

    # The two unique indications have the expected IDs.
    assert len(indication_ids) == 2

    # Every reference in cleaned_products.xml resolves to an indication.
    assert all(indication_ref.get("primaryKey") in indication_ids for indication_ref in indication_refs)


def test_extract_indications_raises_if_products_has_no_root(
    tmp_path: Path,
) -> None:
    """Raise InvalidXMLError when the parsed XML has no root."""
    mock_tree = MagicMock(spec=ET.ElementTree)
    mock_tree.getroot.return_value = None

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.transform.extract_indications.parse",
            return_value=mock_tree,
        ),
        pytest.raises(InvalidXMLError),
    ):
        extract_indications(tmp_path)


def test_canonicalize_indication() -> None:
    """Canonicalize an indication into the expected structure."""
    indication = fromstring(
        """
        <Indication
            dosageFrom="1"
            dosageTo="2"
            waitingPeriod="3"
            expenditureForm="13.000000"
            expenditureTo="4">
            <Culture primaryKey="culture-2"/>
            <Measure primaryKey="measure-1"/>
            <Culture primaryKey="culture-1"/>
            <Pest primaryKey="pest-2" type="PEST_FULL_EFFECT"/>
            <Pest primaryKey="pest-1" type="PEST_FULL_EFFECT"/>
        </Indication>
        """
    )

    result = canonicalize_indication(indication)

    assert result == {
        "attributes": {
            "dosageFrom": "1",
            "dosageTo": "2",
            "waitingPeriod": "3",
            "expenditureForm": "13.000000",
            "expenditureTo": "4",
        },
        "Measure": [
            {
                "attributes": {
                    "primaryKey": "measure-1",
                }
            }
        ],
        "TimeMeasure": [],
        "ApplicationArea": [],
        "ApplicationComment": [],
        "Culture": [
            {
                "attributes": {
                    "primaryKey": "culture-1",
                }
            },
            {
                "attributes": {
                    "primaryKey": "culture-2",
                }
            },
        ],
        "CultureForm": [],
        "Pest": [
            {
                "attributes": {
                    "primaryKey": "pest-1",
                    "type": "PEST_FULL_EFFECT",
                }
            },
            {
                "attributes": {
                    "primaryKey": "pest-2",
                    "type": "PEST_FULL_EFFECT",
                }
            },
        ],
        "Obligation": [],
    }


def test_canonicalize_indication_rejects_unknown_element() -> None:
    """Raise ValueError when an unsupported child is encountered."""
    indication = fromstring(
        """
        <Indication>
            <UnknownElement primaryKey="123"/>
        </Indication>
        """
    )

    with pytest.raises(
        UnexpectedIndicationError,
        match="Unexpected element in Indication: UnknownElement",
    ):
        canonicalize_indication(indication)


def test_indication_hash_is_deterministic() -> None:
    """The same indication always produces the same hash."""
    indication = fromstring(
        """
        <Indication
            dosageFrom=""
            dosageTo=""
            waitingPeriod=""
            expenditureForm="13.000000"
            expenditureTo="">
            <Measure primaryKey="measure-1"/>
            <ApplicationArea primaryKey="area-1"/>
            <Culture primaryKey="culture-1"/>
            <Pest primaryKey="pest-1" type="PEST_FULL_EFFECT"/>
            <Obligation primaryKey="obligation-1"/>
        </Indication>
        """
    )

    hash_1 = indication_hash(indication)
    hash_2 = indication_hash(indication)

    assert hash_1 == hash_2


def test_indication_hash_ignores_child_order() -> None:
    """Equivalent indications with different child order have the same hash."""
    indication_1 = fromstring(
        """
        <Indication
            dosageFrom=""
            dosageTo=""
            waitingPeriod=""
            expenditureForm="13.000000"
            expenditureTo="">
            <Measure primaryKey="measure-1"/>
            <ApplicationArea primaryKey="area-1"/>
            <Culture primaryKey="culture-1"/>
            <Culture primaryKey="culture-2"/>
            <Pest primaryKey="pest-1" type="PEST_FULL_EFFECT"/>
            <Pest primaryKey="pest-2" type="PEST_FULL_EFFECT"/>
            <Obligation primaryKey="obligation-1"/>
            <Obligation primaryKey="obligation-2"/>
        </Indication>
        """
    )

    indication_2 = fromstring(
        """
        <Indication
            expenditureTo=""
            expenditureForm="13.000000"
            waitingPeriod=""
            dosageTo=""
            dosageFrom="">
            <Obligation primaryKey="obligation-2"/>
            <Culture primaryKey="culture-2"/>
            <Pest primaryKey="pest-2" type="PEST_FULL_EFFECT"/>
            <Measure primaryKey="measure-1"/>
            <Obligation primaryKey="obligation-1"/>
            <Pest primaryKey="pest-1" type="PEST_FULL_EFFECT"/>
            <Culture primaryKey="culture-1"/>
            <ApplicationArea primaryKey="area-1"/>
        </Indication>
        """
    )

    assert indication_hash(indication_1) == indication_hash(indication_2)


def test_indication_hash_changes_when_content_changes() -> None:
    """A semantic change to an indication changes its hash."""
    indication_1 = fromstring(
        """
        <Indication expenditureForm="13.000000">
            <Measure primaryKey="measure-1"/>
            <ApplicationArea primaryKey="area-1"/>
            <Culture primaryKey="culture-1"/>
        </Indication>
        """
    )

    indication_2 = fromstring(
        """
        <Indication expenditureForm="9.000000">
            <Measure primaryKey="measure-1"/>
            <ApplicationArea primaryKey="area-1"/>
            <Culture primaryKey="culture-1"/>
        </Indication>
        """
    )

    assert indication_hash(indication_1) != indication_hash(indication_2)


def test_indication_hash_changes_when_culture_changes() -> None:
    """Changing a culture changes the indication hash."""
    indication_1 = fromstring(
        """
        <Indication expenditureForm="13.000000">
            <Culture primaryKey="culture-1"/>
        </Indication>
        """
    )

    indication_2 = fromstring(
        """
        <Indication expenditureForm="13.000000">
            <Culture primaryKey="culture-2"/>
        </Indication>
        """
    )

    assert indication_hash(indication_1) != indication_hash(indication_2)


def test_indication_hash_has_sha256_format() -> None:
    """The indication hash is a 64-character hexadecimal SHA-256 digest."""
    indication = fromstring("<Indication/>")

    result = indication_hash(indication)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)

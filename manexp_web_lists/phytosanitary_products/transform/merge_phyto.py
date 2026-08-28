import xml.etree.ElementTree as ET
from pathlib import Path

from .parsers import parse_xml_root

KEEP_ATTRIBUTES = {
    "id",
    "wNbr",
    "name",
    "exhaustionDeadline",
    "soldoutDeadline",
}

KEEP_PRODUCT_INFORMATION = {
    "ProductCategory",
    "FormulationCode",
    "DangerSymbol",
    "CodeS",
    "CodeR",
    "Indication",
}


def merge_phyto(phyto_path: Path) -> None:
    """
    Normalize and merge products and parallel imports.

    Args:
        phyto_path: The path to the phyto lists folder.
    """
    product_file = phyto_path / "products.xml"
    parallelimport_file = phyto_path / "parallelimports.xml"
    output_file = phyto_path / "merged_products.xml"

    products = read_phyto(product_file) + read_phyto(parallelimport_file)

    root = ET.Element("Products")

    for product in products:
        root.append(product)

    tree = ET.ElementTree(root)

    ET.indent(tree, space="    ")

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True,
    )


def normalize_product(source: ET.Element) -> ET.Element:
    """
    Convert either <Product> or <Parallelimport>
    into a common <Product> structure.

    Args:
        source: the element to normalize

    Returns:
        ET.Element: The normalized element
    """

    product = ET.Element("Product")

    # Copy the attributes we care about
    for attr in KEEP_ATTRIBUTES:
        if attr in source.attrib:
            product.set(attr, source.attrib[attr])

    # Create ProductInformation
    source_info = source.find("ProductInformation")

    if source_info is not None:
        product_info = ET.SubElement(product, "ProductInformation")

        for child in source_info:
            if child.tag in KEEP_PRODUCT_INFORMATION:
                product_info.append(child)

    return product


def read_phyto(filename: Path) -> list[ET.Element]:
    """
    Read the phyto file.

    Args:
        filename: The filename of the phyto file.

    Returns:
        list[ET.Element]: A list of normalized Product elements.
    """

    root = parse_xml_root(filename)

    return [normalize_product(element) for element in root if element.tag in ("Product", "Parallelimport")]

from pathlib import Path
from xml.etree import ElementTree as ET

from defusedxml.ElementTree import fromstring, parse

from manexp_web_lists.phytosanitary_products.transform.merge_phyto import merge_phyto, normalize_product, read_phyto


def test_merge_phyto(tmp_path: Path) -> None:
    """Merge products and parallel imports into one XML file."""

    products_root = ET.Element("Products")

    product = ET.SubElement(
        products_root,
        "Product",
        {
            "id": "8132",
            "wNbr": "6823",
            "name": "Product 1",
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

    products_file = tmp_path / "products.xml"

    ET.ElementTree(products_root).write(
        products_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parallelimports_root = ET.Element("Parallelimports")

    parallelimport = ET.SubElement(
        parallelimports_root,
        "Parallelimport",
        {
            "id": "F-6697",
            "wNbr": "6862",
            "name": "Parallelimport 1",
            "admissionnumber": "2140199",
        },
    )

    parallelimport_info = ET.SubElement(
        parallelimport,
        "ProductInformation",
    )

    ET.SubElement(
        parallelimport_info,
        "ProductCategory",
        {"primaryKey": "category-2"},
    )

    parallelimports_file = tmp_path / "parallelimports.xml"

    ET.ElementTree(parallelimports_root).write(
        parallelimports_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    # Run the function.
    merge_phyto(tmp_path)

    # Check output exists.
    output_file = tmp_path / "merged_products.xml"

    assert output_file.exists()

    # Read output.
    tree = parse(output_file)
    root = tree.getroot()

    assert root.tag == "Products"
    assert len(root) == 2

    # First product.
    product = root[0]

    assert product.tag == "Product"
    assert product.get("id") == "8132"
    assert product.get("wNbr") == "6823"
    assert product.get("name") == "Product 1"

    product_info = product.find("ProductInformation")

    assert product_info is not None
    assert product_info.find("ProductCategory") is not None

    # Second product was a Parallelimport but must now be Product.
    parallelimport = root[1]

    assert parallelimport.tag == "Product"
    assert parallelimport.get("id") == "F-6697"
    assert parallelimport.get("wNbr") == "6862"
    assert parallelimport.get("name") == "Parallelimport 1"

    # Parallelimport-specific attribute was removed.
    assert "admissionnumber" not in parallelimport.attrib

    parallelimport_info = parallelimport.find("ProductInformation")

    assert parallelimport_info is not None
    assert parallelimport_info.find("ProductCategory") is not None


def test_merge_phyto_with_empty_source(tmp_path: Path) -> None:
    """Merge successfully when one source contains no products."""

    products_root = ET.Element("Products")

    ET.SubElement(
        products_root,
        "Product",
        {"id": "8132"},
    )

    ET.ElementTree(products_root).write(
        tmp_path / "products.xml",
        encoding="utf-8",
        xml_declaration=True,
    )

    parallelimports_root = ET.Element("Parallelimports")

    ET.ElementTree(parallelimports_root).write(
        tmp_path / "parallelimports.xml",
        encoding="utf-8",
        xml_declaration=True,
    )

    merge_phyto(tmp_path)

    tree = parse(tmp_path / "merged_products.xml")
    root = tree.getroot()

    assert root.tag == "Products"
    assert len(root) == 1
    assert root[0].get("id") == "8132"


def test_normalize_product() -> None:
    """Normalize a Product element."""
    source = fromstring(
        """
        <Product
            id="8132"
            wNbr="6823"
            name="Gesal"
            exhaustionDeadline=""
            soldoutDeadline=""
            isSalePermission="false"
            terminationReason="reason">

            <ProductInformation>
                <ProductCategory primaryKey="category-1"/>
                <FormulationCode primaryKey="formulation-1"/>
                <DangerSymbol primaryKey="danger-1"/>
                <CodeS primaryKey="code-s-1"/>
                <CodeR primaryKey="code-r-1"/>
                <Indication expenditureForm="13.000000"/>

                <PermissionHolderKey primaryKey="permission-1"/>
                <Ingredient inPercent="24.26">
                    <Substance primaryKey="substance-1"/>
                </Ingredient>
            </ProductInformation>
        </Product>
        """
    )

    result = normalize_product(source)

    assert result.tag == "Product"

    assert result.attrib == {
        "id": "8132",
        "wNbr": "6823",
        "name": "Gesal",
        "exhaustionDeadline": "",
        "soldoutDeadline": "",
    }

    product_information = result.find("ProductInformation")
    assert product_information is not None

    assert [child.tag for child in product_information] == [
        "ProductCategory",
        "FormulationCode",
        "DangerSymbol",
        "CodeS",
        "CodeR",
        "Indication",
    ]

    assert product_information.find("ProductCategory").get("primaryKey") == "category-1"


def test_normalize_parallelimport() -> None:
    """Normalize a Parallelimport into the common Product structure."""
    source = fromstring(
        """
        <Parallelimport
            id="F-6697"
            wNbr="6862"
            name="Inixio Xpert"
            admissionnumber="2140199"
            producingCountryPrimaryKey="country-1"
            exhaustionDeadline=""
            soldoutDeadline=""
            packageInsert="8264">

            <ProductInformation>
                <ProductCategory primaryKey="category-1"/>
                <FormulationCode primaryKey="formulation-1"/>
                <DangerSymbol primaryKey="danger-1"/>
                <CodeS primaryKey="code-s-1"/>
                <CodeR primaryKey="code-r-1"/>
                <Indication expenditureForm="0.200000"/>

                <PermissionHolderKey primaryKey="permission-1"/>
                <Ingredient inPercent="1.00"/>
            </ProductInformation>
        </Parallelimport>
        """
    )

    result = normalize_product(source)

    assert result.tag == "Product"

    assert result.attrib == {
        "id": "F-6697",
        "wNbr": "6862",
        "name": "Inixio Xpert",
        "exhaustionDeadline": "",
        "soldoutDeadline": "",
    }

    product_information = result.find("ProductInformation")
    assert product_information is not None

    assert [child.tag for child in product_information] == [
        "ProductCategory",
        "FormulationCode",
        "DangerSymbol",
        "CodeS",
        "CodeR",
        "Indication",
    ]


def test_normalize_product_without_product_information() -> None:
    """Normalize a product that has no ProductInformation."""
    source = fromstring(
        """
        <Product
            id="8132"
            wNbr="6823"
            name="Gesal"/>
        """
    )

    result = normalize_product(source)

    assert result.tag == "Product"

    assert result.attrib == {
        "id": "8132",
        "wNbr": "6823",
        "name": "Gesal",
    }

    assert result.find("ProductInformation") is None


def test_normalize_product_does_not_modify_source() -> None:
    """Normalizing a product does not modify the source element."""
    source = fromstring(
        """
        <Product id="8132">
            <ProductInformation>
                <ProductCategory primaryKey="category-1"/>
                <PermissionHolderKey primaryKey="permission-1"/>
            </ProductInformation>
        </Product>
        """
    )

    normalize_product(source)

    source_info = source.find("ProductInformation")
    assert source_info is not None

    assert [child.tag for child in source_info] == [
        "ProductCategory",
        "PermissionHolderKey",
    ]


def test_read_phyto(tmp_path: Path) -> None:
    """Read and normalize Product and Parallelimport elements."""
    root = ET.Element("Root")

    ET.SubElement(
        root,
        "Product",
        {
            "id": "product-1",
            "wNbr": "1001",
            "name": "Product 1",
        },
    )

    ET.SubElement(
        root,
        "Parallelimport",
        {
            "id": "parallelimport-1",
            "wNbr": "2001",
            "name": "Parallelimport 1",
        },
    )

    # This element must be ignored.
    ET.SubElement(
        root,
        "SomethingElse",
        {"id": "ignored"},
    )

    filename = tmp_path / "phyto.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = read_phyto(filename)

    assert len(result) == 2

    assert all(element.tag == "Product" for element in result)

    assert result[0].get("id") == "product-1"
    assert result[0].get("wNbr") == "1001"

    assert result[1].get("id") == "parallelimport-1"
    assert result[1].get("wNbr") == "2001"


def test_read_phyto_returns_empty_list_for_no_products(
    tmp_path: Path,
) -> None:
    """Return an empty list when no products are present."""
    root = ET.Element("Root")

    ET.SubElement(root, "SomethingElse")

    filename = tmp_path / "phyto.xml"

    ET.ElementTree(root).write(
        filename,
        encoding="utf-8",
        xml_declaration=True,
    )

    result = read_phyto(filename)

    assert result == []

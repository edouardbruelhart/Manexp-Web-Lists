from unittest.mock import patch

from manexp_web_lists.phytosanitary_products.get_phytosanitary_products import get_phytosanitary_products


def test_get_phytosanitary_products() -> None:

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.get_phytosanitary_products.download_phytosanitary_products"
        ) as mock_download,
        patch("manexp_web_lists.phytosanitary_products.get_phytosanitary_products.merge_phyto") as mock_merge,
        patch("manexp_web_lists.phytosanitary_products.get_phytosanitary_products.extract_indications") as mock_extract,
        patch("manexp_web_lists.phytosanitary_products.get_phytosanitary_products.clean_metadata") as mock_metadata,
        patch("manexp_web_lists.phytosanitary_products.get_phytosanitary_products.clean_products") as mock_products,
        patch(
            "manexp_web_lists.phytosanitary_products.get_phytosanitary_products.clean_indications"
        ) as mock_indications,
    ):
        get_phytosanitary_products()

    mock_download.assert_called_once()
    mock_merge.assert_called_once()
    mock_extract.assert_called_once()
    mock_metadata.assert_called_once()
    mock_products.assert_called_once()
    mock_indications.assert_called_once()

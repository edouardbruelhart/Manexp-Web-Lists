from unittest.mock import patch

from manexp_web_lists.phytosanitary_products.get_phytosanitary_products import get_phytosanitary_products


def test_get_phytosanitary_products() -> None:

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.get_phytosanitary_products.download_phytosanitary_products"
        ) as mock_download,
    ):
        get_phytosanitary_products()

    mock_download.assert_called_once()

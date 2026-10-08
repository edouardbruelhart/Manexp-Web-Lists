from pathlib import Path
from unittest.mock import MagicMock, patch

from manexp_web_lists.phytosanitary_products.get_phytosanitary_products import get_phytosanitary_products


def test_get_phytosanitary_products() -> None:

    file_1 = MagicMock(spec=Path)
    file_2 = MagicMock(spec=Path)

    with (
        patch("manexp_web_lists.phytosanitary_products.get_phytosanitary_products.FILES_PATH") as mock_path,
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
        patch(
            "manexp_web_lists.phytosanitary_products.get_phytosanitary_products.load_phytosanitary_products",
        ) as mock_load,
        patch(
            "manexp_web_lists.phytosanitary_products.get_phytosanitary_products.FILES_PATH.iterdir",
            return_value=[file_1, file_2],
        ) as mock_iterdir,
    ):
        get_phytosanitary_products()

    mock_path.mkdir.assert_called_once()
    mock_download.assert_called_once()
    mock_merge.assert_called_once()
    mock_extract.assert_called_once()
    mock_metadata.assert_called_once()
    mock_products.assert_called_once()
    mock_indications.assert_called_once()
    mock_load.assert_called_once()
    mock_iterdir.assert_called_once_with()
    file_1.unlink.assert_called_once_with()
    file_2.unlink.assert_called_once_with()

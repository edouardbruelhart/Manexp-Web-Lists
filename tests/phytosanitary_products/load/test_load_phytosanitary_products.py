from unittest.mock import patch

from manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products import load_phytosanitary_products


def test_load_phytosanitary_products(tmp_path):
    files_path = tmp_path / "files"
    files_path.mkdir()

    with (
        patch(
            "manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products.generate_schema"
        ) as mock_generate_schema,
        patch(
            "manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products.apply_schema"
        ) as mock_apply_schema,
        patch(
            "manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products.synchronize"
        ) as mock_synchronize,
        patch(
            "manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products.DATABASE_URL",
            new="postgresql://pipeline:secret@127.0.0.1:5432/mydb",
        ),
    ):
        load_phytosanitary_products(files_path)

    schema_path = files_path / "schema.sql"

    mock_generate_schema.assert_called_once_with(
        files_path,
        schema_path,
    )

    mock_apply_schema.assert_called_once_with(
        schema_path, "postgresql://pipeline:secret@127.0.0.1:5432/mydb", "products"
    )

    mock_synchronize.assert_called_once_with(
        files_path,
        "postgresql://pipeline:secret@127.0.0.1:5432/mydb",
        "products",
    )

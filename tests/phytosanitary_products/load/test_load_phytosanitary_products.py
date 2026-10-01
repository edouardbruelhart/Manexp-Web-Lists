from unittest.mock import patch

from manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products import (
    load_phytosanitary_products,
)


def test_load_phytosanitary_products(tmp_path):
    lists_path = tmp_path / "lists"
    lists_path.mkdir()

    with (
        patch.dict(
            "os.environ",
            {
                "POSTGRES_PIPELINE_USER": "pipeline",
                "POSTGRES_PIPELINE_PASSWORD": "secret",
                "POSTGRES_PORT": "5432",
                "POSTGRES_DB": "mydb",
            },
        ),
        patch(
            "manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products.generate_schema"
        ) as mock_generate_schema,
        patch(
            "manexp_web_lists.phytosanitary_products.load.load_phytosanitary_products.apply_schema"
        ) as mock_apply_schema,
    ):
        load_phytosanitary_products(lists_path)

    schema_path = lists_path / "schema.sql"

    mock_generate_schema.assert_called_once_with(
        lists_path,
        schema_path,
    )

    mock_apply_schema.assert_called_once_with(
        schema_path,
        "postgresql://pipeline:secret@127.0.0.1:5432/mydb",
    )

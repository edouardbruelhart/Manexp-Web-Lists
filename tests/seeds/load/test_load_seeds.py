from unittest.mock import patch

from manexp_web_lists.seeds.load.load_seeds import load_seeds


def test_load_seeds(tmp_path):
    files_path = tmp_path / "files"
    files_path.mkdir()

    with (
        patch("manexp_web_lists.seeds.load.load_seeds.generate_schema") as mock_generate_schema,
        patch("manexp_web_lists.seeds.load.load_seeds.apply_schema") as mock_apply_schema,
        patch("manexp_web_lists.seeds.load.load_seeds.synchronize") as mock_synchronize,
    ):
        load_seeds(files_path)

    schema_path = files_path / "schema.sql"

    mock_generate_schema.assert_called_once_with(
        files_path,
        schema_path,
    )

    mock_apply_schema.assert_called_once_with(schema_path, "seeds")

    mock_synchronize.assert_called_once_with(
        files_path,
        "seeds",
    )

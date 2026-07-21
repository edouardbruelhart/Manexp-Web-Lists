from unittest.mock import MagicMock, patch

from manexp_web_lists.register_types.get_register_types import get_register_types


def test_get_register_types() -> None:
    df = MagicMock()

    with (
        patch(
            "manexp_web_lists.register_types.get_register_types.create_register_types", return_value=df
        ) as mock_create,
    ):
        get_register_types()

    mock_create.assert_called_once()
    df.write_parquet.assert_called_once()

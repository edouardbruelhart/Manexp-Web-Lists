from unittest.mock import MagicMock, patch

from manexp_web_lists.register_subtypes.get_register_subtypes import get_register_subtypes


def test_get_register_subtypes() -> None:
    df = MagicMock()

    with (
        patch(
            "manexp_web_lists.register_subtypes.get_register_subtypes.create_register_subtypes", return_value=df
        ) as mock_create,
    ):
        get_register_subtypes()

    mock_create.assert_called_once()
    df.write_parquet.assert_called_once()

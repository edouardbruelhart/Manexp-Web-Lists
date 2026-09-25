from unittest.mock import patch

from manexp_web_lists.clients.translation_client import translate


@patch("manexp_web_lists.clients.translation_client.argostranslate.translate.translate")
def test_translate(mock_translate):
    mock_translate.return_value = "Hello world"

    result = translate("Bonjour le monde", "fr", "en")

    assert result == "Hello world"

    mock_translate.assert_called_once_with(
        "Bonjour le monde",
        "fr",
        "en",
    )

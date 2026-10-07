from unittest.mock import patch

from manexp_web_lists.clients.translation_client import translate


def test_translate():

    with patch(
        "manexp_web_lists.clients.translation_client.argostranslate.translate.translate", return_value="Hello world"
    ) as mock_translate:
        result = translate("Bonjour le monde", "fr", "en")

    assert result == "Hello world"

    mock_translate.assert_called_once_with(
        "Bonjour le monde",
        "fr",
        "en",
    )

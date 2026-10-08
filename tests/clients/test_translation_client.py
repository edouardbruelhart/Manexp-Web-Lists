from unittest.mock import patch

import pytest

from manexp_web_lists.clients.translation_client import translate
from manexp_web_lists.exceptions import LanguageInstallationFailedError


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


def test_translate_installs_language_package_when_missing():
    with (
        patch(
            "manexp_web_lists.clients.translation_client.argostranslate.translate.translate",
            side_effect=[
                AttributeError("'NoneType' object has no attribute 'translate'"),
                "Hello world",
            ],
        ) as mock_translate,
        patch(
            "manexp_web_lists.clients.translation_client.argostranslate.package.install_package_for_language_pair",
            return_value=True,
        ) as mock_install,
    ):
        result = translate("Bonjour le monde", "fr", "en")

    assert result == "Hello world"

    mock_install.assert_called_once_with("fr", "en")
    assert mock_translate.call_count == 2
    mock_translate.assert_any_call(
        "Bonjour le monde",
        "fr",
        "en",
    )


def test_translate_reraises_unexpected_attribute_error():
    error = AttributeError("some other attribute error")

    with (
        patch(
            "manexp_web_lists.clients.translation_client.argostranslate.translate.translate",
            side_effect=error,
        ) as mock_translate,
        pytest.raises(AttributeError, match="some other attribute error"),
    ):
        translate("Bonjour le monde", "fr", "en")

    mock_translate.assert_called_once_with(
        "Bonjour le monde",
        "fr",
        "en",
    )


def test_translate_raises_when_language_package_installation_fails():
    with (
        patch(
            "manexp_web_lists.clients.translation_client.argostranslate.translate.translate",
            side_effect=AttributeError("'NoneType' object has no attribute 'translate'"),
        ) as mock_translate,
        patch(
            "manexp_web_lists.clients.translation_client.argostranslate.package.install_package_for_language_pair",
            return_value=False,
        ) as mock_install,
        pytest.raises(
            LanguageInstallationFailedError,
            match=r"fr.*en",
        ),
    ):
        translate("Bonjour le monde", "fr", "en")

    mock_translate.assert_called_once_with(
        "Bonjour le monde",
        "fr",
        "en",
    )
    mock_install.assert_called_once_with("fr", "en")

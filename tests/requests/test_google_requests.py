"""Tests for requests/google_requests.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.requests.google_requests import translate


def test_translate():
    with patch("manexp_web_lists.requests.google_requests.GoogleTranslator") as MockTranslator:
        instance = MagicMock()
        instance.translate.return_value = "Bonjour"
        MockTranslator.return_value = instance

        result = translate("Hello", "en", "fr")

        MockTranslator.assert_called_once_with(
            source="en",
            target="fr",
        )
        instance.translate.assert_called_once_with("Hello")
        assert result == "Bonjour"

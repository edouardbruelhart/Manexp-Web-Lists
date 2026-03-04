"""Tests for taxa/taxo_translator/google_translation.py"""

from unittest.mock import patch

from manexp_web_lists.taxa.models.translations import Translation, TranslationSource
from manexp_web_lists.taxa.taxo_translator.google_translation import google_translation
from manexp_web_lists.taxa.taxo_translator.models import TranslationReport


def test_google_translation_success():
    translation_report = TranslationReport(
        fr=Translation(name="Humain", source=TranslationSource.WIKIDATA),
        en=None,
        de=None,
        it=None,
    )

    with patch("manexp_web_lists.taxa.taxo_translator.google_translation.translate") as mock_translation:
        mock_translation.side_effect = [
            "Human",  # en
            "Mensch",  # de
            "Uomo umano",  # it
        ]

        result = google_translation(translation_report)

        assert result.de.name == "Mensch"
        assert result.de.source == TranslationSource.GOOGLE
        assert result.fr.name == "Humain"
        assert result.fr.source == TranslationSource.WIKIDATA


def test_google_translation_no_report():
    translation_report = TranslationReport(
        fr=None,
        en=None,
        de=None,
        it=None,
    )

    assert google_translation(translation_report) == translation_report

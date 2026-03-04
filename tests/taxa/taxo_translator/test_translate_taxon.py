"""Tests for taxa/taxo_translator/translate_taxon.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.taxa.models.translations import Translation, TranslationSource
from manexp_web_lists.taxa.taxo_translator.models import TranslationReport
from manexp_web_lists.taxa.taxo_translator.translate_taxon import translate_taxon


def test_translate_taxon_success_wikidata():
    with patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.wikidata_translation") as mock_wikidata:
        mock_wikidata.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=Translation(name="Human being", source=TranslationSource.WIKIDATA),
            de=Translation(name="Mensch", source=TranslationSource.WIKIDATA),
            it=Translation(name="Uomo umano", source=TranslationSource.WIKIDATA),
        )

        cleaned_taxonomy = MagicMock()

        result = translate_taxon(cleaned_taxonomy)

        assert result.fr.name == "Être humain"
        assert result.fr.source == TranslationSource.WIKIDATA


def test_translate_taxon_success_gbif():
    with (
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.wikidata_translation") as mock_wikidata,
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.gbif_translation") as mock_gbif,
    ):
        mock_wikidata.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=None,
            de=None,
            it=None,
        )

        mock_gbif.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=Translation(name="Human being", source=TranslationSource.GBIF),
            de=Translation(name="Mensch", source=TranslationSource.GBIF),
            it=Translation(name="Uomo umano", source=TranslationSource.GBIF),
        )

        cleaned_taxonomy = MagicMock()

        result = translate_taxon(cleaned_taxonomy)

        assert result.fr.name == "Être humain"
        assert result.fr.source == TranslationSource.WIKIDATA
        assert result.en.name == "Human being"
        assert result.en.source == TranslationSource.GBIF


def test_translate_taxon_success_google():
    with (
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.wikidata_translation") as mock_wikidata,
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.gbif_translation") as mock_gbif,
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.google_translation") as mock_google,
    ):
        mock_wikidata.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=None,
            de=None,
            it=None,
        )

        mock_gbif.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=Translation(name="Human being", source=TranslationSource.GBIF),
            de=Translation(name="Mensch", source=TranslationSource.GBIF),
            it=None,
        )

        mock_google.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=Translation(name="Human being", source=TranslationSource.GBIF),
            de=Translation(name="Mensch", source=TranslationSource.GBIF),
            it=Translation(name="Uomo umano", source=TranslationSource.GOOGLE),
        )

        cleaned_taxonomy = MagicMock()

        result = translate_taxon(cleaned_taxonomy)

        assert result.fr.name == "Être humain"
        assert result.fr.source == TranslationSource.WIKIDATA
        assert result.en.name == "Human being"
        assert result.en.source == TranslationSource.GBIF
        assert result.de.name == "Mensch"
        assert result.de.source == TranslationSource.GBIF
        assert result.it.name == "Uomo umano"
        assert result.it.source == TranslationSource.GOOGLE


def test_translate_taxon_no_translation():
    with (
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.wikidata_translation") as mock_wikidata,
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.gbif_translation") as mock_gbif,
    ):
        mock_wikidata.return_value = TranslationReport(
            fr=None,
            en=None,
            de=None,
            it=None,
        )

        mock_gbif.return_value = TranslationReport(
            fr=None,
            en=None,
            de=None,
            it=None,
        )

        cleaned_taxonomy = MagicMock()

        result = translate_taxon(cleaned_taxonomy)

        assert result is None


def test_translate_taxon_missing_translations():
    with (
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.wikidata_translation") as mock_wikidata,
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.gbif_translation") as mock_gbif,
        patch("manexp_web_lists.taxa.taxo_translator.translate_taxon.google_translation") as mock_google,
    ):
        mock_wikidata.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=None,
            de=None,
            it=None,
        )

        mock_gbif.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=Translation(name="Human being", source=TranslationSource.GBIF),
            de=None,
            it=None,
        )

        mock_google.return_value = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.WIKIDATA),
            en=Translation(name="Human being", source=TranslationSource.GBIF),
            de=Translation(name="Mensch", source=TranslationSource.GOOGLE),
            it=None,
        )

        cleaned_taxonomy = MagicMock()

        result = translate_taxon(cleaned_taxonomy)

        assert result is None

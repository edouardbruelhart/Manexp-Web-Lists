"""Tests for taxa/taxo_translator/wikidata_translation.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.taxa.taxo_translator.wikidata_translation import wikidata_translation


def test_wikidata_translation_success():

    cleaned_taxonomy = MagicMock()

    with (
        patch("manexp_web_lists.taxa.taxo_translator.wikidata_translation.wikidata_qid_request") as mock_qid,
        patch("manexp_web_lists.taxa.taxo_translator.wikidata_translation.wikidata_labels_request") as mock_labels,
    ):
        mock_qid.return_value = "Q1234"

        mock_labels.return_value = {
            "fr": {"value": "Être humain"},
            "en": {"value": "Human being"},
            "de": {"value": "Mensch"},
            "it": {"value": "Uomo umano"},
        }

        result = wikidata_translation(cleaned_taxonomy)

        assert result.fr.name == "Être humain"
        assert result.en.name == "Human being"


def test_wikidata_translation_no_id():

    cleaned_taxonomy = MagicMock()

    with patch("manexp_web_lists.taxa.taxo_translator.wikidata_translation.wikidata_qid_request") as mock_qid:
        mock_qid.return_value = None

        result = wikidata_translation(cleaned_taxonomy)

        assert result is None


def test_wikidata_translation_no_labels():

    cleaned_taxonomy = MagicMock()

    with (
        patch("manexp_web_lists.taxa.taxo_translator.wikidata_translation.wikidata_qid_request") as mock_qid,
        patch("manexp_web_lists.taxa.taxo_translator.wikidata_translation.wikidata_labels_request") as mock_labels,
    ):
        mock_qid.return_value = "Q1234"

        mock_labels.return_value = None

        result = wikidata_translation(cleaned_taxonomy)

        assert result is None

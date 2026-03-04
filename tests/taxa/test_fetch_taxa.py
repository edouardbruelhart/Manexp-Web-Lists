"""Tests for taxa/fetch_taxa.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.taxa.fetch_taxa import fetch_taxa


# Just to make codecov happy
def test_fetch_taxa_calls_client_and_enrichers():
    dummy_taxa = MagicMock()

    with (
        patch("manexp_web_lists.taxa.fetch_taxa.JsonClient.download_file") as mock_download,
        patch("manexp_web_lists.taxa.fetch_taxa.JsonClient.load_file", return_value=dummy_taxa) as mock_load,
        patch("manexp_web_lists.taxa.fetch_taxa.varieties_to_taxa", return_value=dummy_taxa) as mock_var_to_tax,
        patch("manexp_web_lists.taxa.fetch_taxa.taxo_cleaner", return_value=dummy_taxa) as mock_cleaner,
        patch("manexp_web_lists.taxa.fetch_taxa.taxo_translator", return_value=dummy_taxa) as mock_translator,
        patch("manexp_web_lists.taxa.fetch_taxa.icon_generator", return_value=dummy_taxa) as mock_icon,
        patch("manexp_web_lists.taxa.fetch_taxa.color_generator", return_value=dummy_taxa) as mock_color,
        patch("manexp_web_lists.taxa.fetch_taxa.save_taxa") as mock_save,
    ):
        # Run
        fetch_taxa()

        # Assertions
        mock_download.assert_called_once()
        mock_load.assert_called_once()
        mock_var_to_tax.assert_called_once()
        mock_cleaner.assert_called_once()
        mock_translator.assert_called_once()
        mock_translator.assert_called_once()
        mock_icon.assert_called_once()
        mock_color.assert_called_once()
        mock_save.assert_called_once()

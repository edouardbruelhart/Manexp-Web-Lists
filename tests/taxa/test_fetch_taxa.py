"""Tests for taxa/fetch_taxa.py"""

from unittest.mock import patch

from manexp_web_lists.taxa.fetch_taxa import fetch_taxa


# Just to make codecov happy
def test_fetch_taxa_calls_client_and_enrichers():
    with (
        patch("manexp_web_lists.taxa.fetch_taxa.JsonClient.download_file") as mock_download,
        patch("manexp_web_lists.taxa.fetch_taxa.JsonClient.load_file") as mock_load,
        patch("manexp_web_lists.taxa.fetch_taxa.varieties_to_taxa") as mock_var_to_tax,
        patch("manexp_web_lists.taxa.fetch_taxa.mailer.taxo_resolver") as mock_resolver,
        patch("manexp_web_lists.taxa.fetch_taxa.taxo_translator") as mock_translator,
        patch("manexp_web_lists.taxa.fetch_taxa.icon_generator") as mock_icon,
        patch("manexp_web_lists.taxa.fetch_taxa.color_generator") as mock_color,
    ):
        # Run
        fetch_taxa()

        # Assertions
        mock_download.assert_called_once()
        mock_load.assert_called_once()
        mock_var_to_tax.assert_called_once()
        mock_resolver.assert_called_once()
        mock_translator.assert_called_once()
        mock_translator.assert_called_once()
        mock_icon.assert_called_once()
        mock_color.assert_called_once()

"""Tests for taxa/taxo_cleaner/resolve_taxonomy.py"""

from unittest.mock import patch

from manexp_web_lists.requests.gbif_requests import GBIFMatchResult, MatchStatus
from manexp_web_lists.taxa.models.taxonomy import TaxonRank
from manexp_web_lists.taxa.taxo_cleaner.resolve_taxonomy import resolve_taxonomy


def test_resolve_taxonomy_success():
    with patch("manexp_web_lists.taxa.taxo_cleaner.resolve_taxonomy.gbif_match_request") as mock_response:
        mock_response.return_value = GBIFMatchResult(
            status=MatchStatus.OK, data={"classification": [{"name": "Solanum", "rank": "GENUS"}]}
        )

        result = resolve_taxonomy("Solanum lycopersicum", TaxonRank.SPECIES, TaxonRank.GENUS)

    assert result == "Solanum"


def test_resolve_taxonomy_matcher_failure():
    with patch("manexp_web_lists.taxa.taxo_cleaner.resolve_taxonomy.gbif_match_request") as mock_response:
        mock_response.return_value = GBIFMatchResult(status=MatchStatus.NONE, data=None)

        result = resolve_taxonomy("Invalid name", TaxonRank.SPECIES, TaxonRank.GENUS)

    assert result is None


def test_resolve_taxonomy_empty_classification():
    with patch("manexp_web_lists.taxa.taxo_cleaner.resolve_taxonomy.gbif_match_request") as mock_response:
        mock_response.return_value = GBIFMatchResult(status=MatchStatus.OK, data={"classification": []})

        result = resolve_taxonomy("Something", TaxonRank.SPECIES, TaxonRank.GENUS)

    assert result is None


def test_resolve_taxonomy_no_classification():
    with patch("manexp_web_lists.taxa.taxo_cleaner.resolve_taxonomy.gbif_match_request") as mock_response:
        mock_response.return_value = GBIFMatchResult(status=MatchStatus.OK, data={"taxonomy": []})

        result = resolve_taxonomy("Something", TaxonRank.SPECIES, TaxonRank.GENUS)

    assert result is None

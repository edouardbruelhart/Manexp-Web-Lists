"""Tests for requests/gbif_requests.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.requests.gbif_requests import (
    MatchStatus,
    gbif_match_request,
    gbif_parser_request,
    gbif_search_request,
    gbif_vernaculars_request,
)
from manexp_web_lists.taxa.models.taxonomy import TaxonRank


def test_gbif_parser_success():
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = [{"parsed": True, "canonicalName": "Homo sapiens"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_parser_request("Homo sapiens")

        assert result["canonicalName"] == "Homo sapiens"


def test_gbif_parser_failed_parsing(caplog):
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = [{"parsed": False, "note": "Unparseable"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_parser_request("Invalid name")

        assert result is None
        assert "Failed to parse" in caplog.text


def test_gbif_match_success():
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"usageKey": 123, "diagnostics": {"matchType": "EXACT"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_match_request("Homo", TaxonRank.GENUS)

        assert result.status is MatchStatus.OK
        assert result.data["usageKey"] == 123


def test_gbif_match_none(caplog):
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"diagnostics": {"matchType": "NONE", "note": "No match found"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_match_request("Unknown", TaxonRank.GENUS)

        assert result.status is MatchStatus.NONE
        assert result.data is None
        assert "No match found" in caplog.text


def test_gbif_match_no_note(caplog):
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"diagnostics": {"matchType": "NONE"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_match_request("Unknown", TaxonRank.GENUS)

        assert result.status is MatchStatus.NONE
        assert result.data is None
        assert "No match found" in caplog.text


def test_gbif_match_multi(caplog):
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"diagnostics": {"matchType": "NONE", "note": "Multiple matches found"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_match_request("Unknown", TaxonRank.GENUS)

        assert result.status is MatchStatus.MULTIPLE
        assert result.data is None
        assert "Multiple matches found" in caplog.text


def test_gbif_search_results():
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"count": 1, "results": [{"key": 123}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_search_request("Homo", TaxonRank.GENUS)

        assert len(result) == 1


def test_gbif_search_no_results(caplog):
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"count": 0, "results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_search_request("Unknown", TaxonRank.GENUS)

        assert result is None
        assert "No search results found" in caplog.text


def test_gbif_vernaculars_success():
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"vernacularName": "Human"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_vernaculars_request("123")

        assert result[0]["vernacularName"] == "Human"


def test_gbif_vernaculars_empty(caplog):
    with patch("manexp_web_lists.requests.gbif_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gbif_vernaculars_request("123")

        assert result is None
        assert "No vernacular names found" in caplog.text

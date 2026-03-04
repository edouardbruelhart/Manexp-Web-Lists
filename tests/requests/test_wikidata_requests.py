"""Tests for requests/wikidata_requests.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.requests.wikidata_requests import wikidata_labels_request, wikidata_qid_request


def test_wikidata_qid_request_success():
    with patch("manexp_web_lists.requests.wikidata_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "search": [{"id": "Q123"}],
            "diagnostics": {"matchType": "EXACT"},
        }

        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = wikidata_qid_request("Homo sapiens")

        assert result == "Q123"


def test_wikidata_qid_request_fail(caplog):
    with patch("manexp_web_lists.requests.wikidata_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "diagnostics": {"matchType": "NONE"},
        }

        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = wikidata_qid_request("Invalid name")

        assert result is None
        assert "Failed to get WikiData QID" in caplog.text


def test_wikidata_labels_request_success():
    with patch("manexp_web_lists.requests.wikidata_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entities": {
                "Q123": {
                    "labels": {
                        "en": {"language": "en", "value": "Human being"},
                        "fr": {"language": "fr", "value": "Être humain"},
                    }
                }
            },
            "diagnostics": {"matchType": "EXACT"},
        }

        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = wikidata_labels_request("Q123")

        assert result["en"]["value"] == "Human being"


def test_wikidata_labels_request_none(caplog):
    with patch("manexp_web_lists.requests.wikidata_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = None

        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = wikidata_labels_request("Q123")

        assert result is None
        assert "Failed to get WikiData labels for QID" in caplog.text


def test_wikidata_labels_request_malformed(caplog):
    with patch("manexp_web_lists.requests.wikidata_requests.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entity": {
                "Q123": {
                    "labels": {
                        "en": {"language": "en", "value": "Human being"},
                        "fr": {"language": "fr", "value": "Être humain"},
                    }
                }
            },
            "diagnostics": {"matchType": "EXACT"},
        }

        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = wikidata_labels_request("Q123")

        assert result is None
        assert "Failed to get WikiData labels for QID" in caplog.text

"""Tests for core/json_client.py"""

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from manexp_web_lists.core.json_client import JsonClient


class MyModel(BaseModel):
    x: int
    y: str


def test_download_file(tmp_path):
    url = "http://example.com/data.json"
    file_path = tmp_path / "data.json"

    client = JsonClient()

    # Fake JSON content
    fake_json_bytes = b'{"x": 123, "y": "abc"}'

    with patch("manexp_web_lists.core.json_client.requests.Session") as mock_session:
        mock_get = mock_session.return_value.__enter__.return_value.get
        mock_response = MagicMock()
        mock_response.content = fake_json_bytes
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        client.download_file(url, file_path)

        # Assertions
        mock_get.assert_called_once_with(url)
        mock_response.raise_for_status.assert_called_once()

        # Check file written correctly
        written_text = file_path.read_text(encoding="utf-8")
        data = json.loads(written_text)
        assert data == {"x": 123, "y": "abc"}


def test_load_file_valid(tmp_path):
    file = tmp_path / "data.json"
    file.write_text('{"x": 42, "y": "hello"}')

    client = JsonClient()
    result = client.load_file(file, MyModel)

    assert isinstance(result, MyModel)
    assert result.x == 42
    assert result.y == "hello"


def test_load_file_invalid(tmp_path):
    file = tmp_path / "data.json"
    file.write_text('{"x": "not-an-int", "y": 5}')

    client = JsonClient()
    with pytest.raises(ValidationError):  # pydantic.ValidationError
        client.load_file(file, MyModel)

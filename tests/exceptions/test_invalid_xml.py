"""Tests for exceptions/invalid_xml.py"""

from manexp_web_lists.exceptions import InvalidXMLError


def test_invalid_xml_error() -> None:
    error = InvalidXMLError()

    assert str(error) == "The xml you are trying to parse is empty or incomplete."

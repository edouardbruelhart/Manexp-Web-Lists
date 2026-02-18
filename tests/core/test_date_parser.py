"""Tests for core/date_parser.py"""

import pytest

from manexp_web_lists.core.date_parser import parse_iso_date


def test_date_parser_valid():
    string = "2023-01-01"
    date = parse_iso_date(string)
    assert date.year == 2023
    assert date.month == 1
    assert date.day == 1


def test_date_parser_invalid():
    string = "Invalid date"
    with pytest.raises(TypeError):
        parse_iso_date(string)

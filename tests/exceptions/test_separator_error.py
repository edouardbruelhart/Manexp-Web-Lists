"""Tests for exceptions/separator_error.py"""

from manexp_web_lists.exceptions import SeparatorError


def test_invalid_chemical_error() -> None:
    error = SeparatorError()

    assert str(error) == "You must provide at least one non null separator."

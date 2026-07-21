"""Tests for exceptions/invalid_pseudo_boolean.py"""

from manexp_web_lists.exceptions import InvalidPseudoBoolError


def test_invalid_chemical_error() -> None:
    error = InvalidPseudoBoolError("Yep")

    assert error.invalid_bool == "Yep"
    assert str(error) == "Invalid pseudo boolean: Yep"

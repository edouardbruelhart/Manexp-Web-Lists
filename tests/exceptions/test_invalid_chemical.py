"""Tests for exceptions/invalid_chemical.py"""

from manexp_web_lists.exceptions import InvalidChemicalError


def test_invalid_chemical_error() -> None:
    error = InvalidChemicalError("H₂SO₄")

    assert error.invalid_chemical == "H₂SO₄"
    assert str(error) == "Invalid chemical content: H₂SO₄"

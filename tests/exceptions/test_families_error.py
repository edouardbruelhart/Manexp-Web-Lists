"""Tests for exceptions/families_error.py"""

from manexp_web_lists.exceptions.families_error import FamiliesError


def test_families_error_message():
    exc = FamiliesError()

    assert str(exc).startswith("New dataset families don't match old dataset families.")

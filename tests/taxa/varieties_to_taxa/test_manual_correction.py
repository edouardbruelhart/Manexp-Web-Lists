"""Tests for taxa/varieties_to_taxa/manual_correction.py"""

from manexp_web_lists.taxa.varieties_to_taxa.manual_correction import apply_manual_correction


def test_manual_correction_in_list():
    correction = apply_manual_correction("Fragaria xananassa Duch.")
    assert correction == "Fragaria ananassa"


def test_manual_correction_not_in_list():
    correction = apply_manual_correction("not in list")
    assert correction == "not in list"


def test_manual_correction_not_string():
    correction = apply_manual_correction(123)
    assert correction == 123

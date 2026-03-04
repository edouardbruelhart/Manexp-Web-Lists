"""Tests for exceptions/crop_category_mismatch.py"""

from manexp_web_lists.exceptions.crop_category_mismatch import CropCategoryMismatchError


def test_crop_category_mismatch_error_message():
    exc = CropCategoryMismatchError(
        focal_name="Tomato",
        first_crop_category="Fruit",
        second_crop_category="Vegetable",
    )

    assert str(exc) == ("Crop category mismatch for Tomato: Fruit != Vegetable")


def test_crop_category_mismatch_error_attributes():
    exc = CropCategoryMismatchError(
        focal_name="Tomato",
        first_crop_category="Fruit",
        second_crop_category="Vegetable",
    )

    assert exc.focal_name == "Tomato"
    assert exc.first_crop_category == "Fruit"
    assert exc.second_crop_category == "Vegetable"

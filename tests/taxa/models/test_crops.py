"""Tests for taxa/models/crops.py"""

import pytest
from pydantic import ValidationError

from manexp_web_lists.taxa.models.crops import Crop, CropCategory, Crops


def test_crop_category_from_string():
    cat = CropCategory("Fruit and berries")
    assert cat is CropCategory.FRUIT


def test_crop_category_from_enum():
    cat = CropCategory(CropCategory.VEGETABLE)
    assert cat is CropCategory.VEGETABLE
    assert cat.value == "Vegetable Crops"


def test_crop_category_invalid_value():
    with pytest.raises(ValueError):
        CropCategory("Invalid category")


def test_crop_category_invalid_type():
    with pytest.raises(ValueError):
        CropCategory(123)


def test_crop_valid():
    crop = Crop(
        id="123",
        status="Approved",
        upov_code="UPOV-001",
        denomination="Golden Apple",
    )

    assert crop.id == "123"
    assert crop.status == "Approved"


def test_crop_missing_field():
    with pytest.raises(ValidationError):
        Crop(
            id="123",
            status="Approved",
            upov_code="UPOV-001",
        )


def test_crop_extra_field():
    with pytest.raises(ValidationError):
        Crop(
            id="123",
            status="Approved",
            upov_code="UPOV-001",
            denomination="Golden Apple",
            extra="boom",
        )


def test_crop_invalid_field():
    with pytest.raises(ValidationError):
        Crop(
            id=123,
            status="Approved",
            upov_code="UPOV-001",
            denomination="Golden Apple",
        )


def test_crops_valid():
    crops = Crops(
        crops=[
            Crop(
                id="123",
                status="Approved",
                upov_code="UPOV-001",
                denomination="Golden Apple",
            ),
            Crop(
                id="456",
                status="Approved",
                upov_code="UPOV-002",
                denomination="Cherry Tomato",
            ),
        ]
    )

    assert len(crops.crops) == 2
    assert crops.crops[0].denomination == "Golden Apple"


def test_crops_invalid_nested_crop():
    with pytest.raises(ValidationError):
        Crops(
            crops=[
                Crop(
                    id="123",
                    status="Approved",
                    upov_code="UPOV-001",
                    # Missing denomination
                )
            ]
        )

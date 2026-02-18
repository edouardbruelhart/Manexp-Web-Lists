"""Tests for core/strict_model.py"""

import pytest
from pydantic import ValidationError

from manexp_web_lists.core.strict_model import StrictModel


# Create a concrete subclass for testing
class User(StrictModel):
    id: int
    name: str


def test_extra_fields_are_forbidden():
    # 'age' is not defined, should raise ValidationError
    with pytest.raises(ValidationError):
        User(id=1, name="Alice", age=30)


def test_strict_types():
    # 'id' should be int, passing a str should fail because strict=True
    with pytest.raises(ValidationError):
        User(id="1", name="Alice")


def test_frozen_model():
    user = User(id=1, name="Alice")
    with pytest.raises(ValidationError):
        user.id = 2  # frozen=True prevents assignment


def test_population_by_name():
    # Populate by field name works
    user = User(id=10, name="Bob")
    assert user.id == 10
    assert user.name == "Bob"

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from manexp_web_lists.exceptions import InvalidPseudoBoolError
from manexp_web_lists.seeds.transform.booleanize_plant_varieties import (
    booleanize_plant_varieties,
    convert_pseudo_bool_to_bool,
)


def test_convert_pseudo_bool_to_bool_success():
    result_true = convert_pseudo_bool_to_bool("Y")
    result_false = convert_pseudo_bool_to_bool("N")

    assert result_true
    assert not result_false


def test_convert_pseudo_bool_to_bool_failure():
    with pytest.raises(InvalidPseudoBoolError) as exc_info:
        convert_pseudo_bool_to_bool("Yep")

    assert exc_info.value.invalid_bool == "Yep"
    assert str(exc_info.value) == "Invalid pseudo boolean: Yep"


def test_booleanize_plant_varieties():
    booleans = pl.DataFrame({"is_gmo": ["Yes"], "is_hybrid": ["Y"], "is_organic": [""]})

    expected = pl.DataFrame({"is_gmo": [True], "is_hybrid": [True], "is_organic": [False]})

    result = booleanize_plant_varieties(booleans)

    assert_frame_equal(result, expected)

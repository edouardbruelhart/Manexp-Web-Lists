from manexp_web_lists.exceptions import UnsupportedTypeError


def test_unsupported_type_error() -> None:
    error = UnsupportedTypeError("culture", "culture_additional_text_id", "uuid")

    assert error.table == "culture"
    assert error.column == "culture_additional_text_id"
    assert error.dtype == "uuid"
    assert str(error) == ("Unsupported type for culture.culture_additional_text_id: uuid")

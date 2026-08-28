from manexp_web_lists.exceptions import UnexpectedIndicationError


def test_unexpeced_indication_error() -> None:
    error = UnexpectedIndicationError("UnknownElement")

    assert error.element == "UnknownElement"
    assert str(error) == "Unexpected element in Indication: UnknownElement"

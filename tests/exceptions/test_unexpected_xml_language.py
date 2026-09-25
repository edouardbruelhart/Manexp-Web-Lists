from manexp_web_lists.exceptions import UnexpectedXMLLanguageError


def test_unexpected_xml_element_error() -> None:
    error = UnexpectedXMLLanguageError("spanish")

    assert error.language == "spanish"
    assert str(error) == "Unexpected XML language: spanish"

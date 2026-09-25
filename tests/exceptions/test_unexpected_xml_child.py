from manexp_web_lists.exceptions import UnexpectedXMLChildError


def test_unexpected_xml_child_error() -> None:
    error = UnexpectedXMLChildError("unexpected_child")

    assert error.child == "unexpected_child"
    assert str(error) == "Unexpected XML child: unexpected_child"

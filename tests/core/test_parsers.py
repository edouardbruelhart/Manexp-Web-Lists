from manexp_web_lists.core.parsers import parse_strings_to_list


def test_parse_strings_to_list_success():
    result = parse_strings_to_list("test/test2,test3+test4")

    assert result == ["test", "test2", "test3", "test4"]


def test_parse_strings_to_list_none():
    result = parse_strings_to_list(None)

    assert result is None


def test_parse_strings_to_list_null():
    result = parse_strings_to_list(",")

    assert not result


def test_parse_strings_to_list_preserves_numeric_slash() -> None:
    assert parse_strings_to_list("1/2") == ["1/2"]

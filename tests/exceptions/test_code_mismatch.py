from manexp_web_lists.exceptions import CodeMismatchError


def test_code_mismatch_error() -> None:
    error = CodeMismatchError("code", "MN1052", "MN1054")

    assert error.column == "code"
    assert error.code_1 == "MN1052"
    assert error.code_2 == "MN1054"
    assert str(error) == "Value for 'code' differs between languages: 'MN1052' != 'MN1054'"

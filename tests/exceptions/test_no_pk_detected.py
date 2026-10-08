from manexp_web_lists.exceptions import NoPKDetectedError


def test_no_pk_detected_error() -> None:
    error = NoPKDetectedError("Table")

    assert error.table_name == "Table"
    assert str(error) == "No primary key detected in table Table."

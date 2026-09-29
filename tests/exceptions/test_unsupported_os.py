from manexp_web_lists.exceptions import UnsupportedOSError


def test_unsupported_os_error() -> None:
    error = UnsupportedOSError("Linux")

    assert error.os == "Linux"
    assert str(error) == (
        "Linux detected. "
        "PostgreSQL configuration cannot be automated on this system. "
        "Please install and configure PostgreSQL manually, disable automatic "
        "PostgreSQL configuration and then run the pipeline again."
    )

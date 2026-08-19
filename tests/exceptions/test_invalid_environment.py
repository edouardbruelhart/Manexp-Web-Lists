from manexp_web_lists.exceptions import InvalidEnvironmentError


def test_invalid_environment_error() -> None:
    error = InvalidEnvironmentError()

    assert (
        str(error)
        == "Environment configuration is incomplete. Please check the .env and be sure to add every information needed."
    )

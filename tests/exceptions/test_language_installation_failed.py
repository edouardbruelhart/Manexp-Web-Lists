from manexp_web_lists.exceptions import LanguageInstallationFailedError


def test_language_installation_failed_error() -> None:
    error = LanguageInstallationFailedError("fr", "en")

    assert error.src_lang == "fr"
    assert error.dest_lang == "en"
    assert str(error) == "Could not install Argos translation package for fr -> en"

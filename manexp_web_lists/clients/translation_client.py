from typing import cast

import argostranslate.package  # type: ignore[import-untyped]
import argostranslate.translate  # type: ignore[import-untyped]

from manexp_web_lists.exceptions import LanguageInstallationFailedError


def translate(text: str, src_lang: str, dest_lang: str) -> str:
    """
    Translate text using Argos Translate.

    Args:
        text: The text to translate
        src_lang: The source language of the text (for example: fr, en, de, it, ...)
        dest_lang: The language of the translation we want to obtain (for example: fr, en, de, it, ...)

    Returns:
        str: The translated text

    Raises:
        AttributeError: Raised when something fails in the translation
        LanguageInstallationFailedError: Raised when language package can't be installed automatically
    """

    try:
        # Try to tranlsate
        return cast(
            str,
            argostranslate.translate.translate(
                text,
                src_lang,
                dest_lang,
            ),
        )
    except AttributeError as error:
        # If it fails, jsut check that the language package is installed
        if "'NoneType' object has no attribute" not in str(error):
            raise

        # If absent, install it
        if not argostranslate.package.install_package_for_language_pair(
            src_lang,
            dest_lang,
        ):
            raise LanguageInstallationFailedError(src_lang, dest_lang) from error

        # Re-run the translation
        return cast(
            str,
            argostranslate.translate.translate(
                text,
                src_lang,
                dest_lang,
            ),
        )

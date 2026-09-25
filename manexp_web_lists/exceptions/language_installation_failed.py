class LanguageInstallationFailedError(Exception):
    """
    Raised when the language package can't be installed.

    Args:
            src_lang: The source language
            dest_lang: The destination language
    """

    def __init__(self, src_lang: str, dest_lang: str):
        self.src_lang = src_lang
        self.dest_lang = dest_lang

        message = f"Could not install Argos translation package for {src_lang} -> {dest_lang}"
        super().__init__(message)

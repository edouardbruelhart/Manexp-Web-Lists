class UnexpectedXMLLanguageError(Exception):
    """
    Raised when an unexpected XML language is met.

    Args:
            language: The unexpected XML language that triggered the error
    """

    def __init__(
        self,
        language: str | None,
    ):
        self.language = language

        message = f"Unexpected XML language: {self.language}"
        super().__init__(message)

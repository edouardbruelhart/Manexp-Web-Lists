class InvalidXMLError(Exception):
    """
    Raised when invalid xml is met.
    """

    def __init__(
        self,
    ) -> None:

        message = "The xml you are trying to parse is empty or incomplete."
        super().__init__(message)

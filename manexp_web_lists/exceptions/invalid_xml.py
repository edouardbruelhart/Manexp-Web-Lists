class InvalidXMLError(Exception):
    """
    Raised when invalid xml is met.
    """

    def __init__(
        self,
    ) -> None:

        super().__init__()

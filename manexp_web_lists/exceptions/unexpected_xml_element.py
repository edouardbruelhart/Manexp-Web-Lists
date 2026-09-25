class UnexpectedXMLElementError(Exception):
    """
    Raised when an unexpected XML element is met.

    Args:
            element: The unexpected element that triggered the error
    """

    def __init__(
        self,
        element: str,
    ):
        self.element = element

        message = f"Unexpected element: {self.element}"
        super().__init__(message)

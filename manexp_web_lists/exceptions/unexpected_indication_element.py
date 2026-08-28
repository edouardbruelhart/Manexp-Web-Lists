class UnexpectedIndicationError(Exception):
    """
    Raised when an unexpected indication element is met.

    Args:
            element: The unexpected element that triggered the error
    """

    def __init__(
        self,
        element: str,
    ):
        self.element = element

        message = f"Unexpected element in Indication: {self.element}"
        super().__init__(message)

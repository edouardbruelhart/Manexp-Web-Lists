class UnexpectedXMLChildError(Exception):
    """
    Raised when an unexpected XML child is met.

    Args:
            child: The unexpected XML child that triggered the error
    """

    def __init__(
        self,
        child: str,
    ):
        self.child = child

        message = f"Unexpected XML child: {self.child}"
        super().__init__(message)

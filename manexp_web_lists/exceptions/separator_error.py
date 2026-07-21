class SeparatorError(Exception):
    """
    Raised when an invalid separator is met
    """

    def __init__(
        self,
    ) -> None:

        message = "You must provide at least one non null separator."
        super().__init__(message)

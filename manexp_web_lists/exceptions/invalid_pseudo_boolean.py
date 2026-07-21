class InvalidPseudoBoolError(Exception):
    """
    Raised when invalid pseudo boolean is met.

    Args:
            invalid_bool: The invalid pseudo boolean that triggered the error
    """

    def __init__(
        self,
        invalid_bool: str,
    ):
        self.invalid_bool = invalid_bool

        message = f"Invalid pseudo boolean: {self.invalid_bool}"
        super().__init__(message)

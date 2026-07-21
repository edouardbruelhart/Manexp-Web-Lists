class InvalidChemicalError(Exception):
    """
    Raised when invalid or unknown chemical content is met.

    Args:
            invalid_chemical: The invalid chemical content that triggered the error
    """

    def __init__(
        self,
        invalid_chemical: str,
    ):
        self.invalid_chemical = invalid_chemical

        message = f"Invalid chemical content: {self.invalid_chemical}"
        super().__init__(message)

class InvalidEnvironmentError(Exception):
    """
    Raised when .env file is invalid or incomplete.
    """

    def __init__(
        self,
    ) -> None:

        message = "Environment configuration is incomplete. Please check the .env and be sure to add every information needed."
        super().__init__(message)

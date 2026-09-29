class UnsupportedOSError(Exception):
    """
    Raised when an unsupported operating system is detected.

    Args:
            os: The detected unsupported operating system
    """

    def __init__(
        self,
        os: str,
    ):
        self.os = os

        message = (
            f"{self.os} detected. "
            "PostgreSQL configuration cannot be automated on this system. "
            "Please install and configure PostgreSQL manually, disable automatic "
            "PostgreSQL configuration and then run the pipeline again."
        )
        super().__init__(message)

class NoPKDetectedError(Exception):
    """
    Raised when a table without primary key is detected

    Args:
            table_name: The table name that doesn't contain a primary key
    """

    def __init__(
        self,
        table_name: str,
    ):
        self.table_name = table_name

        message = f"No primary key detected in table {self.table_name}."
        super().__init__(message)

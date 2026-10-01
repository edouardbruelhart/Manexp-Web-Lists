class UnsupportedTypeError(Exception):
    """
    Raised when an unsupported type is encountered.

    Args:
        table: the name of the table where the unsupported type was encountered.
        column: the name of the column where the unsupported type was encountered.
        dtype: the type that was encountered.
    """

    def __init__(self, table: str, column: str, dtype: str):
        self.table = table
        self.column = column
        self.dtype = dtype

        message = f"Unsupported type for {self.table}.{self.column}: {self.dtype}"
        super().__init__(message)

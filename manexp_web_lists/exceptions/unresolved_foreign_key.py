class UnresolvedForeignKeyError(Exception):
    """
    Raised when an unsupported foreign key is encountered.

    Args:
        source_table: the name of the table that contains the foreign key
        source_column: the name of the column in the table that contains the foreign key
        target_table: the name of the table that is referenced by the foreign key
        target_column: the name of the column in the table that is referenced by the foreign key
    """

    def __init__(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_column: str,
    ):
        self.source_table = source_table
        self.source_column = source_column
        self.target_table = target_table
        self.target_column = target_column

        message = (
            f"Cannot resolve Foreing Key: "
            f"{self.source_table}.{self.source_column} -> "
            f"{self.target_table}.{self.target_column}"
        )
        super().__init__(message)

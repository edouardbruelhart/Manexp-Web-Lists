class CodeMismatchError(Exception):
    """
    Raised when the code is different among languages.

    Args:
            column: The unexpected XML child that triggered the error
            code_1: The first code
            code_2: The second code that is different from the first one
    """

    def __init__(self, column: str, code_1: str | None, code_2: str):
        self.column = column
        self.code_1 = code_1
        self.code_2 = code_2

        message = f"Value for '{column}' differs between languages: {code_1!r} != {code_2!r}"
        super().__init__(message)

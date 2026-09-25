import re

SEPARATORS = {
    "/",
    ",",
    "+",
}


def parse_strings_to_list(text: str | None) -> list[str] | None:
    """
    Parse text from a string into a list of strings.

    Args:
        text: The string to parse

    Returns:
        list[str] | None: The list of strings
    """

    if not text:
        return None

    # Protect numeric slashes as these are not separators but part of the denomination
    text = re.sub(r"(\d)//(\d)", r"\1§DOUBLE_SLASH§\2", text)
    text = re.sub(r"(\d)/(\d)", r"\1§SLASH§\2", text)

    # Replace every separator by ';'
    for sep in SEPARATORS:
        text = text.replace(sep, ";")

    # Restore protected slashes
    text = text.replace("§DOUBLE_SLASH§", "//").replace("§SLASH§", "/")

    # Split into list
    result = []

    for name in text.split(";"):
        if name:
            result.append(name)

    return result

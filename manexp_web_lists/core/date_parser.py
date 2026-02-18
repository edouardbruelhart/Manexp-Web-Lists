from datetime import date
from typing import Annotated

from pydantic import BeforeValidator


def parse_iso_date(date_str: str) -> date:
    """
    Take a string date and return a date object.

    Args:
        date_str: The date string to parse

    Returns:
        date: The parsed date object

    Raises:
        TypeError: If the date string is not valid
    """

    try:
        return date.fromisoformat(date_str)
    except ValueError as e:
        raise TypeError(e) from None


ISODate = Annotated[date, BeforeValidator(parse_iso_date)]

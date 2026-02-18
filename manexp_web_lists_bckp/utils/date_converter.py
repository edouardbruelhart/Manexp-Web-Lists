from datetime import date
from typing import Annotated

from pydantic import BeforeValidator


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as e:
        raise TypeError(e) from None


ISODate = Annotated[date, BeforeValidator(parse_iso_date)]

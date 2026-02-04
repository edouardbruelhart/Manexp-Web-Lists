from typing import Optional

from pydantic import Field

from manexp_web_lists.utils.strict_model import StrictModel


class Crop(StrictModel):
    id: str
    status: str
    crop_category: str
    family: Optional[str] = Field(default=None)
    genus: Optional[str] = Field(default=None)
    species: str
    upov_code: str
    denomination: str


class Crops(StrictModel):
    """Represents the cleaned list of crops."""

    crops: list[Crop]

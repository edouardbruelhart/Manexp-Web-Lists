from manexp_web_lists.utils.strict_model import StrictModel


class Crop(StrictModel):
    """Represents a crop."""

    id: str
    status: str
    upov_code: str
    denomination: str


class Crops(StrictModel):
    """Represents a list of crops."""

    crops: list[Crop]

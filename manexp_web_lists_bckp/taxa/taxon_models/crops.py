from manexp_web_lists.utils.strict_model import StrictModel
from pydantic import Field


class Crop(StrictModel):
    """Represents a crop."""

    id: str = Field(..., description="The UUID of the crop")
    status: str = Field(..., description="The validation status of the crop")
    upov_code: str = Field(..., description="The UPOV code of the crop. For more information: https://www.upov.int/en")
    denomination: str = Field(..., description="The official crop unique denomination")


class Crops(StrictModel):
    """Represents a list of crops."""

    crops: list[Crop] = Field(..., description="The list of crops")

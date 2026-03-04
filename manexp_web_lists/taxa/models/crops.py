from enum import Enum

from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import BeforeValidatorFunctionSchema

from manexp_web_lists.core.strict_model import StrictModel


class CropCategory(str, Enum):
    """Represent the crop category of the taxon"""

    VEGETABLE = "Vegetable Crops"
    ORNAMENTAL = "Ornamental and medicinal plants"
    FRUIT = "Fruit and berries"
    AGRICULTURAL = "Agricultural Crops"

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type["CropCategory"],
        _: type,
        handler: GetCoreSchemaHandler,
    ) -> BeforeValidatorFunctionSchema:
        return core_schema.no_info_before_validator_function(
            cls._parse,
            handler(cls),
        )

    @classmethod
    def _parse(cls: type["CropCategory"], value: str) -> str:
        """
        Parse the crop category.

        Args:
            value: The crop category to parse

        Returns:
            str: The parsed crop category
        """
        if isinstance(value, cls):
            return value
        return cls(value)


class Crop(StrictModel):
    """Represent a crop."""

    id: str = Field(..., description="The UUID of the crop")
    status: str = Field(..., description="The validation status of the crop")
    upov_code: str = Field(..., description="The UPOV code of the crop. For more information: https://www.upov.int/en")
    denomination: str = Field(..., description="The official crop unique denomination")


class Crops(StrictModel):
    """Represent a list of crops."""

    crops: list[Crop] = Field(..., description="The list of crops corresponding to a taxon")

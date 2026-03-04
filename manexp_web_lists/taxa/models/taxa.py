from enum import Enum

from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import BeforeValidatorFunctionSchema

from manexp_web_lists.core.strict_model import StrictModel
from manexp_web_lists.taxa.models.crops import CropCategory, Crops
from manexp_web_lists.taxa.models.taxonomy import CleanedTaxonomy, RawTaxonomy
from manexp_web_lists.taxa.models.translations import Translations


class Icon(str, Enum):
    """Represent icons that describe main crop usages (Does not reflect CropCategory)."""

    CEREALS = "wheat"
    ORNAMENTAL = "deceased"
    MEDICINAL = "pill"
    HERBS = "grass"
    FRUITS = "nutrition"
    VEGETABLES = "restaurant"
    TREES = "nature"
    SUCCULENTS = "spa"

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type["Icon"],
        _: type,
        handler: GetCoreSchemaHandler,
    ) -> BeforeValidatorFunctionSchema:
        return core_schema.no_info_before_validator_function(
            cls._parse,
            handler(cls),
        )

    @classmethod
    def _parse(cls: type["Icon"], value: str) -> str:
        """
        Parse the icon.

        Args:
            value: The icon to parse

        Returns:
            str: The parsed icon"""

        if isinstance(value, cls):
            return value
        else:
            return cls(value)


class RawTaxon(StrictModel):
    """Represent the raw taxon model"""

    crop_category: CropCategory = Field(..., description="The crop category of the taxon")
    taxonomy: RawTaxonomy = Field(..., description="The raw taxonomy of the taxon")
    crops: Crops = Field(..., description="The crops of the taxon")


class RawTaxa(StrictModel):
    """Represent the raw taxa model"""

    taxa: list[RawTaxon] = Field(..., description="The list of taxa")


class CleanedTaxon(RawTaxon):
    """Represent the cleaned taxon model"""

    taxonomy: CleanedTaxonomy = Field(..., description="The cleaned taxonomy of the taxon")


class CleanedTaxa(StrictModel):
    """Represent the cleaned taxa model"""

    taxa: list[CleanedTaxon] = Field(..., description="The list of taxa")


class TranslatedTaxon(CleanedTaxon):
    """Represent the translated taxon model"""

    translations: Translations = Field(..., description="The list of translations")


class TranslatedTaxa(StrictModel):
    """Represent the translated taxa model"""

    taxa: list[TranslatedTaxon] = Field(..., description="The list of taxa")


class IconedTaxon(TranslatedTaxon):
    """Represent the iconed taxon model"""

    icon: Icon = Field(..., description="The icon of the taxon, based on the taxon family")


class IconedTaxa(StrictModel):
    """Represent the iconed taxa model"""

    taxa: list[IconedTaxon] = Field(..., description="The list of taxa")


class ColoredTaxon(IconedTaxon):
    """Represent the colored taxon model"""

    color: str = Field(..., description="The color of the taxon, generated from the focal name")


class ColoredTaxa(StrictModel):
    """Represent the colored taxa model"""

    taxa: list[ColoredTaxon] = Field(..., description="The list of taxa")

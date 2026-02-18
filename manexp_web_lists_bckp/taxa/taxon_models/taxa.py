from enum import Enum

from manexp_web_lists.taxa.taxon_models.crops import Crops
from manexp_web_lists.taxa.taxon_models.taxonomy import RawTaxonomy, ResolvedTaxonomy
from manexp_web_lists.taxa.taxon_models.translations import Translations
from manexp_web_lists.utils.strict_model import StrictModel
from pydantic import Field, field_validator


class CropCategory(str, Enum):
    """
    Represents the crop category of the taxon

    Attributes:
        VEGETABLE (str): Vegetable crop category
        ORNAMENTAL (str): Ornamental and medicinal plants
        FRUIT (str): Fruit and berries
        AGRICULTURAL (str): Agricultural Crops
    """

    VEGETABLE = "Vegetable Crops"
    ORNAMENTAL = "Ornamental and medicinal plants"
    FRUIT = "Fruit and berries"
    AGRICULTURAL = "Agricultural Crops"


class Icon(str, Enum):
    """
    Icons representing main crop usages (Does not reflect crop category)

    Attributes:
        CEREALS (str): Wheat

    """

    CEREALS = "wheat"
    """Cereals. Associated to all poaceae"""

    ORNAMENTAL = "deceased"
    """Ornamental plants. Associated to families that mainly contain ornamental plants"""

    MEDICINAL = "pill"
    """Medicinal plants. Associated to familites that mainly contain medicinal plants"""

    HERBS = "grass"
    """Herbs plants. Associated to families that mainly contain herbs"""

    FRUITS = "nutrition"
    """Fruits plants. Associated to families that mainly contain fruits and berries plants"""

    VEGETABLES = "restaurant"
    """Vegetables plants. Associated to families that mainly contain vegetables plants"""

    TREES = "nature"
    """Trees. Associated to families that mainlx contain woody plants"""

    SUCCULENTS = "spa"
    """Succulent plants. Associated to families that mainly contain succulent plants"""


class RawTaxon(StrictModel):
    """Represents the raw taxon model"""

    crop_category: CropCategory = Field(..., description="The crop category of the taxon")
    taxonomy: RawTaxonomy = Field(..., description="The taxonomy of the taxon")
    crops: Crops = Field(..., description="The crops of the taxon")

    @field_validator("crop_category", mode="before")
    @classmethod
    def parse_taxonomy(cls: type["RawTaxon"], v: str | CropCategory) -> CropCategory:
        """
        Parse the crop category.

        Args:
            cls (type["RawTaxon"]): Class
            v (str | CropCategory): Source

        Returns:
            CropCategory: Valid value
        """
        if isinstance(v, str):
            return CropCategory(v)
        return v


class RawTaxa(StrictModel):
    """Represents the raw taxa model"""

    taxa: list[RawTaxon] = Field(..., description="The list of taxa")


class ResolvedTaxon(RawTaxon):
    """Represents the resolved taxon model"""

    taxonomy: ResolvedTaxonomy = Field(..., description="The taxonomy of the taxon")


class ResolvedTaxa(StrictModel):
    """Represents the resolved taxa model"""

    taxa: list[ResolvedTaxon] = Field(..., description="The list of taxa")


class TranslatedTaxon(ResolvedTaxon):
    """Represents the translated taxon model"""

    translations: Translations = Field(..., description="The list of translations")


class TranslatedTaxa(StrictModel):
    """Represents the translated taxa model"""

    taxa: list[TranslatedTaxon] = Field(..., description="The list of taxa")


class IconedTaxon(TranslatedTaxon):
    """Represents the iconed taxon model"""

    icon: Icon = Field(..., description="The icon of the taxon, based on the taxon family")


class IconedTaxa(StrictModel):
    """Represents the iconed taxa model"""

    taxa: list[IconedTaxon] = Field(..., description="The list of taxa")


class ColoredTaxon(IconedTaxon):
    """Represents the colored taxon model"""

    color: str = Field(..., description="The color of the taxon, generated from the focal name")


class ColoredTaxa(StrictModel):
    """Represents the colored taxa model"""

    taxa: list[ColoredTaxon] = Field(..., description="The list of taxa")

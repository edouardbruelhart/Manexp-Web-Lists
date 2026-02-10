from enum import Enum
from typing import Optional

from pydantic import field_validator

from manexp_web_lists.utils.strict_model import StrictModel
from manexp_web_lists.varieties.models.crops import Crops


class TranslationSource(str, Enum):
    """Defines where does the translation come from"""

    WIKIDATA = "wikidata"
    GBIF = "gbif"
    GOOGLE = "google"


class Translation(StrictModel):
    """Represents a translation"""

    name: str
    source: TranslationSource


class Translations(StrictModel):
    """Represents the translations"""

    fr: Translation
    en: Translation
    de: Translation
    it: Translation


class TaxonRank(str, Enum):
    """Represents the rank of the taxon"""

    GENUS = "genus"
    SPECIES = "species"


class RawTaxon(StrictModel):
    """Represents the raw taxon model"""

    crop_category: str
    taxon_rank: TaxonRank
    family: Optional[str]
    genus: Optional[str]
    species: Optional[str]
    crops: Crops

    @field_validator("taxon_rank", mode="before")
    @classmethod
    def parse_taxon_rank(cls: type["RawTaxon"], v: str | TaxonRank) -> TaxonRank:
        if isinstance(v, str):
            return TaxonRank(v)
        return v


class RawTaxons(StrictModel):
    """Represents the raw taxons model"""

    taxons: list[RawTaxon]


class ResolvedTaxon(RawTaxon):
    """Represents the resolved taxon model"""

    family: str
    genus: str


class ResolvedTaxons(StrictModel):
    """Represents the resolved taxons model"""

    taxons: list[ResolvedTaxon]


class TranslatedTaxon(ResolvedTaxon):
    """Represents the translated taxon model"""

    translations: Translations


class TranslatedTaxons(StrictModel):
    """Represents the translated taxons model"""

    taxons: list[TranslatedTaxon]


class ColoredTaxon(TranslatedTaxon):
    """Represents the colored taxon model"""

    color: str


class ColoredTaxons(StrictModel):
    """Represents the colored taxons model"""

    taxons: list[ColoredTaxon]


class IconedTaxon(ColoredTaxon):
    """Represents the iconed taxon model"""

    icon: str


class IconedTaxons(StrictModel):
    """Represents the iconed taxons model"""

    taxons: list[IconedTaxon]

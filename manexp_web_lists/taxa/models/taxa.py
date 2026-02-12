from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from manexp_web_lists.taxa.models.crops import Crops
from manexp_web_lists.utils.strict_model import StrictModel


class TranslationSource(str, Enum):
    """Defines where does the translation come from"""

    WIKIDATA = "wikidata"
    GBIF = "gbif"
    GOOGLE = "google"


class Translation(StrictModel):
    """Represents a translation"""

    name: str
    source: TranslationSource

    @field_validator("source", mode="before")
    @classmethod
    def parse_taxon_rank(cls: type["Translation"], v: str | TranslationSource) -> TranslationSource:
        if isinstance(v, str):
            return TranslationSource(v)
        return v


class Translations(StrictModel):
    """Represents the translations for a taxon"""

    fr: Translation = Field(..., description="French translation")
    en: Translation = Field(..., description="English translation")
    de: Translation = Field(..., description="German translation")
    it: Translation = Field(..., description="Italian translation")


class TaxonRank(str, Enum):
    """Represents the rank of the taxon"""

    GENUS = "genus"
    SPECIES = "species"


class RawClassification(StrictModel):
    """Represents the raw classification model"""

    family: Optional[str]
    genus: Optional[str]
    species: Optional[str]
    focal_name: str


class ResolvedClassification(RawClassification):
    """Represents the resolved classification model"""

    family: str
    genus: str


class RawTaxonomy(StrictModel):
    """Represents the raw taxonomy model"""

    rank: TaxonRank
    raw_classification: RawClassification

    @field_validator("rank", mode="before")
    @classmethod
    def parse_taxon_rank(cls: type["RawTaxonomy"], v: str | TaxonRank) -> TaxonRank:
        if isinstance(v, str):
            return TaxonRank(v)
        return v


class ResolvedTaxonomy(RawTaxonomy):
    """Represents the resolved taxonomy model"""

    resolved_classification: ResolvedClassification


class RawTaxon(StrictModel):
    """Represents the raw taxon model"""

    crop_category: str
    taxonomy: RawTaxonomy
    crops: Crops


class RawTaxa(StrictModel):
    """Represents the raw taxa model"""

    taxa: list[RawTaxon]


class ResolvedTaxon(RawTaxon):
    """Represents the resolved taxon model"""

    taxonomy: ResolvedTaxonomy


class ResolvedTaxa(StrictModel):
    """Represents the resolved taxa model"""

    taxa: list[ResolvedTaxon]


class TranslatedTaxon(ResolvedTaxon):
    """Represents the translated taxon model"""

    translations: Translations


class TranslatedTaxa(StrictModel):
    """Represents the translated taxa model"""

    taxa: list[TranslatedTaxon]


class IconedTaxon(TranslatedTaxon):
    """Represents the iconed taxon model"""

    icon: str


class IconedTaxa(StrictModel):
    """Represents the iconed taxa model"""

    taxa: list[IconedTaxon]


class ColoredTaxon(IconedTaxon):
    """Represents the colored taxon model"""

    color: str


class ColoredTaxa(StrictModel):
    """Represents the colored taxa model"""

    taxa: list[ColoredTaxon]

from enum import Enum
from typing import Optional

from manexp_web_lists.utils.strict_model import StrictModel
from pydantic import Field, field_validator


class TaxonRank(str, Enum):
    """
    Represents the rank of the taxon

    Attributes:
        GENUS (str): Genus rank, so no species defined
        SPECIES (str): Species rank
    """

    GENUS = "genus"
    SPECIES = "species"


class RawClassification(StrictModel):
    """
    Represents the raw classification model, hosting the raw list values

    Attributes:
        family (Optional[str]): The family of the taxon
        genus (Optional[str]): The genus of the taxon
        species (Optional[str]): The species of the taxon
        focal_name (str): The focal name representing species if species is not null, else genus. Used for resolution and translation purposes

    """

    family: Optional[str]
    genus: Optional[str]
    species: Optional[str]
    focal_name: str


class ResolvedClassification(RawClassification):
    """
    Represents the resolved classification model, hosting the resolved values

    Attributes:
        family (str): The family of the taxon
        genus (str): The genus of the taxon
    """

    family: str
    genus: str


class RawTaxonomy(StrictModel):
    """
    Represents the raw taxonomy model, hosting the raw list

    Attributes:
        rank (TaxonRank): The rank of the taxon
        raw_classification (RawClassification): The raw classification of the taxon
    """

    rank: TaxonRank
    raw_classification: RawClassification

    @field_validator("rank", mode="before")
    @classmethod
    def parse_taxon_rank(cls: type["RawTaxonomy"], source: str | TaxonRank) -> TaxonRank:
        """
        Parse the rank of the taxon.

        Args:
            cls (type["RawTaxonomy"]): RawTaxonomy class
            source (str | TaxonRank): Taxon rank source

        Returns:
            TaxonRank: Taxon rank value
        """

        if isinstance(source, str):
            return TaxonRank(source)
        return source


class ResolvedTaxonomy(RawTaxonomy):
    """Represents the resolved taxonomy model"""

    resolved_classification: ResolvedClassification = Field(..., description="The resolved classification of the taxon")

from enum import Enum
from typing import Optional

from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import BeforeValidatorFunctionSchema

from manexp_web_lists.core.strict_model import StrictModel


class TaxonRank(str, Enum):
    """
    Represent the rank of the taxon
    """

    FAMILY = "family"
    GENUS = "genus"
    SPECIES = "species"

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type["TaxonRank"],
        _: type,
        handler: GetCoreSchemaHandler,
    ) -> BeforeValidatorFunctionSchema:
        return core_schema.no_info_before_validator_function(
            cls._parse,
            handler(cls),
        )

    @classmethod
    def _parse(cls: type["TaxonRank"], value: str) -> str:
        """
        Parse the rank.

        Args:
            value: The rank to parse

        Returns:
            str: The parsed rank
        """

        if isinstance(value, cls):
            return value
        return cls(value)


class RawClassification(StrictModel):
    """Represent the raw classification model."""

    family: Optional[str] = Field(None, description="Taxon family")
    genus: Optional[str] = Field(None, description="Taxon genus")
    species: Optional[str] = Field(None, description="Taxon species")
    focal_name: str = Field(
        ...,
        description="Focal name of the taxon. This represents the lowest level of the classification for a specific taxon.",
    )


class CleanedClassification(RawClassification):
    """Represent the cleaned classification model."""

    family: str = Field(..., description="Taxon family")
    genus: str = Field(..., description="Taxon genus")


class RawTaxonomy(StrictModel):
    """Represent the raw taxonomy model."""

    rank: TaxonRank = Field(..., description="Rank of the lowest level of the classification for a specific taxon.")
    raw_classification: RawClassification = Field(..., description="The raw classification of the taxon")


class CleanedTaxonomy(RawTaxonomy):
    """Represent the cleaned taxonomy model."""

    cleaned_classification: CleanedClassification = Field(..., description="The cleaned classification of the taxon")

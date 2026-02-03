from enum import Enum

from pydantic import UUID1, BaseModel, Field


class Species(BaseModel):
    """Represents a species object."""

    family: str
    genus: str
    species: str
    cleaned_species: str
    french_name: str
    english_name: str
    german_name: str
    italian_name: str
    icon: str
    color: str


class CropStatus(str, Enum):
    """Enumeration of possible crop statuses."""

    FINALIZED = "Finalized"
    PENDING = "InProgress"


class Crop(BaseModel):
    """Represents a specimen object."""

    id: UUID1
    status: CropStatus = Field(alias="dossierStatus")
    category: str = Field(alias="cropCategory")
    family: str
    genus: str
    species: str
    cleaned_species: str
    upov_code: str
    denomination: str
    owner: str

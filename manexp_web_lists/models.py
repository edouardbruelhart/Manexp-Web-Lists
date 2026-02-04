from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        frozen=True,  # makes objects immutable (optional but good for safety)
    )


class Address(StrictModel):
    name: str
    address: str
    post_box: str = Field(alias="postBox")
    postal_code: str = Field(alias="postalCode")
    city: str
    country: str


class BotanicalInfo(StrictModel):
    family: str
    genus: str
    species: str
    upov_code: str = Field(alias="upovCode")


class StatusHistory(StrictModel):
    status: str
    valid_from: date = Field(alias="validFrom")


class Denomination(StrictModel):
    denomination: str
    status_history: list[StatusHistory] = Field(alias="statusHistory")


class CurrentDenomination(StrictModel):
    denomination: str
    status: str
    valid_from: date = Field(alias="validFrom")


class PBRRequest(StrictModel):
    number: str
    entry_date: date = Field(alias="entryDate")


class PBRRegister(StrictModel):
    number: str
    grant_of_protection: date = Field(alias="grantOfProtection")
    max_protection_years: int = Field(alias="maxProtectionYears")


class PBRContacts(StrictModel):
    agent: Address


class PlantBreedersRight(StrictModel):
    status: str
    request: PBRRequest
    register_info: PBRRegister = Field(alias="register")
    contacts: PBRContacts


class VarietyContacts(StrictModel):
    owners: list[Address]
    breeders: list[Address]


class Variety(StrictModel):
    id: str
    dossier_status: str = Field(alias="dossierStatus")

    breeders_reference: Optional[str] = Field(default=None, alias="breedersReference")

    breeding_country: str = Field(alias="breedingCountry")

    trade_names: Optional[list[str]] = Field(default=None, alias="tradeNames")

    crop_category: str = Field(alias="cropCategory")

    botanical_info: BotanicalInfo = Field(alias="botanicalInformation")

    current_denomination: CurrentDenomination = Field(alias="currentlyRelevantDenomination")

    denominations: list[Denomination]

    plant_breeders_right: PlantBreedersRight = Field(alias="plantBreedersRight")

    contacts: VarietyContacts


class VarietiesResponse(StrictModel):
    varieties: list[Variety]

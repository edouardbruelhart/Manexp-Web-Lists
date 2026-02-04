from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as e:
        raise TypeError(e) from None


ISODate = Annotated[date, BeforeValidator(parse_iso_date)]


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        frozen=True,
        strict=True,
    )


class Address(StrictModel):
    name: str
    address: str
    post_box: Optional[str] = Field(default=None, alias="postBox")
    postal_code: Optional[str] = Field(default=None, alias="postalCode")
    city: Optional[str] = Field(default=None)
    country: str


class BotanicalInfo(StrictModel):
    family: Optional[str] = Field(default=None)
    genus: Optional[str] = Field(default=None)
    species: Optional[str] = Field(default=None)
    upov_code: str = Field(alias="upovCode")


class StatusHistory(StrictModel):
    status: str
    valid_from: ISODate = Field(alias="validFrom")


class Denomination(StrictModel):
    denomination: str
    status_history: list[StatusHistory] = Field(alias="statusHistory")


class CurrentDenomination(StrictModel):
    denomination: str
    status: str
    valid_from: ISODate = Field(alias="validFrom")


class PBRRequest(StrictModel):
    number: str
    entry_date: Optional[ISODate] = Field(default=None, alias="entryDate")


class PBRRegister(StrictModel):
    number: str
    grant_of_protection: ISODate = Field(alias="grantOfProtection")
    max_protection_years: int = Field(alias="maxProtectionYears")
    end_protection: Optional[ISODate] = Field(default=None, alias="endOfProtection")


class PBRContacts(StrictModel):
    agent: Address


class PlantBreedersRight(StrictModel):
    status: str
    request: PBRRequest
    register_info: Optional[PBRRegister] = Field(default=None, alias="register")
    contacts: PBRContacts


class VarietyContacts(StrictModel):
    owners: list[Address]
    breeders: list[Address]


class Variety(StrictModel):
    id: str
    dossier_status: str = Field(alias="dossierStatus")
    trade_names: Optional[list[str]] = Field(default=None, alias="tradeNames")
    brand_names: Optional[list[str]] = Field(default=None, alias="brandNames")
    breeders_reference: Optional[str] = Field(default=None, alias="breedersReference")
    breeding_country: Optional[str] = Field(default=None, alias="breedingCountry")
    crop_category: str = Field(alias="cropCategory")
    botanical_info: BotanicalInfo = Field(alias="botanicalInformation")
    current_denomination: Optional[CurrentDenomination] = Field(default=None, alias="currentlyRelevantDenomination")
    denominations: Optional[list[Denomination]] = Field(default=None)
    plant_breeders_right: PlantBreedersRight = Field(alias="plantBreedersRight")
    contacts: VarietyContacts


class Varieties(StrictModel):
    varieties: list[Variety]

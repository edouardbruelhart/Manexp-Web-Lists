from typing import Optional

from manexp_web_lists.utils.date_converter import ISODate
from manexp_web_lists.utils.strict_model import StrictModel
from pydantic import Field


class Address(StrictModel):
    """Represents an address."""

    name: str
    address: str
    post_box: Optional[str] = Field(default=None, alias="postBox")
    postal_code: Optional[str] = Field(default=None, alias="postalCode")
    city: Optional[str] = Field(default=None)
    country: str


class BotanicalInfo(StrictModel):
    """Represents botanical information."""

    family: Optional[str] = Field(default=None)
    genus: Optional[str] = Field(default=None)
    species: Optional[str] = Field(default=None)
    upov_code: str = Field(alias="upovCode")


class StatusHistory(StrictModel):
    """Represents a status history"""

    status: str
    valid_from: ISODate = Field(alias="validFrom")


class Denomination(StrictModel):
    """Represents a denomination"""

    denomination: str
    status_history: list[StatusHistory] = Field(alias="statusHistory")


class CurrentDenomination(StrictModel):
    """Represents the current denomination"""

    denomination: str
    status: str
    valid_from: ISODate = Field(alias="validFrom")


class PBRRequest(StrictModel):
    """Represents a plant breeders right request"""

    number: str
    entry_date: Optional[ISODate] = Field(default=None, alias="entryDate")


class PBRRegister(StrictModel):
    """Represents a plant breeders right Register"""

    number: str
    grant_of_protection: ISODate = Field(alias="grantOfProtection")
    max_protection_years: int = Field(alias="maxProtectionYears")
    end_protection: Optional[ISODate] = Field(default=None, alias="endOfProtection")


class PBRContact(StrictModel):
    """Represent a plant breeders right contact"""

    agent: Address


class PlantBreedersRight(StrictModel):
    """Represents a plant breeders right"""

    status: str
    request: PBRRequest
    register_info: Optional[PBRRegister] = Field(default=None, alias="register")
    contacts: PBRContact


class VarietyContacts(StrictModel):
    """Represents the contacts of a variety"""

    owners: list[Address]
    breeders: list[Address]


class Variety(StrictModel):
    """Represents a plant variety."""

    id: str
    status: str = Field(alias="dossierStatus")
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
    """Represents the raw data model for plant varieties."""

    varieties: list[Variety]

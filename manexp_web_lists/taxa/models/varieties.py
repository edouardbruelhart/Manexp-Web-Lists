from typing import Optional

from pydantic import Field, model_validator

from manexp_web_lists.core.date_parser import ISODate
from manexp_web_lists.core.strict_model import StrictModel
from manexp_web_lists.taxa.models.crops import CropCategory


class Contact(StrictModel):
    """Represent a contact."""

    name: str = Field(..., description="Name of the company")
    address: str = Field(..., description="Address of the company")
    post_box: Optional[str] = Field(default=None, alias="postBox", description="Post box of the company")
    postal_code: Optional[str] = Field(default=None, alias="postalCode", description="Postal code of the company")
    city: Optional[str] = Field(default=None, description="City of the company")
    country: str


class BotanicalInfo(StrictModel):
    """Represent botanical information."""

    family: Optional[str] = Field(default=None, description="Family of the plant")
    genus: Optional[str] = Field(default=None, description="Genus of the plant")
    species: Optional[str] = Field(default=None, description="Species of the plant")
    upov_code: str = Field(
        alias="upovCode", description="UPOV code of the plant. For more information: https://www.upov.int/en"
    )


class Status(StrictModel):
    """Represent a status"""

    status: str = Field(..., description="Application status")
    valid_from: ISODate = Field(alias="validFrom", description="Valid from date")


class Denomination(StrictModel):
    """Represent a denomination"""

    denomination: str = Field(..., description="Denomination of the crop")
    status_history: list[Status] = Field(alias="statusHistory", description="Status history of the crop")


class CurrentDenomination(StrictModel):
    """Represent the current denomination"""

    denomination: str = Field(..., description="Current denomination of the crop")
    status: Status = Field(..., description="Current status of the crop")

    @model_validator(mode="before")
    @classmethod
    def build_status(cls: type["CurrentDenomination"], source: dict) -> dict:
        """
        Transform flat input into nested Status.

        Args:
            source: Current denomination source

        Returns:
            dict: nested current denomination
        """

        # If already nested return it as is
        if "status" in source and isinstance(source["status"], dict):
            return source

        return {
            "denomination": source["denomination"],
            "status": {
                "status": source["status"],
                "validFrom": source["validFrom"],
            },
        }


class PBRRequest(StrictModel):
    """Represent a plant breeders request"""

    number: str = Field(..., description="Number of the request")
    entry_date: Optional[ISODate] = Field(default=None, alias="entryDate", description="Entry date of the request")


class PBRRegister(StrictModel):
    """Represent a plant breeders register"""

    number: str = Field(..., description="Number of the register")
    grant_of_protection: ISODate = Field(alias="grantOfProtection", description="Grant of protection date")
    max_protection_years: int = Field(alias="maxProtectionYears", description="Max protection years")
    end_protection: Optional[ISODate] = Field(
        default=None, alias="endOfProtection", description="End of protection date"
    )


class PBRContact(StrictModel):
    """Represent a plant breeders contact"""

    agent: Contact = Field(..., description="Plant breeders contact")


class PlantBreedersRight(StrictModel):
    """Represent a plant breeders right"""

    status: str = Field(..., description="Plant breeders status")
    request: PBRRequest = Field(..., description="Plant breeders request")
    register_info: Optional[PBRRegister] = Field(default=None, alias="register", description="Plant breeders register")
    contact: PBRContact = Field(alias="contacts", description="plant breeders contact")


class VarietyContacts(StrictModel):
    """Represent the contacts of the plant variety"""

    owners: list[Contact] = Field(..., description="Owners contacts")
    breeders: list[Contact] = Field(..., description="Breeders contacts")


class Variety(StrictModel):
    """Represent a plant variety."""

    id: str = Field(..., description="Unique identifier of the variety. Represented by a UUID")
    status: str = Field(alias="dossierStatus", description="Variety status")
    breeding_country: Optional[str] = Field(
        default=None, alias="breedingCountry", description="Breeding country of the variety"
    )
    trade_names: Optional[list[str]] = Field(default=None, alias="tradeNames", description="Trade names of the variety")
    brand_names: Optional[list[str]] = Field(default=None, alias="brandNames", description="Brand names of the variety")
    breeders_reference: Optional[str] = Field(
        default=None, alias="breedersReference", description="Breeders reference of the variety"
    )
    crop_category: CropCategory = Field(alias="cropCategory", description="Crop category of the variety")
    botanical_info: BotanicalInfo = Field(
        alias="botanicalInformation", description="Botanical information of the variety"
    )
    current_denomination: Optional[CurrentDenomination] = Field(
        default=None,
        alias="currentlyRelevantDenomination",
        description="Currently accepted denomination of the variety",
    )
    denominations: Optional[list[Denomination]] = Field(default=None, description="Denomination history of the variety")
    plant_breeders_right: PlantBreedersRight = Field(
        alias="plantBreedersRight", description="Plant breeders right of the variety"
    )
    contacts: VarietyContacts = Field(..., description="Contacts of the variety")


class Varieties(StrictModel):
    """Represent the raw data model for plant varieties."""

    varieties: list[Variety] = Field(..., description="List of varieties")

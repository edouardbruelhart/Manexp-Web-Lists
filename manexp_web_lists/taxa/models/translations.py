from enum import Enum

from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import BeforeValidatorFunctionSchema

from manexp_web_lists.core.strict_model import StrictModel


class TranslationSource(str, Enum):
    """Define where the translation comes from."""

    WIKIDATA = "wikidata"
    GBIF = "gbif"
    GOOGLE = "google"

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type["TranslationSource"],
        _: type,
        handler: GetCoreSchemaHandler,
    ) -> BeforeValidatorFunctionSchema:
        return core_schema.no_info_before_validator_function(
            cls._parse,
            handler(cls),
        )

    @classmethod
    def _parse(cls: type["TranslationSource"], value: str) -> str:
        """
        Parse the translation source.

        Args:
            value: The translation source to parse

        Returns:
            str: The parsed translation source
        """

        if isinstance(value, cls):
            return value
        else:
            return cls(value)


class Translation(StrictModel):
    """Represent a translation"""

    name: str = Field(..., description="The translation")
    source: TranslationSource = Field(..., description="The source of the translation")


class Translations(StrictModel):
    """Represent the translations model for a taxon"""

    fr: Translation = Field(..., description="French translation")
    en: Translation = Field(..., description="English translation")
    de: Translation = Field(..., description="German translation")
    it: Translation = Field(..., description="Italian translation")

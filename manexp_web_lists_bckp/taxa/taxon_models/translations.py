from enum import StrEnum

from manexp_web_lists.utils.strict_model import StrictModel
from pydantic import Field, field_validator


class TranslationSource(StrEnum):
    """Defines where the translation comes from."""

    WIKIDATA = "wikidata"
    GBIF = "gbif"
    GOOGLE = "google"


class Translation(StrictModel):
    """
    Represents a translation
    """

    name: str = Field(description="The translation")
    source: TranslationSource = Field(description="The source of the translation")

    @field_validator("source", mode="before")
    @classmethod
    def parse_translation_source(cls: type["Translation"], source: str | TranslationSource) -> TranslationSource:
        """
        Parse the source of the translation.

        Args:
            cls (type["Translation"]): Translation class
            source (str | TranslationSource): TranslationSource source

        Returns:
            TranslationSource: TranslationSource value
        """

        if isinstance(source, str):
            return TranslationSource(source)
        return source


class Translations(StrictModel):
    """
    Represents the translations model for a taxon

    Attributes:
        fr (Translation): French translation
        en (Translation): English translation
        de (Translation): German translation
        it (Translation): Italian translation

    """

    fr: Translation
    en: Translation
    de: Translation
    it: Translation

"""Tests for taxa/models/translations.py"""

import pytest
from pydantic import ValidationError

from manexp_web_lists.core.strict_model import StrictModel
from manexp_web_lists.taxa.models.translations import Translation, Translations, TranslationSource


class SourceModel(StrictModel):
    source: TranslationSource


def test_translation_source_from_string():
    source = TranslationSource("wikidata")
    assert source is TranslationSource.WIKIDATA


def test_translation_source_from_enum():
    source = TranslationSource(TranslationSource.GBIF)
    assert source is TranslationSource.GBIF
    assert source.value == "gbif"


def test_translation_source_from_model():
    model = SourceModel(source=TranslationSource.WIKIDATA)

    assert model.source == TranslationSource.WIKIDATA


def test_translation_source_invalid_value():
    with pytest.raises(ValueError):
        TranslationSource("Invalid Source")


def test_translation_source_invalid_type():
    with pytest.raises(ValueError):
        TranslationSource(123)


def test_translation_valid():
    translation = Translation(name="Tomato", source="wikidata")

    assert translation.name == "Tomato"
    assert translation.source == TranslationSource.WIKIDATA


def test_translation_missing_field():
    with pytest.raises(ValueError):
        Translation(
            # Missing name
            source="wikidata"
        )


def test_translation_extra_field():
    with pytest.raises(ValidationError):
        Translation(name="Tomato", source="wikidata", extra="boom")


def test_translation_invalid_field():
    with pytest.raises(ValidationError):
        Translation(name="Tomato", source=45)


def test_translations_valid():
    translations = Translations(
        fr=Translation(name="Tomate", source="wikidata"),
        en=Translation(name="Tomato", source="gbif"),
        de=Translation(name="Tomate", source="wikidata"),
        it=Translation(name="Pomodoro", source="google"),
    )

    assert translations.fr.name == "Tomate"
    assert translations.en.source == TranslationSource.GBIF

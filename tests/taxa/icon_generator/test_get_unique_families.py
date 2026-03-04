"""Tests for taxa/icon_generator/get_unique_families.py"""

from manexp_web_lists.taxa.icon_generator.get_unique_families import get_unique_families
from manexp_web_lists.taxa.models.crops import Crop, Crops
from manexp_web_lists.taxa.models.taxa import TranslatedTaxa, TranslatedTaxon
from manexp_web_lists.taxa.models.taxonomy import CleanedClassification, CleanedTaxonomy, RawClassification
from manexp_web_lists.taxa.models.translations import Translation, Translations, TranslationSource

TRANSLATED_TAXON = TranslatedTaxon(
    crop_category="Vegetable Crops",
    taxonomy=CleanedTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum",
            focal_name="Solanum lycopersicum",
        ),
        cleaned_classification=CleanedClassification(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum",
            focal_name="Solanum lycopersicum",
        ),
    ),
    crops=Crops(
        crops=[
            Crop(
                id="123",
                status="Approved",
                upov_code="UPOV-001",
                denomination="Green Zebra Tomato",
            ),
            Crop(
                id="456",
                status="Approved",
                upov_code="UPOV-002",
                denomination="Cherry Tomato",
            ),
        ]
    ),
    translations=Translations(
        fr=Translation(name="Tomate", source=TranslationSource.GBIF),
        en=Translation(name="Tomato", source=TranslationSource.GBIF),
        de=Translation(name="Tomate", source=TranslationSource.GBIF),
        it=Translation(name="Pomodoro", source=TranslationSource.GBIF),
    ),
)


def test_get_unique_families_single():
    translated_taxa = TranslatedTaxa(taxa=[TRANSLATED_TAXON])

    result = get_unique_families(translated_taxa)

    assert result == ["Solanaceae"]


def test_get_unique_families_copy():
    translated_taxa = TranslatedTaxa(taxa=[TRANSLATED_TAXON, TRANSLATED_TAXON])

    result = get_unique_families(translated_taxa)

    assert result == ["Solanaceae"]

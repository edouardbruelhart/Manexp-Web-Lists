"""Tests for taxa/color_generator/color_generator.py"""

from unittest.mock import patch

from manexp_web_lists.taxa.color_generator.color_generator import color_generator
from manexp_web_lists.taxa.models.crops import Crop, Crops
from manexp_web_lists.taxa.models.taxa import Icon, IconedTaxa, IconedTaxon
from manexp_web_lists.taxa.models.taxonomy import CleanedClassification, CleanedTaxonomy, RawClassification
from manexp_web_lists.taxa.models.translations import Translation, Translations, TranslationSource

ICONED_TAXON = IconedTaxon(
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
    icon=Icon.VEGETABLES,
)


def test_color_generator():
    taxa = IconedTaxa(taxa=[ICONED_TAXON])

    with patch("manexp_web_lists.taxa.color_generator.color_generator.save_taxa") as mock_save:
        result = color_generator(taxa)

        assert result.taxa[0].color == "#5bcc32"
        mock_save.assert_called_once()

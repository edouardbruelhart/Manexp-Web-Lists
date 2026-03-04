"""Tests for taxa/taxo_translator/taxo_translator.py"""

from unittest.mock import patch

from manexp_web_lists.taxa.models.crops import Crop, Crops
from manexp_web_lists.taxa.models.taxa import CleanedTaxa, CleanedTaxon
from manexp_web_lists.taxa.models.taxonomy import CleanedClassification, CleanedTaxonomy, RawClassification
from manexp_web_lists.taxa.models.translations import Translation, Translations, TranslationSource
from manexp_web_lists.taxa.taxo_translator.taxo_translator import taxo_translator

CLEANED_TAXON = CleanedTaxon(
    crop_category="Vegetable Crops",
    taxonomy=CleanedTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Tomato",
            genus="Garden Tomato",
            species="Edible Tomato",
            focal_name="Edible Tomato",
        ),
        cleaned_classification=CleanedClassification(
            family="Tomato",
            genus="Garden Tomato",
            species="Edible Tomato",
            focal_name="Edible Tomato",
        ),
    ),
    crops=Crops(
        crops=[
            Crop(
                id="123",
                status="Approved",
                upov_code="UPOV-001",
                denomination="Golden Apple",
            ),
            Crop(
                id="456",
                status="Approved",
                upov_code="UPOV-002",
                denomination="Cherry Tomato",
            ),
        ]
    ),
)


def test_taxo_translator_success():
    with (
        patch("manexp_web_lists.taxa.taxo_translator.taxo_translator.translate_taxon") as mock_translate,
        patch("manexp_web_lists.taxa.taxo_translator.taxo_translator.save_taxa") as mock_save,
    ):
        mock_translate.return_value = Translations(
            fr=Translation(name="Être humain", source=TranslationSource.GBIF),
            en=Translation(name="Human being", source=TranslationSource.GBIF),
            de=Translation(name="Mensch", source=TranslationSource.GBIF),
            it=Translation(name="Uomo umano", source=TranslationSource.GBIF),
        )

        cleaned_taxa = CleanedTaxa(taxa=[CLEANED_TAXON])

        result = taxo_translator(cleaned_taxa)

    assert result.taxa[0].translations.fr.name == "Être humain"
    assert result.taxa[0].translations.en.name == "Human being"
    mock_save.assert_called_once()


def test_taxo_translator_failure():
    with (
        patch("manexp_web_lists.taxa.taxo_translator.taxo_translator.translate_taxon") as mock_translate,
        patch("manexp_web_lists.taxa.taxo_translator.taxo_translator.save_taxa") as mock_save,
    ):
        mock_translate.return_value = None

        cleaned_taxa = CleanedTaxa(taxa=[CLEANED_TAXON])

        result = taxo_translator(cleaned_taxa)

    assert result.taxa == []
    mock_save.assert_called_once()

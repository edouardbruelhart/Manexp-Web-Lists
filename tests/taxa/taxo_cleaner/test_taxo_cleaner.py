"""Tests for taxa/taxo_cleaner/taxo_cleaner.py"""

from pathlib import Path
from unittest.mock import patch

import pytest

from manexp_web_lists.exceptions.crop_category_mismatch import CropCategoryMismatchError
from manexp_web_lists.taxa.models.crops import Crop, Crops
from manexp_web_lists.taxa.models.taxa import RawTaxa, RawTaxon
from manexp_web_lists.taxa.models.taxonomy import RawClassification, RawTaxonomy
from manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy import CleaningReport
from manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner import taxo_cleaner

RAW_TAXON = RawTaxon(
    crop_category="Vegetable Crops",
    taxonomy=RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
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


def test_taxo_cleaner_single_taxon():
    with (
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.clean_taxonomy") as mock_clean,
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.save_taxa") as mock_save,
    ):
        mock_clean.return_value = CleaningReport(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum",
        )

        input_taxa = RawTaxa(taxa=[RAW_TAXON])

        result = taxo_cleaner(input_taxa)

    assert len(result.taxa) == 1
    cleaned = result.taxa[0]

    assert cleaned.taxonomy.cleaned_classification.species == "Solanum lycopersicum"
    assert cleaned.crop_category == RAW_TAXON.crop_category
    mock_save.assert_called_once()


def test_taxo_cleaner_ignores_failed_cleaning():
    with (
        patch(
            "manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.clean_taxonomy",
            return_value=None,
        ),
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.save_taxa"),
    ):
        result = taxo_cleaner(RawTaxa(taxa=[RAW_TAXON]))

    assert result.taxa == []


def test_taxo_cleaner_merges_crops():
    taxon2 = RawTaxon(
        crop_category="Vegetable Crops",
        taxonomy=RawTaxonomy(
            rank="species",
            raw_classification=RawClassification(
                family="Tomato",
                genus="Garden Tomato",
                species="Edible Tomato",
                focal_name="Edible Tomato",
            ),
        ),
        crops=Crops(
            crops=[
                Crop(
                    id="789",
                    status="Approved",
                    upov_code="UPOV-001",
                    denomination="Golden Apple",
                )
            ]
        ),
    )

    with (
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.clean_taxonomy") as mock_clean,
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.save_taxa"),
    ):
        mock_clean.return_value = CleaningReport(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum",
        )

        result = taxo_cleaner(RawTaxa(taxa=[RAW_TAXON, taxon2]))

    assert len(result.taxa) == 1


def test_taxo_cleaner_crop_category_mismatch():
    taxon2 = RawTaxon(
        crop_category="Fruit and berries",
        taxonomy=RawTaxonomy(
            rank="species",
            raw_classification=RawClassification(
                family="Tomato",
                genus="Garden Tomato",
                species="Edible Tomato",
                focal_name="Edible Tomato",
            ),
        ),
        crops=Crops(
            crops=[
                Crop(
                    id="789",
                    status="Approved",
                    upov_code="UPOV-001",
                    denomination="Golden Apple",
                )
            ]
        ),
    )

    with (
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.clean_taxonomy") as mock_clean,
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.save_taxa"),
    ):
        mock_clean.return_value = CleaningReport(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum",
        )

        with pytest.raises(CropCategoryMismatchError):
            taxo_cleaner(RawTaxa(taxa=[RAW_TAXON, taxon2]))


def test_taxo_cleaner_saves_to_expected_path():
    with (
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.clean_taxonomy") as mock_clean,
        patch("manexp_web_lists.taxa.taxo_cleaner.taxo_cleaner.save_taxa") as mock_save,
    ):
        mock_clean.return_value = CleaningReport(
            family="Solanaceae",
            genus="Solanum",
            species=None,
        )

        taxo_cleaner(RawTaxa(taxa=[RAW_TAXON]))

    args, _ = mock_save.call_args
    assert args[1] == Path("../lists/in/cleaned/cleaned_taxon_list.json")

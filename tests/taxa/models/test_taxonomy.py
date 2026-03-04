"""Tests for taxa/models/taxonomy.py"""

from manexp_web_lists.taxa.models.taxonomy import (
    CleanedClassification,
    CleanedTaxonomy,
    RawClassification,
    RawTaxonomy,
    TaxonRank,
)


def test_taxon_rank_from_string():
    rank = TaxonRank("species")
    assert rank is TaxonRank.SPECIES


def test_taxon_rank_from_enum():
    rank = TaxonRank(TaxonRank.GENUS)
    assert rank is TaxonRank.GENUS
    assert rank.value == "genus"


def test_raw_taxonomy():
    raw_taxonomy = RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Tomato",
            # Missing genus
            species="Edible Tomato",
            focal_name="Edible Tomato",
        ),
    )

    assert raw_taxonomy.rank == TaxonRank.SPECIES
    assert raw_taxonomy.raw_classification.family == "Tomato"


def test_cleaned_taxonomy():
    cleaned_taxonomy = CleanedTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Tomato",
            # Missing genus field
            species="Edible Tomato",
            focal_name="Edible Tomato",
        ),
        cleaned_classification=CleanedClassification(
            family="Tomato", genus="Garden Tomato", species="Edible Tomato", focal_name="Edible Tomato"
        ),
    )

    assert cleaned_taxonomy.raw_classification.genus is None
    assert cleaned_taxonomy.cleaned_classification.genus == "Garden Tomato"

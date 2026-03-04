"""Tests for taxa/models/taxa.py"""

from manexp_web_lists.core.strict_model import StrictModel
from manexp_web_lists.taxa.models.crops import Crop, Crops
from manexp_web_lists.taxa.models.taxa import ColoredTaxa, ColoredTaxon, Icon
from manexp_web_lists.taxa.models.taxonomy import (
    CleanedClassification,
    CleanedTaxonomy,
    RawClassification,
)
from manexp_web_lists.taxa.models.translations import Translation, Translations


class IconModel(StrictModel):
    icon: Icon


def test_icon_from_string():
    icon = Icon("wheat")
    assert icon is Icon.CEREALS


def test_icon_from_enum():
    icon = Icon(Icon.ORNAMENTAL)
    assert icon is Icon.ORNAMENTAL
    assert icon.value == "deceased"


def test_icon_from_model():
    model = IconModel(icon="wheat")
    assert model.icon == Icon.CEREALS


def test_colored_taxon():
    colored_taxon = ColoredTaxon(
        crop_category="Fruit and berries",
        taxonomy=CleanedTaxonomy(
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
        translations=Translations(
            fr=Translation(name="Tomate", source="wikidata"),
            en=Translation(name="Tomato", source="gbif"),
            de=Translation(name="Tomate", source="wikidata"),
            it=Translation(name="Pomodoro", source="google"),
        ),
        icon=Icon.CEREALS,
        color="#000000",
    )

    assert colored_taxon.translations.fr.name == "Tomate"
    assert colored_taxon.icon == Icon.CEREALS


def test_colored_taxa():
    colored_taxa = ColoredTaxa(
        taxa=[
            ColoredTaxon(
                crop_category="Fruit and berries",
                taxonomy=CleanedTaxonomy(
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
                translations=Translations(
                    fr=Translation(name="Tomate", source="wikidata"),
                    en=Translation(name="Tomato", source="gbif"),
                    de=Translation(name="Tomate", source="wikidata"),
                    it=Translation(name="Pomodoro", source="google"),
                ),
                icon=Icon.CEREALS,
                color="#000000",
            )
        ]
    )

    assert len(colored_taxa.taxa) == 1
    assert colored_taxa.taxa[0].taxonomy.cleaned_classification.family == "Tomato"

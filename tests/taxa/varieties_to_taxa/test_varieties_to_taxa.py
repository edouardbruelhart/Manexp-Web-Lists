"""Tests for taxa/varieties_to_taxa/varieties_to_taxa.py"""

from unittest.mock import patch

from manexp_web_lists.taxa.models.crops import CropCategory
from manexp_web_lists.taxa.models.taxa import RawTaxa
from manexp_web_lists.taxa.models.varieties import (
    BotanicalInfo,
    Contact,
    PBRContact,
    PBRRequest,
    PlantBreedersRight,
    Varieties,
    Variety,
    VarietyContacts,
)
from manexp_web_lists.taxa.varieties_to_taxa.varieties_to_taxa import varieties_to_taxa


def test_varieties_to_taxa_basic():
    # Build minimal Variety
    variety = Variety(
        id="var1",
        status="Approved",
        crop_category=CropCategory.VEGETABLE,
        botanical_info=BotanicalInfo(
            family="Solanaceae",
            genus="Solanum",
            species="lycopersicum",
            upov_code="123",
        ),
        current_denomination={
            "denomination": "Vitalion",
            "status": "Approved",
            "validFrom": "2023-04-13",
        },
        plant_breeders_right=PlantBreedersRight(
            status="Approved",
            request=PBRRequest(number="10"),
            contact=PBRContact(agent=Contact(name="Test company", address="Test address", country="Test country")),
        ),
        contacts=VarietyContacts(
            owners=[Contact(name="Test owner", address="Test address", country="Test country")],
            breeders=[Contact(name="Test breeder", address="Test address", country="Test country")],
        ),
    )

    varieties = Varieties(varieties=[variety])

    # Patch save_taxa to avoid filesystem writes
    with patch("manexp_web_lists.taxa.varieties_to_taxa.varieties_to_taxa.save_taxa") as mock_save:
        # Call the function
        raw_taxa = varieties_to_taxa(varieties)

        taxon = raw_taxa.taxa[0]

        assert isinstance(raw_taxa, RawTaxa)
        assert len(raw_taxa.taxa) == 1
        assert taxon.taxonomy.raw_classification.family == "Solanaceae"
        assert taxon.taxonomy.raw_classification.genus == "Solanum"
        assert taxon.taxonomy.raw_classification.species == "lycopersicum"
        assert taxon.crops.crops[0].denomination == "Vitalion"
        mock_save.assert_called_once()


def test_varieties_to_taxa_groups_crops():
    # Two varieties in same taxonomy
    var1 = Variety(
        id="var1",
        status="Approved",
        crop_category=CropCategory.VEGETABLE,
        botanical_info=BotanicalInfo(
            family="Solanaceae",
            genus="Solanum",
            species="lycopersicum",
            upov_code="123",
        ),
        current_denomination={
            "denomination": "Vitalion",
            "status": "Approved",
            "validFrom": "2023-04-13",
        },
        plant_breeders_right=PlantBreedersRight(
            status="Approved",
            request=PBRRequest(number="10"),
            contact=PBRContact(agent=Contact(name="Test company", address="Test address", country="Test country")),
        ),
        contacts=VarietyContacts(
            owners=[Contact(name="Test owner", address="Test address", country="Test country")],
            breeders=[Contact(name="Test breeder", address="Test address", country="Test country")],
        ),
    )

    var2 = Variety(
        id="var2",
        status="Approved",
        crop_category=CropCategory.VEGETABLE,
        botanical_info=BotanicalInfo(
            family="Solanaceae",
            genus="Solanum",
            species="lycopersicum",
            upov_code="456",
        ),
        current_denomination={
            "denomination": "Vitatigre",
            "status": "Approved",
            "validFrom": "2023-04-13",
        },
        plant_breeders_right=PlantBreedersRight(
            status="Approved",
            request=PBRRequest(number="10"),
            contact=PBRContact(agent=Contact(name="Test company", address="Test address", country="Test country")),
        ),
        contacts=VarietyContacts(
            owners=[Contact(name="Test owner", address="Test address", country="Test country")],
            breeders=[Contact(name="Test breeder", address="Test address", country="Test country")],
        ),
    )

    varieties = Varieties(varieties=[var1, var2])

    with patch("manexp_web_lists.taxa.varieties_to_taxa.varieties_to_taxa.save_taxa") as mock_save:
        raw_taxa = varieties_to_taxa(varieties)

        assert len(raw_taxa.taxa) == 1
        crops = raw_taxa.taxa[0].crops.crops
        assert len(crops) == 2
        names = [c.denomination for c in crops]
        assert "Vitalion" in names and "Vitatigre" in names
        mock_save.assert_called_once()


def test_varieties_to_taxa_no_focal_name():
    # Build minimal Variety
    variety = Variety(
        id="var1",
        status="Approved",
        crop_category=CropCategory.VEGETABLE,
        botanical_info=BotanicalInfo(
            family="Solanaceae",
            genus=None,
            species=None,
            upov_code="123",
        ),
        current_denomination={
            "denomination": "Vitalion",
            "status": "Approved",
            "validFrom": "2023-04-13",
        },
        plant_breeders_right=PlantBreedersRight(
            status="Approved",
            request=PBRRequest(number="10"),
            contact=PBRContact(agent=Contact(name="Test company", address="Test address", country="Test country")),
        ),
        contacts=VarietyContacts(
            owners=[Contact(name="Test owner", address="Test address", country="Test country")],
            breeders=[Contact(name="Test breeder", address="Test address", country="Test country")],
        ),
    )

    varieties = Varieties(varieties=[variety])

    # Patch save_taxa to avoid filesystem writes
    with patch("manexp_web_lists.taxa.varieties_to_taxa.varieties_to_taxa.save_taxa") as mock_save:
        # Call the function
        raw_taxa = varieties_to_taxa(varieties)

        assert len(raw_taxa.taxa) == 0
        mock_save.assert_called_once()


def test_varieties_to_taxa_no_denomination():
    # Build minimal Variety
    variety = Variety(
        id="var1",
        status="Approved",
        crop_category=CropCategory.VEGETABLE,
        botanical_info=BotanicalInfo(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum",
            upov_code="123",
        ),
        current_denomination=None,
        plant_breeders_right=PlantBreedersRight(
            status="Approved",
            request=PBRRequest(number="10"),
            contact=PBRContact(agent=Contact(name="Test company", address="Test address", country="Test country")),
        ),
        contacts=VarietyContacts(
            owners=[Contact(name="Test owner", address="Test address", country="Test country")],
            breeders=[Contact(name="Test breeder", address="Test address", country="Test country")],
        ),
    )

    varieties = Varieties(varieties=[variety])

    # Patch save_taxa to avoid filesystem writes
    with patch("manexp_web_lists.taxa.varieties_to_taxa.varieties_to_taxa.save_taxa") as mock_save:
        # Call the function
        raw_taxa = varieties_to_taxa(varieties)

        assert len(raw_taxa.taxa) == 0
        mock_save.assert_called_once()

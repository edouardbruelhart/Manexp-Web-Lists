"""Tests for taxa/taxo_cleaner/clean_taxonomy.py"""

from unittest.mock import patch

from manexp_web_lists.taxa.models.taxonomy import RawClassification, RawTaxonomy
from manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy import clean_name, clean_taxonomy


def test_clean_name_success():
    with patch("manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.gbif_parser_request") as mock_response:
        mock_response.return_value = {"canonicalName": "Solanum lycopersicum"}

        result = clean_name("Solanum lycopersicum L.")

    assert result == "Solanum lycopersicum"


def test_clean_name_null():
    with patch("manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.gbif_parser_request") as mock_response:
        mock_response.return_value = None

        result = clean_name(None)

    assert result is None


def test_clean_name_parser_failure():
    with patch("manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.gbif_parser_request") as mock_response:
        mock_response.return_value = None

        result = clean_name("Invalid name")

    assert result is None


def test_clean_name_no_canonical():
    with patch("manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.gbif_parser_request") as mock_response:
        mock_response.return_value = {}

        result = clean_name("Something")

    assert result is None


def test_clean_taxonomy_success():
    raw_taxonomy = RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum",
            focal_name="Solanum lycopersicum",
        ),
    )

    def fake_clean_name(value):
        return {
            "Solanum lycopersicum": "Solanum lycopersicum",
            "Solanum": "Solanum",
            "Solanaceae": "Solanaceae",
        }.get(value)

    with patch(
        "manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.clean_name",
        side_effect=fake_clean_name,
    ):
        result = clean_taxonomy(raw_taxonomy)

    assert result.species == "Solanum lycopersicum"
    assert result.genus == "Solanum"
    assert result.family == "Solanaceae"


def test_clean_taxonomy_missing_species_and_genus(caplog):
    taxonomy = RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            focal_name="Unknown",
            species=None,
            genus=None,
            family=None,
        ),
    )

    result = clean_taxonomy(taxonomy)

    assert result is None
    assert "Missing species and genus" in caplog.text


def test_clean_taxonomy_cropped_species_success():
    raw_taxonomy = RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicum x Solanum tuberosum",
            focal_name="Solanum lycopersicum x Solanum tuberosum",
        ),
    )

    def fake_clean_name(value):
        return {
            "Solanum lycopersicum x Solanum tuberosum": None,
            "Solanum lycopersicum": "Solanum lycopersicum",
            "Solanum": "Solanum",
            "Solanaceae": "Solanaceae",
        }.get(value)

    with patch(
        "manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.clean_name",
        side_effect=fake_clean_name,
    ):
        result = clean_taxonomy(raw_taxonomy)

    assert result.species == "Solanum lycopersicum"
    assert result.genus == "Solanum"
    assert result.family == "Solanaceae"


def test_clean_taxonomy_cropped_species_error(caplog):
    raw_taxonomy = RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Solanaceae",
            genus="Solanum",
            species="Solanum lycopersicu",
            focal_name="Solanum lycopersicu",
        ),
    )

    def fake_clean_name(value):
        return {
            "Solanum lycopersicu": None,
            "Solanum": "Solanum",
            "Solanaceae": "Solanaceae",
        }.get(value)

    with patch(
        "manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.clean_name",
        side_effect=fake_clean_name,
    ):
        result = clean_taxonomy(raw_taxonomy)

    assert result.species is None
    assert "Parsing also failed with cropped species" in caplog.text


def test_clean_taxonomy_cropped_genus_success():
    raw_taxonomy = RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Solanaceae",
            genus="Solanum x Fragaria",
            species="Solanum lycopersicum",
            focal_name="Solanum lycopersicum",
        ),
    )

    def fake_clean_name(value):
        return {
            "Solanum lycopersicum": "Solanum lycopersicum",
            "Solanum x Fragaria": None,
            "Solanum": "Solanum",
            "Solanaceae": "Solanaceae",
        }.get(value)

    with patch(
        "manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.clean_name",
        side_effect=fake_clean_name,
    ):
        result = clean_taxonomy(raw_taxonomy)

    assert result.species == "Solanum lycopersicum"
    assert result.genus == "Solanum"
    assert result.family == "Solanaceae"


def test_clean_taxonomy_cropped_genus_error(caplog):
    raw_taxonomy = RawTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Solanaceae",
            genus="Solanu",
            species="Solanum lycopersicum",
            focal_name="Solanum lycopersicum",
        ),
    )

    def fake_clean_name(value):
        return {
            "Solanum lycopersicum": "Solanum lycopersicum",
            "Solanu": None,
            "Solanaceae": "Solanaceae",
        }.get(value)

    with patch(
        "manexp_web_lists.taxa.taxo_cleaner.clean_taxonomy.clean_name",
        side_effect=fake_clean_name,
    ):
        result = clean_taxonomy(raw_taxonomy)

    assert result is None
    assert "Parsing also failed with cropped genus" in caplog.text

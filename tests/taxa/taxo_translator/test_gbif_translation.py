"""Tests for taxa/taxo_translator/gbif_translation.py"""

from unittest.mock import MagicMock, patch

from manexp_web_lists.requests.gbif_requests import GBIFMatchResult, MatchStatus
from manexp_web_lists.taxa.models.taxonomy import CleanedClassification, CleanedTaxonomy, RawClassification, TaxonRank
from manexp_web_lists.taxa.models.translations import Translation, TranslationSource
from manexp_web_lists.taxa.taxo_translator.gbif_translation import (
    gbif_translation,
    get_gbif_key,
    is_valid_candidate,
    translation_report_from_vernaculars,
)
from manexp_web_lists.taxa.taxo_translator.models import TranslationReport


def test_gbif_translation_success():
    taxonomy = MagicMock()

    translation_report = TranslationReport(
        fr=None,
        en=None,
        de=None,
        it=None,
    )

    with (
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.get_gbif_key") as mock_key,
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_vernaculars_request") as mock_vernaculars,
        patch(
            "manexp_web_lists.taxa.taxo_translator.gbif_translation.translation_report_from_vernaculars"
        ) as mock_report,
    ):
        mock_key.return_value = "1234"

        mock_vernaculars.return_value = [
            {"vernacularName": "Être humain", "language": "fra"},
            {"vernacularName": "Human being", "language": "eng"},
            {"vernacularName": "Mensch", "language": "deu"},
            {"vernacularName": "Uomo umano", "language": "ita"},
        ]

        expected_report = TranslationReport(
            fr=Translation(name="Être humain", source=TranslationSource.GBIF),
            en=Translation(name="Human being", source=TranslationSource.GBIF),
            de=Translation(name="Mensch", source=TranslationSource.GBIF),
            it=Translation(name="Uomo umano", source=TranslationSource.GBIF),
        )

        mock_report.return_value = expected_report

        result = gbif_translation(taxonomy, translation_report)

        assert result == expected_report


def test_gbif_translation_no_key():
    taxonomy = MagicMock()

    translation_report = TranslationReport(
        fr=None,
        en=None,
        de=None,
        it=None,
    )

    with patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.get_gbif_key") as mock_key:
        mock_key.return_value = None

        result = gbif_translation(taxonomy, translation_report)

        assert result == translation_report


def test_gbif_translation_no_vernaculars():
    taxonomy = MagicMock()

    translation_report = TranslationReport(
        fr=None,
        en=None,
        de=None,
        it=None,
    )

    with (
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.get_gbif_key") as mock_key,
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_vernaculars_request") as mock_vernaculars,
    ):
        mock_key.return_value = "1234"

        mock_vernaculars.return_value = None

        result = gbif_translation(taxonomy, translation_report)

        assert result == translation_report


def test_get_gbif_key_success_match():
    taxonomy = CleanedTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
        cleaned_classification=CleanedClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
    )

    with patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_match_request") as mock_match:
        mock_match.return_value = GBIFMatchResult(
            status=MatchStatus.OK,
            data={
                "usage": {
                    "key": "2930137",
                    "name": "Solanum lycopersicum L.",
                    "canonicalName": "Solanum lycopersicum",
                    "authorship": "L.",
                    "rank": "SPECIES",
                    "status": "ACCEPTED",
                    "genericName": "Solanum",
                    "specificEpithet": "lycopersicum",
                    "type": "SCIENTIFIC",
                    "formattedName": "<i>Solanum</i> <i>lycopersicum</i> L.",
                },
                "classification": [
                    {"key": "6", "name": "Plantae", "rank": "KINGDOM"},
                    {"key": "7707728", "name": "Tracheophyta", "rank": "PHYLUM"},
                    {"key": "220", "name": "Magnoliopsida", "rank": "CLASS"},
                    {"key": "1176", "name": "Solanales", "rank": "ORDER"},
                    {"key": "7717", "name": "Solanaceae", "rank": "FAMILY"},
                    {"key": "2928997", "name": "Solanum", "rank": "GENUS"},
                    {"key": "2930137", "name": "Solanum lycopersicum", "rank": "SPECIES"},
                ],
                "diagnostics": {
                    "matchType": "EXACT",
                    "confidence": 98,
                    "timeTaken": 17,
                    "timings": {"nameNRank": 0, "sciNameMatch": 17, "nameParse": 1, "luceneMatch": 16},
                },
                "synonym": False,
                "left": 573188,
                "right": 573209,
            },
        )

        result = get_gbif_key(taxonomy)

        assert result == "2930137"


def test_get_gbif_key_success_search():
    taxonomy = CleanedTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
        cleaned_classification=CleanedClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
    )

    with (
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_match_request") as mock_match,
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_search_request") as mock_search,
    ):
        mock_match.return_value = GBIFMatchResult(status=MatchStatus.MULTIPLE, data=None)

        mock_search.return_value = [
            {
                "key": 100492266,
                "datasetKey": "16c3f9cb-4b19-4553-ac8e-ebb90003aa02",
                "nubKey": 2436436,
                "parentKey": 100492250,
                "parent": "Homo",
                "taxonomicStatus": "ACCEPTED",
                "kingdom": "Plantae",
                "family": "Hominidae",
                "genus": "Homo",
                "species": "Homo sapiens",
                "familyKey": 314627940,
                "genusKey": 100492250,
                "speciesKey": 100492266,
                "scientificName": "Homo sapiens",
                "canonicalName": "Homo sapiens",
                "nameType": "SCIENTIFIC",
                "rank": "SPECIES",
                "origin": "SOURCE",
                "numDescendants": 0,
                "numOccurrences": 0,
                "taxonID": "399351",
                "extinct": False,
                "habitats": [],
                "nomenclaturalStatus": [],
                "threatStatuses": [],
                "vernacularNames": [
                    {"vernacularName": "Cro-Magnon-Mensch", "language": "deu"},
                    {"vernacularName": "Mensch", "language": "deu"},
                ],
                "higherClassificationMap": {"314627940": "Hominidae", "100492250": "Homo"},
                "synonym": False,
            },
        ]

        result = get_gbif_key(taxonomy)

        assert result == "2436436"


def test_get_gbif_key_no_usage():
    taxonomy = CleanedTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
        cleaned_classification=CleanedClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
    )

    with patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_match_request") as mock_match:
        mock_match.return_value = GBIFMatchResult(
            status=MatchStatus.OK,
            data={
                "result": {
                    "key": "2930137",
                    "name": "Solanum lycopersicum L.",
                    "canonicalName": "Solanum lycopersicum",
                    "authorship": "L.",
                    "rank": "SPECIES",
                    "status": "ACCEPTED",
                    "genericName": "Solanum",
                    "specificEpithet": "lycopersicum",
                    "type": "SCIENTIFIC",
                    "formattedName": "<i>Solanum</i> <i>lycopersicum</i> L.",
                },
                "classification": [
                    {"key": "6", "name": "Plantae", "rank": "KINGDOM"},
                    {"key": "7707728", "name": "Tracheophyta", "rank": "PHYLUM"},
                    {"key": "220", "name": "Magnoliopsida", "rank": "CLASS"},
                    {"key": "1176", "name": "Solanales", "rank": "ORDER"},
                    {"key": "7717", "name": "Solanaceae", "rank": "FAMILY"},
                    {"key": "2928997", "name": "Solanum", "rank": "GENUS"},
                    {"key": "2930137", "name": "Solanum lycopersicum", "rank": "SPECIES"},
                ],
                "diagnostics": {
                    "matchType": "EXACT",
                    "confidence": 98,
                    "timeTaken": 17,
                    "timings": {"nameNRank": 0, "sciNameMatch": 17, "nameParse": 1, "luceneMatch": 16},
                },
                "synonym": False,
                "left": 573188,
                "right": 573209,
            },
        )

        result = get_gbif_key(taxonomy)

        assert result is None


def test_get_gbif_key_no_candidates():
    taxonomy = CleanedTaxonomy(
        rank="species",
        raw_classification=RawClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
        cleaned_classification=CleanedClassification(
            family="Hominidae",
            genus="Homo",
            species="Homo sapiens",
            focal_name="Homo sapiens",
        ),
    )

    with (
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_match_request") as mock_match,
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_search_request") as mock_search,
    ):
        mock_match.return_value = GBIFMatchResult(status=MatchStatus.MULTIPLE, data=None)

        mock_search.return_value = [
            {
                "key": 100492266,
                "datasetKey": "16c3f9cb-4b19-4553-ac8e-ebb90003aa02",
                "nubKey": 2436436,
                "parentKey": 100492250,
                "parent": "Homo",
                "taxonomicStatus": "ACCEPTED",
                "kingdom": "Plantae",
                "family": "Hominidae",
                "genus": "Homo",
                "species": "Homo neanderthalensis",
                "familyKey": 314627940,
                "genusKey": 100492250,
                "speciesKey": 100492266,
                "scientificName": "Homo sapiens",
                "canonicalName": "Homo sapiens",
                "nameType": "SCIENTIFIC",
                "rank": "SPECIES",
                "origin": "SOURCE",
                "numDescendants": 0,
                "numOccurrences": 0,
                "taxonID": "399351",
                "extinct": False,
                "habitats": [],
                "nomenclaturalStatus": [],
                "threatStatuses": [],
                "vernacularNames": [
                    {"vernacularName": "Cro-Magnon-Mensch", "language": "deu"},
                    {"vernacularName": "Mensch", "language": "deu"},
                ],
                "higherClassificationMap": {"314627940": "Hominidae", "100492250": "Homo"},
                "synonym": False,
            },
        ]

        result = get_gbif_key(taxonomy)

        assert result is None


def test_get_gbif_no_match():
    taxonomy = MagicMock()

    with patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_match_request") as mock_match:
        mock_match.return_value = GBIFMatchResult(status=MatchStatus.NONE, data=None)

        result = get_gbif_key(taxonomy)

        assert result is None


def test_get_gbif_key_no_candidate():
    taxonomy = MagicMock()

    with (
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_match_request") as mock_match,
        patch("manexp_web_lists.taxa.taxo_translator.gbif_translation.gbif_search_request") as mock_search,
    ):
        mock_match.return_value = GBIFMatchResult(status=MatchStatus.MULTIPLE, data=None)

        mock_search.return_value = []

        result = get_gbif_key(taxonomy)

        assert result is None


def test_translation_report_from_vernaculars_with_none():
    vernaculars = [
        {"vernacularName": "Être humain", "language": "fra"},
        {"vernacularName": "Human being", "language": "eng"},
        {"vernacularName": "Mensch", "language": "deu"},
        {"vernacularName": "Uomo umano", "language": "ita"},
    ]

    result = translation_report_from_vernaculars(vernaculars, None)

    assert result.fr.name == "Être humain"
    assert result.en.name == "Human being"
    assert result.de.name == "Mensch"
    assert result.it.name == "Uomo umano"


def test_translation_report_from_vernaculars_with_report():
    vernaculars = [
        {"vernacularName": "Être humain", "language": "fra"},
        {"vernacularName": "Human being", "language": "eng"},
        {"vernacularName": "Mensch", "language": "deu"},
        {"vernacularName": "Uomo umano", "language": "ita"},
    ]

    report = TranslationReport(
        fr=Translation(name="Humain", source=TranslationSource.WIKIDATA),
        en=None,
        de=None,
        it=None,
    )

    result = translation_report_from_vernaculars(vernaculars, report)

    assert result.fr.name == "Humain"
    assert result.fr.source == TranslationSource.WIKIDATA
    assert result.en.name == "Human being"
    assert result.de.name == "Mensch"
    assert result.it.name == "Uomo umano"


def test_is_valid_candidate_success_species():
    r = {
        "key": 100492266,
        "datasetKey": "16c3f9cb-4b19-4553-ac8e-ebb90003aa02",
        "nubKey": 2436436,
        "parentKey": 100492250,
        "parent": "Homo",
        "taxonomicStatus": "ACCEPTED",
        "kingdom": "Plantae",
        "family": "Hominidae",
        "genus": "Homo",
        "species": "Homo sapiens",
        "familyKey": 314627940,
        "genusKey": 100492250,
        "speciesKey": 100492266,
        "scientificName": "Homo sapiens",
        "canonicalName": "Homo sapiens",
        "nameType": "SCIENTIFIC",
        "rank": "SPECIES",
        "origin": "SOURCE",
        "numDescendants": 0,
        "numOccurrences": 0,
        "taxonID": "399351",
        "extinct": False,
        "habitats": [],
        "nomenclaturalStatus": [],
        "threatStatuses": [],
        "vernacularNames": [
            {"vernacularName": "Cro-Magnon-Mensch", "language": "deu"},
            {"vernacularName": "Mensch", "language": "deu"},
        ],
        "higherClassificationMap": {"314627940": "Hominidae", "100492250": "Homo"},
        "synonym": False,
    }

    rank = TaxonRank.SPECIES
    family = "Hominidae"
    genus = "Homo"
    species = "Homo sapiens"

    result = is_valid_candidate(r, rank=rank, family=family, genus=genus, species=species)

    assert result


def test_is_valid_candidate_success_genus():
    r = {
        "key": 100492266,
        "datasetKey": "16c3f9cb-4b19-4553-ac8e-ebb90003aa02",
        "nubKey": 2436436,
        "parentKey": 100492250,
        "parent": "Homo",
        "taxonomicStatus": "ACCEPTED",
        "kingdom": "Plantae",
        "family": "Hominidae",
        "genus": "Homo",
        "species": "Homo sapiens",
        "familyKey": 314627940,
        "genusKey": 100492250,
        "speciesKey": 100492266,
        "scientificName": "Homo sapiens",
        "canonicalName": "Homo sapiens",
        "nameType": "SCIENTIFIC",
        "rank": "GENUS",
        "origin": "SOURCE",
        "numDescendants": 0,
        "numOccurrences": 0,
        "taxonID": "399351",
        "extinct": False,
        "habitats": [],
        "nomenclaturalStatus": [],
        "threatStatuses": [],
        "vernacularNames": [
            {"vernacularName": "Cro-Magnon-Mensch", "language": "deu"},
            {"vernacularName": "Mensch", "language": "deu"},
        ],
        "higherClassificationMap": {"314627940": "Hominidae", "100492250": "Homo"},
        "synonym": False,
    }

    rank = TaxonRank.GENUS
    family = "Hominidae"
    genus = "Homo"
    species = None

    result = is_valid_candidate(r, rank=rank, family=family, genus=genus, species=species)

    assert result


def test_is_valid_candidate_bad_rank():
    r = {
        "key": 100492266,
        "datasetKey": "16c3f9cb-4b19-4553-ac8e-ebb90003aa02",
        "nubKey": 2436436,
        "parentKey": 100492250,
        "parent": "Homo",
        "taxonomicStatus": "ACCEPTED",
        "kingdom": "Plantae",
        "family": "Hominidae",
        "genus": "Homo",
        "species": "Homo sapiens",
        "familyKey": 314627940,
        "genusKey": 100492250,
        "speciesKey": 100492266,
        "scientificName": "Homo sapiens",
        "canonicalName": "Homo sapiens",
        "nameType": "SCIENTIFIC",
        "rank": "GENUS",
        "origin": "SOURCE",
        "numDescendants": 0,
        "numOccurrences": 0,
        "taxonID": "399351",
        "extinct": False,
        "habitats": [],
        "nomenclaturalStatus": [],
        "threatStatuses": [],
        "vernacularNames": [
            {"vernacularName": "Cro-Magnon-Mensch", "language": "deu"},
            {"vernacularName": "Mensch", "language": "deu"},
        ],
        "higherClassificationMap": {"314627940": "Hominidae", "100492250": "Homo"},
        "synonym": False,
    }

    rank = TaxonRank.SPECIES
    family = "Hominidae"
    genus = "Homo"
    species = "Homo sapiens"

    result = is_valid_candidate(r, rank=rank, family=family, genus=genus, species=species)

    assert not result

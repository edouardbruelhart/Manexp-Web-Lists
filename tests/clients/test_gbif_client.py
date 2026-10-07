import requests_mock

from manexp_web_lists.clients.gbif_client import TaxonRank, parse_with_gbif


def test_parse_with_gbif_successful_parsing():
    # Mock the response from GBIF API
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.gbif.org/v1/parser/name",
            json=[{"parsed": True, "canonicalName": "Taxon Name", "genusOrAbove": "Genus", "rankMarker": "sp."}],
        )

        # Call the function
        response = parse_with_gbif("Taxon Name")

    # Assert the expected result
    assert response == {"focal_name": "Taxon Name", "genus": "Genus", "rank": "SPECIES", "parsed": True}


def test_parse_with_gbif_no_data():
    # Mock the response from GBIF API
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.gbif.org/v1/parser/name",
            json=[],
        )

        # Call the function
        response = parse_with_gbif("Taxon Name")

    # Assert the expected result
    assert response == {"focal_name": "Taxon Name", "genus": None, "rank": "UNKNOWN", "parsed": False}


def test_parse_with_gbif_partial_parsing():
    # Mock the response from GBIF API
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.gbif.org/v1/parser/name",
            json=[{"parsed": True, "parsedPartially": True, "genusOrAbove": "Genus", "rankMarker": "gen."}],
        )

        # Call the function
        response = parse_with_gbif("Taxon Name")

    # Assert the expected result
    assert response == {"focal_name": "Taxon Name", "genus": "Genus", "rank": "GENUS", "parsed": False}


def test_parse_with_gbif_failed_parsing():
    # Mock the response from GBIF API
    with requests_mock.Mocker() as m:
        m.get("https://api.gbif.org/v1/parser/name", json=[{"parsed": False, "genusOrAbove": None, "rankMarker": None}])

        # Call the function
        response = parse_with_gbif("Taxon Name")

    # Assert the expected result
    assert response == {"focal_name": "Taxon Name", "genus": None, "rank": "UNKNOWN", "parsed": False}


def test_parse_with_gbif_no_name_provided():
    # Call the function with no name provided
    response = parse_with_gbif(None)

    # Assert the expected result
    assert response == {"focal_name": None, "genus": None, "rank": "UNKNOWN", "parsed": False}


def test_taxon_rank_enum_values():
    # Check that all expected values are present in the enum
    expected_values = {
        "cultivar group",
        "var.",
        "subsp.",
        "infrasp.",
        "morph",
        "sp.",
        "subgen.",
        "gen.",
        "sect.",
        "convar.",
        "subvar.",
        "unknown",
    }

    actual_values = {value.value for value in TaxonRank}

    assert expected_values == actual_values


def test_taxon_rank_enum_type():
    # Check that each enum value is of type str
    for rank in TaxonRank:
        assert isinstance(rank.value, str)

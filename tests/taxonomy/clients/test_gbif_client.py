import unittest

import requests_mock

from manexp_web_lists.taxonomy.clients.gbif_client import gbif_parser_request


class TestGBIFClient(unittest.TestCase):
    @requests_mock.mock()
    def test_successful_parsing(self, m):
        # Mock the response from GBIF API
        m.get(
            "https://api.gbif.org/v1/parser/name",
            json=[{"parsed": True, "canonicalName": "Taxon Name", "genusOrAbove": "Genus", "rankMarker": "sp."}],
        )

        # Call the function
        response = gbif_parser_request("Taxon Name")

        # Assert the expected result
        self.assertEqual(response, {"focal_name": "Taxon Name", "genus": "Genus", "rank": "SPECIES", "parsed": True})

    @requests_mock.mock()
    def test_no_data(self, m):
        # Mock the response from GBIF API
        m.get(
            "https://api.gbif.org/v1/parser/name",
            json=[],
        )

        # Call the function
        response = gbif_parser_request("Taxon Name")

        # Assert the expected result
        self.assertEqual(response, {"focal_name": "Taxon Name", "genus": None, "rank": "UNKNOWN", "parsed": False})

    @requests_mock.mock()
    def test_partial_parsing(self, m):
        # Mock the response from GBIF API
        m.get(
            "https://api.gbif.org/v1/parser/name",
            json=[{"parsed": True, "parsedPartially": True, "genusOrAbove": "Genus", "rankMarker": "gen."}],
        )

        # Call the function
        response = gbif_parser_request("Taxon Name")

        # Assert the expected result
        self.assertEqual(response, {"focal_name": "Taxon Name", "genus": "Genus", "rank": "GENUS", "parsed": False})

    @requests_mock.mock()
    def test_failed_parsing(self, m):
        # Mock the response from GBIF API
        m.get("https://api.gbif.org/v1/parser/name", json=[{"parsed": False, "genusOrAbove": None, "rankMarker": None}])

        # Call the function
        response = gbif_parser_request("Taxon Name")

        # Assert the expected result
        self.assertEqual(response, {"focal_name": "Taxon Name", "genus": None, "rank": "UNKNOWN", "parsed": False})

    @requests_mock.mock()
    def test_no_name_provided(self, m):
        # Call the function with no name provided
        response = gbif_parser_request(None)

        # Assert the expected result
        self.assertEqual(response, {"focal_name": None, "genus": None, "rank": "UNKNOWN", "parsed": False})


if __name__ == "__main__":
    unittest.main()

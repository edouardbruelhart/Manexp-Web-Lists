from unittest.mock import patch

import polars as pl
from polars.testing import assert_frame_equal

from manexp_web_lists.taxonomy.transform.clean_taxonomy import clean_taxonomy


def test_clean_taxonomy():

    taxonomy = pl.DataFrame({"botanical_name": "Taxon Name"})

    fake_response = {"focal_name": "Taxon Name", "genus": "Genus", "rank": "SPECIES", "parsed": True}

    with patch("manexp_web_lists.taxonomy.transform.clean_taxonomy.gbif_parser_request", return_value=fake_response):
        # Call the clean_taxonomy function
        cleaned_taxonomy = clean_taxonomy(taxonomy)

    # Assert the expected output
    expected_output = pl.DataFrame({
        "focal_name": "Taxon Name",
        "genus": "Genus",
        "rank": "SPECIES",
        "parsed": True,
    })

    assert_frame_equal(cleaned_taxonomy, expected_output)

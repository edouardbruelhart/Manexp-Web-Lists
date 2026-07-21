import unittest

from manexp_web_lists.taxonomy.models.taxon_rank import TaxonRank


class TestTaxonRank(unittest.TestCase):
    def test_enum_values(self):
        # Check that all expected values are present in the enum
        expected_values = {"cultivar group", "var.", "subsp.", "infrasp.", "morph", "sp.", "subgen.", "gen.", "unknown"}

        actual_values = {value.value for value in TaxonRank}

        self.assertEqual(expected_values, actual_values)

    def test_enum_type(self):
        # Check that each enum value is of type str
        for rank in TaxonRank:
            self.assertIsInstance(rank.value, str)


if __name__ == "__main__":
    unittest.main()

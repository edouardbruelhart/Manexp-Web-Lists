"""Tests for taxa/icon_generator/icon_generator.py"""

from unittest.mock import MagicMock, patch

import pytest

from manexp_web_lists.exceptions.families_error import FamiliesError
from manexp_web_lists.taxa.icon_generator.icon_generator import FAMILY_TO_ICON, icon_generator
from manexp_web_lists.taxa.models.taxa import Icon, TranslatedTaxa
from tests.taxa.icon_generator.test_get_unique_families import TRANSLATED_TAXON


def test_icon_generator_success():

    families = list(FAMILY_TO_ICON.keys())

    translated_taxa = TranslatedTaxa(taxa=[TRANSLATED_TAXON])

    with (
        patch(
            "manexp_web_lists.taxa.icon_generator.icon_generator.get_unique_families",
            return_value=families,
        ),
        patch("manexp_web_lists.taxa.icon_generator.icon_generator.save_taxa") as mock_save,
    ):
        result = icon_generator(translated_taxa)

        assert result.taxa[0].icon == Icon.VEGETABLES
        assert len(result.taxa) == len(translated_taxa.taxa)
        mock_save.assert_called_once()


def test_icon_generator_raises_families_error():

    translated_taxa = MagicMock()

    with (
        patch(
            "manexp_web_lists.taxa.icon_generator.icon_generator.get_unique_families",
            return_value=["TotallyFakeFamily"],
        ),
        pytest.raises(FamiliesError),
    ):
        icon_generator(translated_taxa)

from pathlib import Path

from manexp_web_lists.exceptions.families_exception import FamiliesException
from manexp_web_lists.taxa.icon_generator.models.families import FAMILY_TO_ICON
from manexp_web_lists.taxa.models.taxa import IconedTaxa, IconedTaxon, TranslatedTaxa
from manexp_web_lists.taxa.utils.save_taxa import save_taxa


def icon_generator(input_taxa: TranslatedTaxa) -> IconedTaxa:
    """Add material icons from google to taxa depending on their family"""

    # List to hold iconed taxa
    taxon_list: list[IconedTaxon] = []

    # Get updated families list
    families = get_unique_families(input_taxa)

    # Check that current families to icon mapping is matching new dataset families
    if len(families) != len(FAMILY_TO_ICON) or sorted(families) != sorted(FAMILY_TO_ICON):
        raise FamiliesException()

    # Put an icon to each taxon
    for taxon in input_taxa.taxa:
        # Get family
        family = taxon.taxonomy.resolved_classification.family

        # Get icon
        icon = FAMILY_TO_ICON[family]

        # Add iconed taxon to the list
        taxon_list.append(
            IconedTaxon(
                crop_category=taxon.crop_category,
                taxonomy=taxon.taxonomy,
                crops=taxon.crops,
                translations=taxon.translations,
                icon=icon,
            )
        )

    # Create iconed taxa
    iconed_taxa = IconedTaxa(taxa=taxon_list)

    # Save taxa to json file
    save_taxa(iconed_taxa, Path("../lists/in/iconed/iconed_taxon_list.json"))

    # Return iconed taxa
    return iconed_taxa


def get_unique_families(taxa: TranslatedTaxa) -> list[str]:
    unique_families: list[str] = []

    for taxon in taxa.taxa:
        family = taxon.taxonomy.resolved_classification.family
        if family not in unique_families:
            unique_families.append(family)

    return unique_families

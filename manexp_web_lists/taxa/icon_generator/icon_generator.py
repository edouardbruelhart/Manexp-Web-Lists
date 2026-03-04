import logging
from pathlib import Path

from manexp_web_lists.exceptions.families_error import FamiliesError
from manexp_web_lists.taxa.icon_generator.get_unique_families import get_unique_families
from manexp_web_lists.taxa.models.taxa import Icon, IconedTaxa, IconedTaxon, TranslatedTaxa
from manexp_web_lists.taxa.save_taxa import save_taxa

# Initialize logger
logger = logging.getLogger(__name__)


def icon_generator(input_taxa: TranslatedTaxa) -> IconedTaxa:
    """
    Add material icons from google to taxa depending on their family

    Args:
        input_taxa: The translated taxon list to iconize

    Returns:
        IconedTaxa: The iconed taxon list

    Raises:
        FamiliesError: If actual families to icon mapping is not matching new dataset families
    """

    # List to hold iconed taxa
    taxon_list: list[IconedTaxon] = []

    # Get updated families list
    families = get_unique_families(input_taxa)

    # Check that current families to icon mapping is matching new dataset families
    if sorted(families) != sorted(FAMILY_TO_ICON.keys()):
        raise FamiliesError()

    # Put an icon to each taxon
    for taxon in input_taxa.taxa:
        # Get family
        family = taxon.taxonomy.cleaned_classification.family

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

    logger.info(f"Done! added icon to {len(iconed_taxa.taxa)} taxa.")

    # Return iconed taxa
    return iconed_taxa


FAMILY_TO_ICON: dict[str, Icon] = {
    # Cereals
    "Poaceae": Icon.CEREALS,
    # Fruits
    "Rosaceae": Icon.FRUITS,
    "Grossulariaceae": Icon.FRUITS,
    "Actinidiaceae": Icon.FRUITS,
    "Vitaceae": Icon.FRUITS,
    "Moraceae": Icon.FRUITS,
    # Vegetables
    "Solanaceae": Icon.VEGETABLES,
    "Cucurbitaceae": Icon.VEGETABLES,
    "Brassicaceae": Icon.VEGETABLES,
    "Apiaceae": Icon.VEGETABLES,
    "Fabaceae": Icon.VEGETABLES,
    "Amaranthaceae": Icon.VEGETABLES,
    "Cannaceae": Icon.VEGETABLES,
    "Chenopodiaceae": Icon.VEGETABLES,
    # Herbs (culinary / aromatic)
    "Lamiaceae": Icon.HERBS,
    "Verbenaceae": Icon.HERBS,
    "Plantaginaceae": Icon.HERBS,
    "Alliaceae": Icon.HERBS,
    # Medicinal
    "Hypericaceae": Icon.MEDICINAL,
    "Gentianaceae": Icon.MEDICINAL,
    "Elaeagnaceae": Icon.MEDICINAL,
    # Trees / woody plants
    "Pinaceae": Icon.TREES,
    "Cupressaceae": Icon.TREES,
    "Platanaceae": Icon.TREES,
    "Ulmaceae": Icon.TREES,
    "Juglandaceae": Icon.TREES,
    "Cornaceae": Icon.TREES,
    "Sapindaceae": Icon.TREES,
    # Succulents / fleshy plants
    "Crassulaceae": Icon.SUCCULENTS,
    "Euphorbiaceae": Icon.SUCCULENTS,
    "Bromeliaceae": Icon.SUCCULENTS,
    # Ornamental
    "Geraniaceae": Icon.ORNAMENTAL,
    "Ericaceae": Icon.ORNAMENTAL,
    "Asteraceae": Icon.ORNAMENTAL,
    "Ranunculaceae": Icon.ORNAMENTAL,
    "Caryophyllaceae": Icon.ORNAMENTAL,
    "Campanulaceae": Icon.ORNAMENTAL,
    "Scrophulariaceae": Icon.ORNAMENTAL,
    "Violaceae": Icon.ORNAMENTAL,
    "Polemoniaceae": Icon.ORNAMENTAL,
    "Onagraceae": Icon.ORNAMENTAL,
    "Myrsinaceae": Icon.ORNAMENTAL,
    "Begoniaceae": Icon.ORNAMENTAL,
    "Hydrangea": Icon.ORNAMENTAL,
    "Balsaminaceae": Icon.ORNAMENTAL,
    "Calceolariaceae": Icon.ORNAMENTAL,
    "Boraginaceae": Icon.ORNAMENTAL,
    "Goodeniaceae": Icon.ORNAMENTAL,
    "Gesneriaceae": Icon.ORNAMENTAL,
    "Malvaceae": Icon.ORNAMENTAL,
    "Convolvulaceae": Icon.ORNAMENTAL,
    "Cannabaceae": Icon.ORNAMENTAL,
    "Polypodiaceae": Icon.ORNAMENTAL,
    "Agapanthaceae": Icon.ORNAMENTAL,
}

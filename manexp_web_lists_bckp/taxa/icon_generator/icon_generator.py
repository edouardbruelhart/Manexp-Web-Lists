from pathlib import Path

from manexp_web_lists.exceptions.families_exception import FamiliesException
from manexp_web_lists.taxa.taxon_models.taxa import Icon, IconedTaxa, IconedTaxon, TranslatedTaxa
from manexp_web_lists.taxa.utils.save_taxa import save_taxa


def icon_generator(input_taxa: TranslatedTaxa) -> IconedTaxa:
    """Add material icons from google to taxa depending on their family"""

    # List to hold iconed taxa
    taxon_list: list[IconedTaxon] = []

    # Get updated families list
    families = get_unique_families(input_taxa)

    # Check that current families to icon mapping is matching new dataset families
    if sorted(families) != sorted(FAMILY_TO_ICON):
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
    # Herbs (culinary / aromatic)
    "Lamiaceae": Icon.HERBS,
    "Verbenaceae": Icon.HERBS,
    "Plantaginaceae": Icon.HERBS,
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
    "Amaryllidaceae": Icon.SUCCULENTS,
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
    "Primulaceae": Icon.ORNAMENTAL,
    "Begoniaceae": Icon.ORNAMENTAL,
    "Caprifoliaceae": Icon.ORNAMENTAL,
    "Balsaminaceae": Icon.ORNAMENTAL,
    "Calceolariaceae": Icon.ORNAMENTAL,
    "Heliotropiaceae": Icon.ORNAMENTAL,
    "Goodeniaceae": Icon.ORNAMENTAL,
    "Gesneriaceae": Icon.ORNAMENTAL,
    "Hydrangeaceae": Icon.ORNAMENTAL,
    "Malvaceae": Icon.ORNAMENTAL,
    "Convolvulaceae": Icon.ORNAMENTAL,
    "Cannabaceae": Icon.ORNAMENTAL,
    "Polypodiaceae": Icon.ORNAMENTAL,
}

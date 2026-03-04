import logging
from pathlib import Path

from manexp_web_lists.taxa.color_generator.text_to_color import text_to_color
from manexp_web_lists.taxa.models.taxa import ColoredTaxa, ColoredTaxon, IconedTaxa
from manexp_web_lists.taxa.save_taxa import save_taxa

# Initialize logger
logger = logging.getLogger(__name__)


def color_generator(input_taxa: IconedTaxa) -> ColoredTaxa:
    """
    Add hexadecimal color code for each taxon

    Args:
        input_taxa: The iconed taxon list

    Returns:
        ColoredTaxa: The colored taxon list
    """

    # List to hold colored taxa
    taxon_list: list[ColoredTaxon] = []

    # Assign a color to each taxon
    for taxon in input_taxa.taxa:
        # Get focal name
        focal_name = taxon.taxonomy.cleaned_classification.focal_name

        # Get color from focal name
        color = text_to_color(focal_name)

        # Append colored taxon to list
        taxon_list.append(
            ColoredTaxon(
                crop_category=taxon.crop_category,
                taxonomy=taxon.taxonomy,
                crops=taxon.crops,
                translations=taxon.translations,
                icon=taxon.icon,
                color=color,
            )
        )

    # Create colored taxa
    colored_taxa = ColoredTaxa(taxa=taxon_list)

    # Save taxa to json file
    save_taxa(colored_taxa, Path("../lists/in/colored/colored_taxon_list.json"))

    logger.info(f"Done! added color to {len(colored_taxa.taxa)} taxa.")

    # Return colored taxa
    return colored_taxa

import colorsys
import hashlib
from pathlib import Path

from manexp_web_lists.taxa.taxon_models.taxa import ColoredTaxa, ColoredTaxon, IconedTaxa
from manexp_web_lists.taxa.utils.save_taxa import save_taxa


def color_generator(input_taxa: IconedTaxa) -> ColoredTaxa:
    """Add hexadecimal color code for each taxon"""

    # List to hold colored taxa
    taxon_list: list[ColoredTaxon] = []

    # Assign a color to each taxon
    for taxon in input_taxa.taxa:
        # Get focal name
        focal_name = taxon.taxonomy.resolved_classification.focal_name

        # Get color from focal name
        color = text_to_color(focal_name)

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

    # Return colored taxa
    return colored_taxa


def text_to_color(text: str) -> str:
    """Returns always the same hexadecimal color for a given text"""
    # Hash it
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Get hue from part of the hash
    hue = int(digest[:8], 16) % 360

    # Define saturation and lightness
    saturation = 0.60
    lightness = 0.50

    # Generate RGB
    r, g, b = colorsys.hls_to_rgb(hue / 360.0, lightness, saturation)

    hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    return hex_color

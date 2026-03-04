import logging
from pathlib import Path

from manexp_web_lists.taxa.models.taxa import CleanedTaxa, TranslatedTaxa, TranslatedTaxon
from manexp_web_lists.taxa.save_taxa import save_taxa
from manexp_web_lists.taxa.taxo_translator.translate_taxon import translate_taxon

# Initialize logger
logger = logging.getLogger(__name__)

TRANSLATED_PATH = Path("../lists/in/translated/translated_taxon_list.json")


def taxo_translator(input_taxa: CleanedTaxa) -> TranslatedTaxa:
    """
    Translate taxonomy in french, english, german and italian

    Args:
        input_taxa: Cleaned taxa without translation

    Returns:
        TranslatedTaxa: Translated taxa
    """

    # List to hold translated taxa
    taxon_list: list[TranslatedTaxon] = []

    # Translate each taxon
    for taxon in input_taxa.taxa:
        # Get translations
        translations = translate_taxon(taxon.taxonomy)

        # Ignore entries where translation fails
        if translations is None:
            continue

        # Add translated taxon to the list
        taxon_list.append(
            TranslatedTaxon(
                crop_category=taxon.crop_category,
                taxonomy=taxon.taxonomy,
                crops=taxon.crops,
                translations=translations,
            )
        )

    # Create translated taxa
    translated_taxa = TranslatedTaxa(taxa=taxon_list)

    # Save taxa to json file
    save_taxa(translated_taxa, TRANSLATED_PATH)

    logger.info(f"Done! translated {len(translated_taxa.taxa)} taxa.")

    # Return translated taxa
    return translated_taxa

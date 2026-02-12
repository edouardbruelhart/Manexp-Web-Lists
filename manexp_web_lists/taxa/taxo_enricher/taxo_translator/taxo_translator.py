import logging
from pathlib import Path
from typing import Optional, TypeGuard

from manexp_web_lists.taxa.models.taxa import (
    ResolvedTaxa,
    ResolvedTaxonomy,
    TranslatedTaxa,
    TranslatedTaxon,
    Translations,
)
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.gbif_translation import translate_with_gbif
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.google_translation import translate_with_google
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.models import CompleteTranslationReport, TranslationReport
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.wikidata_translation import translate_with_wikidata
from manexp_web_lists.taxa.utils.save_taxa import save_taxa

# Initialize logger
logger = logging.getLogger(__name__)


def taxo_translator(input_taxons: ResolvedTaxa) -> TranslatedTaxa:
    """
    Translate taxonomy in french, english, german and italian

    :param input_taxons: Resolved taxa without translation
    :type input_taxons: ResolvedTaxa
    :return: Translated taxa
    :rtype: TranslatedTaxa

    """

    # List to hold translated taxa
    taxon_list: list[TranslatedTaxon] = []

    # Translate each taxon
    for taxon in input_taxons.taxa:
        # Get translations
        translations = translate_taxo(taxon.taxonomy)

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
    save_taxa(translated_taxa, Path("../lists/in/translated/translated_taxon_list.json"))

    # Return translated taxa
    return translated_taxa


def translate_taxo(taxonomy: ResolvedTaxonomy) -> Optional[Translations]:
    """
    Get translations for a given taxonomy with source tracking.

    :param taxonomy: Resolved taxonomy from a resolved taxon
    :type taxonomy: ResolvedTaxonomy
    :return: Translations for the given taxonomy in french, english, german and italian
    :rtype: Translations | None

    """

    # Isolate frequently used variables
    focal_name = taxonomy.resolved_classification.focal_name
    rank = taxonomy.rank

    # Try first with wikidata (best results)
    wiki_report = translate_with_wikidata(taxonomy)

    # Directly return translations if complete
    if is_translation_complete(wiki_report):
        return get_valid_translation(wiki_report)

    # First fallback to GBIF
    gbif_report = translate_with_gbif(taxonomy, wiki_report)

    # Directly return translations if complete
    if is_translation_complete(gbif_report):
        return get_valid_translation(gbif_report)

    # If no translation found, it is useless to go to google fallback
    if gbif_report is None or (not gbif_report.fr and not gbif_report.en and not gbif_report.de and not gbif_report.it):
        logger.warning(f"Skipping {focal_name} with rank {rank.name} due to absence of translations")
        return None

    # Last fallback to Google
    google_report = translate_with_google(gbif_report)

    # Directly return translations if complete
    if is_translation_complete(google_report):
        return get_valid_translation(google_report)
    else:
        # Failed to translate, return none
        logger.warning(
            f"Skipping {focal_name} with rank {rank.name} due to missing tranlsations. Translation report: {google_report}"
        )
        return None


def is_translation_complete(
    translation_report: Optional[TranslationReport],
) -> TypeGuard[CompleteTranslationReport]:
    """
    Check if a translation report is complete.

    :param translation_report: Generated translation report to check
    :type translation_report: Optional[TranslationReport]
    :return: True if the translation report is complete, False otherwise and certifies that translation report is not None and empty
    :rtype: TypeGuard[CompleteTranslationReport]
    """
    return (
        translation_report is not None
        and translation_report.fr is not None
        and translation_report.en is not None
        and translation_report.de is not None
        and translation_report.it is not None
    )


def get_valid_translation(translation_report: CompleteTranslationReport) -> Translations:
    """
    Convert a translation report to a valid translations object.

    :param translation_report: Report obtained from translate_taxo function
    :type translation_report: CompleteTranslationReport
    :return: Valid translations object containing all the translations
    :rtype: Translations
    """
    return Translations(
        fr=translation_report.fr,
        en=translation_report.en,
        de=translation_report.de,
        it=translation_report.it,
    )

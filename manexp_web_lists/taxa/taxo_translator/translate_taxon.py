import logging
from typing import Optional, TypeGuard

from manexp_web_lists.taxa.models.taxa import CleanedTaxonomy
from manexp_web_lists.taxa.models.translations import Translations
from manexp_web_lists.taxa.taxo_translator.gbif_translation import gbif_translation
from manexp_web_lists.taxa.taxo_translator.google_translation import google_translation
from manexp_web_lists.taxa.taxo_translator.models import CompleteTranslationReport, TranslationReport
from manexp_web_lists.taxa.taxo_translator.wikidata_translation import wikidata_translation

# Initialize logger
logger = logging.getLogger(__name__)


def translate_taxon(taxonomy: CleanedTaxonomy) -> Translations | None:
    """
    Get translations for a given taxonomy with source tracking.

    Args:
        taxonomy: Cleaned taxonomy from a cleaned taxon

    Returns:
        Translations | None: The translations for the specific taxon
    """

    # Isolate frequently used variables
    focal_name = taxonomy.cleaned_classification.focal_name
    rank = taxonomy.rank

    # Try first with wikidata (best results)
    wiki_report = wikidata_translation(taxonomy)

    # Directly return translations if complete
    if is_translation_complete(wiki_report):
        return get_valid_translation(wiki_report)

    # First fallback to GBIF
    gbif_report = gbif_translation(taxonomy, wiki_report)

    # Directly return translations if complete
    if is_translation_complete(gbif_report):
        return get_valid_translation(gbif_report)

    # If no translation found, it is useless to go to google fallback
    if gbif_report is None or (not gbif_report.fr and not gbif_report.en and not gbif_report.de and not gbif_report.it):
        logger.warning(f"Skipping {focal_name} with rank {rank.name} due to absence of translations")
        return None

    # Last fallback to Google
    google_report = google_translation(gbif_report)

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

    Args:
        translation_report: The translation report to check.

    Returns:
        TypeGuard[CompleteTranslationReport]: True if the report is complete, False otherwise.
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

    Args:
        translation_report: The translation report to convert.

    Returns:
        Translations: The valid translations object.
    """

    return Translations(
        fr=translation_report.fr,
        en=translation_report.en,
        de=translation_report.de,
        it=translation_report.it,
    )

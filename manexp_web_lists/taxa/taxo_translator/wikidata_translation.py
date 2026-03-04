import requests

from manexp_web_lists.requests.wikidata_requests import wikidata_labels_request, wikidata_qid_request
from manexp_web_lists.taxa.models.taxa import CleanedTaxonomy
from manexp_web_lists.taxa.models.translations import Translation, TranslationSource
from manexp_web_lists.taxa.taxo_translator.models import TranslationReport

# Default resquest session that can be customized globally
session = requests.Session()

# Bot version transmitted to wikidata API
bot_version = 0.1


def wikidata_translation(taxonomy: CleanedTaxonomy) -> TranslationReport | None:
    """
    Get translations using WikiData API

    Args:
        taxonomy: Cleaned taxonomy from a cleaned taxon

    Returns:
        TranslationReport | None: The translation report for the specific taxon
    """

    # Isolate frequently used variables
    focal_name = taxonomy.cleaned_classification.focal_name

    # Get WikiData id
    qid = wikidata_qid_request(focal_name)

    # If no WikiData id
    if qid is None:
        return None

    # Extract labels
    labels = wikidata_labels_request(qid)

    if labels is None or not isinstance(labels, dict):
        return None

    # Get translations
    french = labels["fr"]["value"] if labels.get("fr") else None
    english = labels["en"]["value"] if labels.get("en") else None
    german = labels["de"]["value"] if labels.get("de") else None
    italian = labels["it"]["value"] if labels.get("it") else None

    # Create translations
    french_translation = (
        Translation(name=french, source=TranslationSource.WIKIDATA) if french and french != focal_name else None
    )
    english_translation = (
        Translation(name=english, source=TranslationSource.WIKIDATA) if english and english != focal_name else None
    )
    german_translation = (
        Translation(name=german, source=TranslationSource.WIKIDATA) if german and german != focal_name else None
    )
    italian_translation = (
        Translation(name=italian, source=TranslationSource.WIKIDATA) if italian and italian != focal_name else None
    )

    # Create translation report
    translation_report = TranslationReport(
        fr=french_translation, en=english_translation, de=german_translation, it=italian_translation
    )

    # Return translation report
    return translation_report

from typing import Optional

import requests
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.languages import LANGUAGES
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.models import TranslationReport
from manexp_web_lists.taxa.taxon_models.taxa import (
    ResolvedTaxonomy,
    Translation,
    TranslationSource,
)

# Default resquest session that can be customized globally
session = requests.Session()

# Bot version transmitted to wikidata API
bot_version = 0.1


def translate_with_wikidata(taxonomy: ResolvedTaxonomy) -> Optional[TranslationReport]:
    """Get translations using WikiData API"""

    # Isolate frequently used variables
    focal_name = taxonomy.resolved_classification.focal_name
    rank = taxonomy.rank

    # Request parameters
    url = "https://www.wikidata.org/w/api.php"
    headers = {"User-Agent": f"Manexp-Web-Lists Bot/{bot_version} (https://manexp.ch; edouard.brulhart@manexp.ch)"}
    params = {"action": "wbsearchentities", "search": focal_name, "language": "en", "format": "json", "type": "item"}

    # Request to get WikiData id
    response = session.get(url, params=params, headers=headers)
    response.raise_for_status()

    # Get data
    data = response.json()

    # If search is not successful, skip next steps and return null
    if not data["search"]:
        print(f"Failed to get WikiData QID for taxon '{focal_name}' with rank {rank.name}: {data}")
        return None

    # Get WikiData id
    qid = data["search"][0]["id"]

    # Parameters to get translations
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels",
        "languages": "|".join(LANGUAGES),
        "format": "json",
    }

    # Request to get translations
    response = session.get(url, params=params, headers=headers)
    response.raise_for_status()

    # Get data
    data = response.json()

    # Extract labels
    labels = data["entities"][qid]["labels"]

    # Get translations
    french = labels.get("fr")["value"] if labels.get("fr") else None
    english = labels.get("en")["value"] if labels.get("en") else None
    german = labels.get("de")["value"] if labels.get("de") else None
    italian = labels.get("it")["value"] if labels.get("it") else None

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

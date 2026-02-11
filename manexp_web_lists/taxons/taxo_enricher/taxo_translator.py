from pathlib import Path
from typing import Optional

import requests
from deep_translator import GoogleTranslator

from manexp_web_lists.exceptions.fetch_exception import FetchException
from manexp_web_lists.taxons.models.taxons import (
    ResolvedTaxons,
    TaxonRank,
    TranslatedTaxon,
    TranslatedTaxons,
    Translation,
    Translations,
    TranslationSource,
)
from manexp_web_lists.taxons.utils.save_taxons import save_taxons
from manexp_web_lists.utils.strict_model import StrictModel


class TranslationReport(StrictModel):
    fr: Optional[Translation]
    en: Optional[Translation]
    de: Optional[Translation]
    it: Optional[Translation]


languages = ["fr", "en", "de", "it"]

human_languages = {"fr": "French", "en": "English", "de": "German", "it": "Italian"}

gbif_languages = {"fr": "fra", "en": "eng", "de": "deu", "it": "ita"}

bot_version = 0.1

session = requests.Session()


def taxo_translator(input_taxons: ResolvedTaxons) -> TranslatedTaxons:
    """Translate taxonomy in french, english, german and italian"""
    taxon_list: list[TranslatedTaxon] = []

    for taxon in input_taxons.taxons:
        taxon_name = taxon.species if taxon.species else taxon.genus

        translations = translate_taxo(taxon_name, taxon.taxon_rank)

        # Ignore entries where translation fails
        if translations is None:
            continue

        print(f"Successfully translated {taxon_name} with rank {taxon.taxon_rank.name}")

        taxon_list.append(
            TranslatedTaxon(
                crop_category=taxon.crop_category,
                taxon_rank=taxon.taxon_rank,
                family=taxon.family,
                genus=taxon.genus,
                species=taxon.species,
                crops=taxon.crops,
                translations=translations,
            )
        )

    translate_taxons = TranslatedTaxons(taxons=taxon_list)

    save_taxons(translate_taxons, Path("../lists/in/translated/translated_taxon_list.json"))

    return translate_taxons


def translate_taxo(taxon: str, rank: TaxonRank) -> Optional[Translations]:
    """Get translations for a given taxonomy with source tracking."""
    try:
        translations = translate_with_wikidata(taxon, rank)

        if translations is None:
            print(f"No translations found for taxon '{taxon}' with rank {rank}")
            return None

        if translations.fr is None or translations.en is None or translations.de is None or translations.it is None:
            print(f"One or more translations are missing for taxon '{taxon}' with rank {rank}: {translations}")
            return None
        else:
            validated_translations = Translations(
                fr=translations.fr, en=translations.en, de=translations.de, it=translations.it
            )

            return validated_translations

    except requests.RequestException as e:
        raise FetchException(taxon, str(e)) from e


def translate_with_wikidata(taxon: str, rank: TaxonRank) -> Optional[TranslationReport]:
    url = "https://www.wikidata.org/w/api.php"
    header = {"User-Agent": f"Manexp-Web-Lists Bot/{bot_version} (https://manexp.ch; edouard.brulhart@manexp.ch)"}
    params = {"action": "wbsearchentities", "search": taxon, "language": "en", "format": "json", "type": "item"}

    response = session.get(url, params=params, headers=header)

    response.raise_for_status()

    data = response.json()

    if not data["search"]:
        print(f"Failed to get WikiData QID for taxon '{taxon}' with rank {rank.name}: {data}")
        return None

    qid = data["search"][0]["id"]

    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels",
        "languages": "|".join(languages),
        "format": "json",
    }

    response = session.get(url, params=params, headers=header)

    response.raise_for_status()

    data = response.json()

    labels = data["entities"][qid]["labels"]

    french = labels.get("fr")["value"] if labels.get("fr") else None
    english = labels.get("en")["value"] if labels.get("en") else None
    german = labels.get("de")["value"] if labels.get("de") else None
    italian = labels.get("it")["value"] if labels.get("it") else None

    french_translation = (
        Translation(name=french, source=TranslationSource.WIKIDATA) if french and french != taxon else None
    )

    english_translation = (
        Translation(name=english, source=TranslationSource.WIKIDATA) if english and english != taxon else None
    )

    german_translation = (
        Translation(name=german, source=TranslationSource.WIKIDATA) if german and german != taxon else None
    )

    italian_translation = (
        Translation(name=italian, source=TranslationSource.WIKIDATA) if italian and italian != taxon else None
    )

    translation_report = TranslationReport(
        fr=french_translation, en=english_translation, de=german_translation, it=italian_translation
    )

    if (
        french_translation is None
        or english_translation is None
        or german_translation is None
        or italian_translation is None
    ):
        fallback_translation_report = fallback_translation(taxon, rank, translation_report)
        return fallback_translation_report

    return translation_report


def fallback_translation(taxon: str, rank: TaxonRank, translation_report: TranslationReport) -> TranslationReport:
    # First fallback to GBIF
    gbif_translation_report = translate_with_gbif(taxon, rank, translation_report)

    if (
        gbif_translation_report.fr is not None
        and gbif_translation_report.en is not None
        and gbif_translation_report.de is not None
        and gbif_translation_report.it is not None
    ):
        return gbif_translation_report

    # Last fallback to google
    google_translation_report = translate_with_google(gbif_translation_report)

    return google_translation_report


def translate_with_gbif(taxon: str, rank: TaxonRank, translation_report: TranslationReport) -> TranslationReport:
    # Get taxon key
    url = f"https://api.gbif.org/v1/species/match?name={taxon}"
    params = {"q": taxon, "rank": rank.name}
    response = session.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if not data["results"]:
        print(f"No GBIF results found for taxon '{taxon}' with rank {rank.name}: {data}")
        return translation_report

    gbif_key = data["usageKey"]

    # Get GBIF vernaculars
    url = f"https://api.gbif.org/v1/species/{gbif_key}/vernacularNames"
    response = session.get(url)
    response.raise_for_status()
    data = response.json()
    vernaculars = list(data["results"])

    # If no vernaculars for this language
    if vernaculars is None or len(vernaculars) == 0:
        print(f"No GBIF vernaculars found for {taxon} with rank {rank.name}")
        return translation_report

    french_vernaculars = [v for v in vernaculars if v["language"] == "fra"]

    english_vernaculars = [v for v in vernaculars if v["language"] == "eng"]

    german_vernaculars = [v for v in vernaculars if v["language"] == "deu"]

    italian_vernaculars = [v for v in vernaculars if v["language"] == "ita"]

    french_translation = (
        Translation(name=french_vernaculars[0]["vernacularName"], source=TranslationSource.GBIF)
        if french_vernaculars and len(french_vernaculars) > 0
        else None
    )

    english_translation = (
        Translation(name=english_vernaculars[0]["vernacularName"], source=TranslationSource.GBIF)
        if english_vernaculars and len(english_vernaculars) > 0
        else None
    )

    german_translation = (
        Translation(name=german_vernaculars[0]["vernacularName"], source=TranslationSource.GBIF)
        if german_vernaculars and len(german_vernaculars) > 0
        else None
    )

    italian_translation = (
        Translation(name=italian_vernaculars[0]["vernacularName"], source=TranslationSource.GBIF)
        if italian_vernaculars and len(italian_vernaculars) > 0
        else None
    )

    gbif_translation_report = TranslationReport(
        fr=translation_report.fr if translation_report.fr else french_translation,
        en=translation_report.en if translation_report.en else english_translation,
        de=translation_report.de if translation_report.de else german_translation,
        it=translation_report.it if translation_report.it else italian_translation,
    )

    return gbif_translation_report


def translate_with_google(translation_report: TranslationReport) -> TranslationReport:
    base = (
        translation_report.en.name
        if translation_report.en
        else translation_report.fr.name
        if translation_report.fr
        else translation_report.de.name
        if translation_report.de
        else translation_report.it.name
        if translation_report.it
        else None
    )

    src = (
        "en"
        if translation_report.en
        else "fr"
        if translation_report.fr
        else "de"
        if translation_report.de
        else "it"
        if translation_report.it
        else None
    )

    # Nothing to translate
    if base is None or src is None:
        return translation_report

    def gt(dest: str) -> str:
        return GoogleTranslator(source=src, target=dest).translate(base)

    return TranslationReport(
        fr=translation_report.fr or Translation(name=gt("fr"), source=TranslationSource.GOOGLE),
        en=translation_report.en or Translation(name=gt("en"), source=TranslationSource.GOOGLE),
        de=translation_report.de or Translation(name=gt("de"), source=TranslationSource.GOOGLE),
        it=translation_report.it or Translation(name=gt("it"), source=TranslationSource.GOOGLE),
    )

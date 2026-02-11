from typing import Optional

import requests

from manexp_web_lists.taxa.models.taxa import (
    ResolvedTaxonomy,
    TaxonRank,
    Translation,
    TranslationSource,
)
from manexp_web_lists.taxa.taxo_enricher.taxo_translator.models import TranslationReport

# Default resquest session that can be customized globally
session = requests.Session()


def translate_with_gbif(
    taxonomy: ResolvedTaxonomy, translation_report: Optional[TranslationReport]
) -> Optional[TranslationReport]:

    # Isolate frequently used variables
    focal_name = taxonomy.resolved_classification.focal_name
    rank = taxonomy.rank

    # Request parameters to get GBIF key
    url = f"https://api.gbif.org/v1/species/match?name={focal_name}"
    params = {"q": focal_name, "rank": rank.name}

    # Request to get GBIF key
    response = session.get(url, params=params)
    response.raise_for_status()

    # Get data
    data = response.json()

    # Get GBIF key
    gbif_key = (
        get_gbif_key_from_multiple_matches(taxonomy)
        if data.get("matchType") == "NONE" and "Multiple equal matches" in data.get("note", "")
        else data["usageKey"]
    )

    # If we can't retrieve GBIF key, just return the translation report
    if gbif_key is None:
        print(f"Failed to get GBIF key for taxon '{focal_name}' with rank {rank.name}: {data}")
        return translation_report

    # Request url to get translations
    url = f"https://api.gbif.org/v1/species/{gbif_key}/vernacularNames"

    # Request to get vernaculars
    response = session.get(url)
    response.raise_for_status()

    # Get data
    data = response.json()

    # Convert results to list
    vernaculars = list(data["results"])

    # If no vernaculars for this language
    if vernaculars is None or len(vernaculars) == 0:
        return translation_report

    # Get vernaculars for each language
    french_vernaculars = [v for v in vernaculars if v["language"] == "fra"]

    english_vernaculars = [v for v in vernaculars if v["language"] == "eng"]

    german_vernaculars = [v for v in vernaculars if v["language"] == "deu"]

    italian_vernaculars = [v for v in vernaculars if v["language"] == "ita"]

    # Construct translations
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

    # If passed translation report is null, create one
    if translation_report is None:
        new_translation_report = TranslationReport(
            fr=french_translation, en=english_translation, de=german_translation, it=italian_translation
        )
    # Else update it
    else:
        new_translation_report = TranslationReport(
            fr=translation_report.fr if translation_report.fr else french_translation,
            en=translation_report.en if translation_report.en else english_translation,
            de=translation_report.de if translation_report.de else german_translation,
            it=translation_report.it if translation_report.it else italian_translation,
        )

    # Return the report
    return new_translation_report


def get_gbif_key_from_multiple_matches(taxonomy: ResolvedTaxonomy) -> Optional[str]:

    # Isolate frequently used variables
    focal_name = taxonomy.resolved_classification.focal_name
    rank = taxonomy.rank
    family = taxonomy.resolved_classification.family
    genus = taxonomy.resolved_classification.genus
    species = taxonomy.resolved_classification.species

    if focal_name is None:
        return None

    # Get key
    key = gbif_search_request(focal_name, rank, family, genus, species)

    return key


def gbif_search_request(
    focal_name: str, rank: TaxonRank, family: str, genus: str, species: Optional[str]
) -> Optional[str]:
    # Request parameters
    url = "https://api.gbif.org/v1/species/search"
    params = {"q": focal_name, "rank": rank.name}

    # Request
    response = session.get(url, params=params)
    response.raise_for_status()

    # Get data
    data = response.json()

    # Filter candidates
    candidates = [
        r
        for r in data["results"]
        if is_valid_candidate(
            r,
            rank=rank,
            family=family,
            genus=genus,
            species=species,
        )
    ]

    # If no candidate return none
    if candidates is None or len(candidates) == 0:
        return None

    # We have a match!
    if len(candidates) > 0:
        return str(candidates[0]["nubKey"])
    else:
        return None


def is_valid_candidate(
    r: dict,
    *,
    rank: TaxonRank,
    family: str,
    genus: str,
    species: str | None = None,
) -> bool:
    if (
        r.get("rank") != rank.name
        or r.get("taxonomicStatus") != "ACCEPTED"
        or r.get("kingdom") != "Plantae"
        or r.get("family") != family
        or r.get("genus") != genus
        or r.get("nubKey") is None
    ):
        return False

    if rank == TaxonRank.SPECIES:
        return r.get("species") == species

    return True

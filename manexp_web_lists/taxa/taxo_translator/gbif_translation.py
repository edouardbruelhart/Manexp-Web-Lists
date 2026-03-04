from manexp_web_lists.requests.gbif_requests import (
    MatchStatus,
    gbif_match_request,
    gbif_search_request,
    gbif_vernaculars_request,
)
from manexp_web_lists.taxa.models.taxa import CleanedTaxonomy
from manexp_web_lists.taxa.models.taxonomy import TaxonRank
from manexp_web_lists.taxa.models.translations import Translation, TranslationSource
from manexp_web_lists.taxa.taxo_translator.models import TranslationReport


def gbif_translation(
    taxonomy: CleanedTaxonomy, translation_report: TranslationReport | None
) -> TranslationReport | None:
    """
    Get translations using GBIF API

    Args:
        taxonomy: cleaned taxonomy from a cleaned taxon
        translation_report: The translation report to update

    Returns:
        TranslationReport | None: The translation report for the specific taxon
    """

    # Get GBIF key
    gbif_key = get_gbif_key(taxonomy)

    # If no GBIF key for this taxon
    if gbif_key is None:
        return translation_report

    # Get vernaculars
    vernaculars = gbif_vernaculars_request(gbif_key)

    # If no vernaculars for this taxon
    if vernaculars is None or len(vernaculars) == 0:
        return translation_report

    # Get translations from vernaculars
    new_translation_report = translation_report_from_vernaculars(vernaculars, translation_report)

    # Return translation report
    return new_translation_report


def get_gbif_key(taxonomy: CleanedTaxonomy) -> str | None:
    """
    Get GBIF key for a given taxonomy

    Args:
        taxonomy: Cleaned taxonomy from a cleaned taxon

    Returns:
        str | None: The GBIF key for the specific taxon
    """

    # First try with match request as it gives cleaner results
    match_response = gbif_match_request(taxonomy.cleaned_classification.focal_name, taxonomy.rank)

    if match_response.status is MatchStatus.OK and match_response.data is not None:
        usage: dict | None = match_response.data.get("usage")

        if usage is None:
            return None

        match_key = usage.get("key")

        return match_key

    elif match_response.status is MatchStatus.MULTIPLE:
        # Fallback to search request if match request failed
        search_response = gbif_search_request(taxonomy.cleaned_classification.focal_name, taxonomy.rank)

        if search_response is None or len(search_response) == 0:
            return None

        # Filter candidates
        candidates = [
            r
            for r in search_response
            if is_valid_candidate(
                r,
                rank=taxonomy.rank,
                family=taxonomy.cleaned_classification.family,
                genus=taxonomy.cleaned_classification.genus,
                species=taxonomy.cleaned_classification.species,
            )
        ]

        # If no candidate return none
        if candidates is None or len(candidates) == 0:
            return None

        # We have a match!
        return str(candidates[0]["nubKey"])

    else:
        return None


def translation_report_from_vernaculars(
    vernaculars: list[dict], translation_report: TranslationReport | None
) -> TranslationReport:
    """
    Convert raw vernaculars to translation report

    Args:
        vernaculars: List of vernaculars
        translation_report: The translation report to update

    Returns:
        TranslationReport: The translation report for the specific taxon
    """

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

    return new_translation_report


def is_valid_candidate(
    r: dict,
    *,
    rank: TaxonRank,
    family: str,
    genus: str,
    species: str | None = None,
) -> bool:
    """
    Check if a candidate from GBIF search is corresponding to the taxon.

    Args:
        r: The candidate to check
        rank: The rank of the taxon
        family: The family of the taxon
        genus: The genus of the taxon
        species: The species of the taxon

    Returns:
        bool: True if the candidate is valid, False otherwise
    """

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

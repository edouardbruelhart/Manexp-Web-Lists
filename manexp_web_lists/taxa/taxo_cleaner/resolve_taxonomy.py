from manexp_web_lists.requests.gbif_requests import MatchStatus, gbif_match_request
from manexp_web_lists.taxa.models.taxonomy import TaxonRank


def resolve_taxonomy(name: str, source_rank: TaxonRank, target_rank: TaxonRank) -> str | None:
    """
    Get target rank from source rank

    Args:
        name: The known identification
        source_rank: The known rank
        target_rank: The target rank

    Returns:
        str | None: The family of the taxon
    """

    response = gbif_match_request(name, source_rank)

    if response.status is MatchStatus.NONE or response.status is MatchStatus.MULTIPLE or response.data is None:
        return None

    classification = response.data.get("classification")

    if classification is None:
        return None

    target = next((item["name"] for item in classification if item["rank"] == target_rank.name.upper()), None)

    return target

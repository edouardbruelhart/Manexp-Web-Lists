import logging
from enum import Enum
from typing import Optional

import requests

from manexp_web_lists.core.strict_model import StrictModel
from manexp_web_lists.taxa.models.taxonomy import TaxonRank

# Initialize logger
logger = logging.getLogger(__name__)

GBIF_URL = "https://api.gbif.org"
PARSER_URL = f"{GBIF_URL}/v1/parser/name"
MATCH_URL = f"{GBIF_URL}/v2/species/match"
SEARCH_URL = f"{GBIF_URL}/v1/species/search"
VERNACULARS_URL = GBIF_URL + "/v1/species/{key}/vernacularNames"


class MatchStatus(str, Enum):
    """Represent the GBIF match status"""

    OK = "ok"
    MULTIPLE = "multiple"
    NONE = "none"


class GBIFMatchResult(StrictModel):
    """Represent the GBIF match result model"""

    status: MatchStatus
    data: Optional[dict] = None


def gbif_parser_request(name: str) -> dict | None:
    """
    Make a parser request to GBIF API

    Args:
        name: The name of the taxon to parse

    Returns:
        dict | None: The GBIF parser response for the specific taxon
    """

    # Request parameters
    params = {"name": name}

    # Request
    with requests.Session() as session:
        response = session.get(PARSER_URL, params=params)
    response.raise_for_status()

    # Get data
    data: dict = response.json()[0]

    # If parsing failed
    if not data.get("parsed"):
        logger.warning(f"Failed to parse {name}: {data}")
        return None

    return data


def gbif_match_request(focal_name: str, rank: TaxonRank) -> GBIFMatchResult:
    """
    Make a match request to GBIF API

    Args:
        focal_name: The name of the taxon
        rank: The rank of the taxon

    Returns:
        GBIFMatchResult: The GBIF match result for the specific taxon
    """

    # Request parameters to get GBIF key
    params = {"genericName": focal_name, "rank": rank.name}

    # Request to get GBIF key
    with requests.Session() as session:
        response = session.get(MATCH_URL, params=params)
    response.raise_for_status()

    # Get data
    data = response.json()

    # If no match found
    if data["diagnostics"]["matchType"] == "NONE":
        try:
            if data["diagnostics"]["note"].__contains__("Multiple"):
                logger.warning(f"Multiple matches found for {focal_name} with rank {rank.name}: {data}")

                return GBIFMatchResult(status=MatchStatus.MULTIPLE)

            else:
                logger.warning(f"No match found for {focal_name} with rank {rank.name}: {data}")

                return GBIFMatchResult(status=MatchStatus.NONE)
        except KeyError:
            logger.warning(f"No match found for {focal_name} with rank {rank.name}: {data}")

            return GBIFMatchResult(status=MatchStatus.NONE)

    return GBIFMatchResult(status=MatchStatus.OK, data=data)


def gbif_search_request(focal_name: str, rank: TaxonRank) -> list[dict] | None:
    """
    Make a search request to GBIF API

    Args:
        focal_name: The name of the taxon
        rank: The rank of the taxon

    Returns:
        list[dict] | None: The GBIF key for the specific taxon
    """

    # Request parameters
    params = {"q": focal_name, "rank": rank.name}

    # Request
    with requests.Session() as session:
        response = session.get(SEARCH_URL, params=params)
    response.raise_for_status()

    # Get data
    data: dict = response.json()

    if data["count"] == 0:
        logger.warning(f"No search results found for {focal_name} with rank {rank.name}: {data}")
        return None

    results: list[dict] = data["results"]

    return results


def gbif_vernaculars_request(gbif_key: str) -> list[dict] | None:
    """
    Make a vernaculars request to GBIF API

    Args:
        gbif_key: The GBIF key of the taxon

    Returns:
        list[dict] | None: The GBIF vernaculars for the specific taxon
    """
    # Request url to get translations
    url = VERNACULARS_URL.format(key=gbif_key)

    # Request
    with requests.Session() as session:
        response = session.get(url)
    response.raise_for_status()

    # Get data
    data: dict = response.json()

    if data["results"] == []:
        logger.warning(f"No vernacular names found for {gbif_key}: {data}")
        return None

    results: list[dict] = data["results"]

    return results

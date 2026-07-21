import logging
from typing import Optional

import requests

from manexp_web_lists.core import StrictModel
from manexp_web_lists.taxonomy.models import TaxonRank

# Initialize logger
logger = logging.getLogger(__name__)

GBIF_URL = "https://api.gbif.org"
PARSER_URL = f"{GBIF_URL}/v1/parser/name"
MATCH_URL = f"{GBIF_URL}/v2/species/match"
SEARCH_URL = f"{GBIF_URL}/v1/species/search"
VERNACULARS_URL = GBIF_URL + "/v1/species/{key}/vernacularNames"


class GBIFParserResponse(StrictModel):
    """Represent the GBIF parser response model"""

    focal_name: str | None
    genus: Optional[str]
    rank: TaxonRank
    parsed: bool


def gbif_parser_request(name: str | None) -> dict:
    """
    Make a parser request to GBIF API

    Args:
        name: The name of the taxon to parse

    Returns:
        dict: The GBIF parser response for the specific taxon
    """

    if not name:
        logger.warning("No name provided for GBIF parser request.")
        return GBIFParserResponse(focal_name=None, genus=None, rank=TaxonRank.UNKNOWN, parsed=False).model_dump()

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
        return GBIFParserResponse(focal_name=name, genus=None, rank=TaxonRank.UNKNOWN, parsed=False).model_dump()

    # If parsing partially failed
    if data.get("parsedPartially"):
        logger.warning(f"Partially parsed {name}: {data}")
        return GBIFParserResponse(
            focal_name=name,
            genus=data.get("genusOrAbove"),
            rank=TaxonRank(data.get("rankMarker") or "unknown"),
            parsed=False,
        ).model_dump()

    return GBIFParserResponse(
        focal_name=data.get("canonicalName"),
        genus=data.get("genusOrAbove"),
        rank=TaxonRank(data.get("rankMarker") or "gen."),
        parsed=True,
    ).model_dump()

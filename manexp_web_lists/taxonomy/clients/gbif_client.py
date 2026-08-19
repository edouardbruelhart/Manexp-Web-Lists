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

    focal_name: Optional[str]
    genus: Optional[str]
    rank: TaxonRank
    parsed: bool


def gbif_parser_request(name: str) -> dict:
    """
    Make a parser request to GBIF API

    Args:
        name: The name(s) of the taxon to parse

    Returns:
        dict: The GBIF parser response for the specific taxon
    """

    # Handle empty name
    if not name:
        logger.warning("No name provided for GBIF parser request")
        return GBIFParserResponse(
            focal_name=name,
            genus=None,
            rank=TaxonRank.UNKNOWN,
            parsed=False,
        ).model_dump()

    # Split and clean synonyms
    synonyms = [part.strip() for part in name.splitlines() if part.strip()]

    # Holder for partial response in case we don't have a complete parsing
    partial_response: GBIFParserResponse | None = None

    with requests.Session() as session:
        for synonym in synonyms:
            # Request parameters
            params = {"name": synonym}

            # Request
            response = session.get(PARSER_URL, params=params)
            response.raise_for_status()

            # Get data
            data = response.json()

            # Skip empty response
            if not data:
                continue

            parsed_data: dict = data[0]

            # If parsing worked, directly return first information met
            if parsed_data.get("parsed") and not parsed_data.get("parsedPartially"):
                return GBIFParserResponse(
                    focal_name=parsed_data.get("canonicalName"),
                    genus=parsed_data.get("genusOrAbove"),
                    rank=TaxonRank(parsed_data.get("rankMarker") or "gen."),
                    parsed=True,
                ).model_dump()

            # If parsing partially failed, store the result in case this is the best match
            if parsed_data.get("parsedPartially") and partial_response is None:
                partial_response = GBIFParserResponse(
                    focal_name=name,
                    genus=parsed_data.get("genusOrAbove"),
                    rank=TaxonRank(parsed_data.get("rankMarker") or "unknown"),
                    parsed=False,
                )

    # Return first partial response as we didn't have a complete result
    if partial_response is not None:
        logger.warning("Partially parsed GBIF name: %s", name)
        return partial_response.model_dump()

    logger.warning("Failed to parse GBIF name: %s", name)
    return GBIFParserResponse(
        focal_name=synonyms[0],
        genus=None,
        rank=TaxonRank.UNKNOWN,
        parsed=False,
    ).model_dump()

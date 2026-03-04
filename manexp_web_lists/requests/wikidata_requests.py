import logging

import requests

from manexp_web_lists.taxa.taxo_translator.models import LANGUAGES

# Initialize logger
logger = logging.getLogger(__name__)

WIKIDATA_URL = "https://www.wikidata.org/w/api.php"
BOT_VERSION = 0.1
HEADERS = {"User-Agent": f"Manexp-Web-Lists Bot/{BOT_VERSION} (https://manexp.ch; edouard.brulhart@manexp.ch)"}


def wikidata_qid_request(name: str) -> str | None:
    """
    Make a QID request to WikiData API

    Args:
        name: The name of the taxon to retrieve QID for

    Returns:
        str | None: The WikiData QID for the specific taxon
    """

    # Request parameters
    params = {"action": "wbsearchentities", "search": name, "language": "en", "format": "json", "type": "item"}

    # Request
    with requests.Session() as session:
        response = session.get(WIKIDATA_URL, params=params, headers=HEADERS)
    response.raise_for_status()

    # Get data
    data = response.json()

    try:
        # Get WikiData id
        qid = data["search"][0]["id"]

        return str(qid)
    except (KeyError, IndexError):
        logger.warning(f"Failed to get WikiData QID for taxon {name}: {data}")
        return None


def wikidata_labels_request(qid: str) -> dict | None:
    """
    Make an labels request to WikiData API

    Args:
        qid: The QID of element we want labels for

    Returns:
        dict | None: The labels
    """

    # Request parameters
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels",
        "languages": "|".join(LANGUAGES),
        "format": "json",
    }

    # Request
    with requests.Session() as session:
        response = session.get(WIKIDATA_URL, params=params, headers=HEADERS)
    response.raise_for_status()

    # Get data
    data: dict = response.json()

    if data is None:
        logger.warning(f"Failed to get WikiData labels for QID {qid}")
        return None

    try:
        labels: dict = data["entities"][qid]["labels"]
    except KeyError:
        logger.warning(f"Failed to get WikiData labels for QID {qid}: {data}")
        return None
    else:
        return labels

import logging
from typing import Callable

from manexp_web_lists.logging_config import configure_logging, log_section
from manexp_web_lists.pesticides.fetch_pesticides import fetch_pesticides
from manexp_web_lists.taxa.fetch_taxa import fetch_taxa
from manexp_web_lists.utils.mailer import Mailer

# Initialize mailer
mailer = Mailer()

# Initialize logger
logger = logging.getLogger(__name__)


def main(taxa: Callable = fetch_taxa, pesticides: Callable = fetch_pesticides) -> None:
    """
    Main function to fetch and clean the different lists

    :param taxa: The function to fetch the taxa
    :type taxa: Callable
    :param pesticides: The function to fetch the pesticides
    :type pesticides: Callable
    """
    # Configure logging
    log_stream = configure_logging()

    try:
        # Generate taxon list
        log_section("FETCHING TAXA")
        taxa()

        # Generate pesticides list
        log_section("FETCHING PESTICIDES")
        pesticides()

        # Send success recap
        mailer.send_email(
            subject="Manexp-Web-List SUCCESS Report",
            body=log_stream.getvalue(),
        )

    except Exception:
        logger.exception("Error while generating lists")
        mailer.send_email(
            subject="Manexp-Web-List EXCEPTION Report",
            body=log_stream.getvalue(),
        )


if __name__ == "__main__":
    main()

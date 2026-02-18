import logging

from manexp_web_lists.core.logging_config import configure_logging, log_section
from manexp_web_lists.core.mailer import Mailer
from manexp_web_lists.taxa.fetch_taxa import fetch_taxa

# Initialize mailer
mailer = Mailer()

# Initialize logger
logger = logging.getLogger(__name__)


def run() -> None:
    """
    The main function to fetch all the lists
    """

    # Configure logging
    log_stream = configure_logging()

    try:
        # Generate taxon list
        log_section("FETCHING TAXA")
        fetch_taxa()

        # Generate pesticides list
        log_section("FETCHING PESTICIDES")
        # fetch_pesticides()

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
    run()
